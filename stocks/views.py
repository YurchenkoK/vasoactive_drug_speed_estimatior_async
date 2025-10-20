from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import Http404
from django.db import connection

from stocks.serializers import (
    DrugSerializer, FullDrugSerializer, OrderSerializer, 
    FullOrderSerializer, UserSerializer, UserRegistrationSerializer
)
from stocks.models import Drug, Order, DrugInOrder
from stocks.minio_utils import add_pic, delete_pic


def get_user():
    try:
        user = User.objects.get(id=1)
    except User.DoesNotExist:
        user = User.objects.create_user(
            id=1,
            username="admin",
            first_name="Admin",
            last_name="Admin",
            password="admin",
            email="admin@example.com"
        )
    return user


class DrugList(APIView):
    def get(self, request, format=None):
        drugs = Drug.objects.filter(is_active=True)
        name = request.query_params.get('name', None)
        if name:
            drugs = drugs.filter(name__icontains=name)
        serializer = DrugSerializer(drugs, many=True)
        return Response(serializer.data)
    
    def post(self, request, format=None):
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            drug = serializer.save()
            pic = request.FILES.get("pic")
            if pic:
                pic_result = add_pic(drug, pic)
                if hasattr(pic_result, 'data') and 'error' in pic_result.data:
                    return pic_result
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DrugDetail(APIView):
    def get(self, request, pk, format=None):
        drug = get_object_or_404(Drug, pk=pk, is_active=True)
        serializer = FullDrugSerializer(drug)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        drug = get_object_or_404(Drug, pk=pk)
        serializer = DrugSerializer(drug, data=request.data, partial=True)
        if 'pic' in request.FILES:
            pic_result = add_pic(drug, request.FILES['pic'])
            if hasattr(pic_result, 'data') and 'error' in pic_result.data:
                return pic_result
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        drug = get_object_or_404(Drug, pk=pk)
        drug.is_active = False
        drug.save()
        delete_pic(drug)
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def add_drug_image(request, pk):
    drug = get_object_or_404(Drug, pk=pk)
    pic = request.FILES.get("pic")
    if not pic:
        return Response({"error": "Файл изображения не предоставлен"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    pic_result = add_pic(drug, pic)
    if hasattr(pic_result, 'data') and 'error' in pic_result.data:
        return pic_result
    serializer = DrugSerializer(drug)
    return Response(serializer.data)


@api_view(['POST'])
def add_drug_to_order(request, pk):
    drug = get_object_or_404(Drug, pk=pk, is_active=True)
    user = get_user()
    order, created = Order.objects.get_or_create(
        creator=user,
        status=Order.OrderStatus.DRAFT,
        defaults={'creation_datetime': timezone.now()}
    )
    drug_in_order, created = DrugInOrder.objects.get_or_create(order=order, drug=drug)
    if not created:
        return Response({"message": "Препарат уже есть в заявке"}, status=status.HTTP_200_OK)
    return Response({"message": "Препарат добавлен в заявку", "order_id": order.id}, 
                   status=status.HTTP_201_CREATED)


@api_view(['GET'])
def cart_icon(request):
    user = get_user()
    try:
        order = Order.objects.get(creator=user, status=Order.OrderStatus.DRAFT)
        count = DrugInOrder.objects.filter(order=order).count()
        return Response({"order_id": order.id, "count": count})
    except Order.DoesNotExist:
        return Response({"order_id": None, "count": 0})


class OrderList(APIView):
    def get(self, request, format=None):
        user = get_user()
        orders = Order.objects.filter(creator=user).exclude(
            status__in=[Order.OrderStatus.DELETED, Order.OrderStatus.DRAFT]
        )
        
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        if date_from:
            orders = orders.filter(creation_datetime__gte=date_from)
        if date_to:
            orders = orders.filter(creation_datetime__lte=date_to)
        
        orders = orders.order_by('status', '-creation_datetime')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetail(APIView):
    def get(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        if order.status == Order.OrderStatus.DELETED:
            return Response({"error": "Заявка удалена"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FullOrderSerializer(order)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        order.status = Order.OrderStatus.DELETED
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT'])
def form_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status != Order.OrderStatus.DRAFT:
        return Response({"error": "Можно формировать только черновик"}, 
                       status=status.HTTP_403_FORBIDDEN)
    if not order.ampoules_count or not order.solvent_volume or not order.patient_weight:
        return Response({"error": "Заполните все обязательные поля"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    if not DrugInOrder.objects.filter(order=order).exists():
        return Response({"error": "В заявке должен быть хотя бы один препарат"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    order.status = Order.OrderStatus.FORMED
    order.formation_datetime = timezone.now()
    order.save()
    serializer = FullOrderSerializer(order)
    return Response(serializer.data)


@api_view(['PUT'])
def complete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    user = get_user()
    if order.status != Order.OrderStatus.FORMED:
        return Response({"error": "Можно завершать только сформированную заявку"}, 
                       status=status.HTTP_403_FORBIDDEN)
    order.status = Order.OrderStatus.COMPLETED
    order.completion_datetime = timezone.now()
    order.moderator = user
    order.save()
    for drug_in_order in DrugInOrder.objects.filter(order=order):
        drug_in_order.calculate_infusion_speed()
        drug_in_order.save()
    serializer = FullOrderSerializer(order)
    return Response(serializer.data)


@api_view(['PUT'])
def reject_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    user = get_user()
    if order.status != Order.OrderStatus.FORMED:
        return Response({"error": "Можно отклонять только сформированную заявку"}, 
                       status=status.HTTP_403_FORBIDDEN)
    order.status = Order.OrderStatus.REJECTED
    order.completion_datetime = timezone.now()
    order.moderator = user
    order.save()
    serializer = FullOrderSerializer(order)
    return Response(serializer.data)


@api_view(['DELETE', 'PUT'])
def drug_in_order_actions(request, order_pk, drug_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if order.status != Order.OrderStatus.DRAFT:
        return Response({"error": "Можно изменять препараты только в черновике"}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    drug_in_order = get_object_or_404(DrugInOrder, order=order, drug_id=drug_pk)
    
    if request.method == 'DELETE':
        drug_in_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        drug_rate = request.data.get('drug_rate')
        if drug_rate is not None:
            drug_in_order.drug_rate = drug_rate
            drug_in_order.save()
        return Response({"message": "Обновлено успешно"})


class UserRegistration(APIView):
    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                "id": user.id,
                "username": user.username,
                "message": "Пользователь успешно зарегистрирован"
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfile(APIView):
    def get(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request, pk, format=None):
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Укажите username и password"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    from django.contrib.auth import authenticate
    user = authenticate(username=username, password=password)
    
    if user is not None:
        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "message": "Успешная аутентификация"
        })
    else:
        return Response({"error": "Неверные учетные данные"}, 
                       status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
def user_logout(request):
    return Response({"message": "Деавторизация выполнена"})


def search(request):
    search_query = request.GET.get('search', '')
    drugs = Drug.objects.filter(is_active=True)
    if search_query:
        drugs = drugs.filter(name__icontains=search_query)
    
    drugs_data = []
    for drug in drugs:
        drugs_data.append({
            'id': drug.id,
            'name': drug.name,
            'description': drug.description,
            'image': drug.image_url or 'http://localhost:9000/images/default.png',
            'concentration': f'{drug.concentration} мг/мл',
            'volume': f'{drug.volume} мл',
        })
    
    estimation_count = 0
    order_id = None
    try:
        user = User.objects.first()
        if user:
            draft_order = Order.objects.filter(creator=user, status=Order.OrderStatus.DRAFT).first()
            if draft_order:
                estimation_count = DrugInOrder.objects.filter(order=draft_order).count()
                order_id = draft_order.id
    except:
        pass
    
    data = {'drugs': drugs_data, 'estimation_count': estimation_count, 'order_id': order_id}
    return render(request, 'main.html', {'data': data, 'search_query': search_query})


def vasoactive_drug_detail(request, drug_id):
    drug = get_object_or_404(Drug, id=drug_id, is_active=True)
    
    drug_data = {
        'id': drug.id,
        'name': drug.name,
        'description': drug.description,
        'image': drug.image_url or 'http://localhost:9000/images/default.png',
        'concentration': f'{drug.concentration} мг/мл',
        'volume': f'{drug.volume} мл',
    }
    
    estimation_count = 0
    order_id = None
    try:
        user = User.objects.first()
        if user:
            draft_order = Order.objects.filter(creator=user, status=Order.OrderStatus.DRAFT).first()
            if draft_order:
                estimation_count = DrugInOrder.objects.filter(order=draft_order).count()
                order_id = draft_order.id
    except:
        pass
    
    return render(request, 'vasoactive_drug.html', {'drug': drug_data, 'estimation_count': estimation_count, 'order_id': order_id})


def add_to_order_html(request, drug_id):
    if request.method != 'POST':
        return redirect('search')
    
    drug = get_object_or_404(Drug, id=drug_id, is_active=True)
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='testuser', password='testpass')
    
    draft_order, created = Order.objects.get_or_create(
        creator=user,
        status=Order.OrderStatus.DRAFT
    )
    
    drug_in_order, created = DrugInOrder.objects.get_or_create(
        order=draft_order,
        drug=drug
    )
    
    return redirect('vasoactive_drug_detail', drug_id=drug_id)


def estimation_infusion_speed(request, order_id=None):
    user = User.objects.first()
    if not user:
        data = {'estimation_items': [], 'estimation_params': {'ampoules': 0, 'solvent_volume': 0, 'patient_weight': 0}}
        return render(request, 'estimation_infusion_speed.html', {'data': data})
    
    if order_id:
        order = get_object_or_404(Order, id=order_id, creator=user)
        if order.status == Order.OrderStatus.DELETED:
            raise Http404("Заявка удалена")
        draft_order = order
    else:
        draft_order = Order.objects.filter(
            creator=user, 
            status__in=[Order.OrderStatus.DRAFT, Order.OrderStatus.FORMED]
        ).first()
    
    if not draft_order:
        data = {'estimation_items': [], 'estimation_params': {'ampoules': 0, 'solvent_volume': 0, 'patient_weight': 0}}
        return render(request, 'estimation_infusion_speed.html', {'data': data})
    
    drugs_in_order = DrugInOrder.objects.filter(order=draft_order).select_related('drug')
    estimation_items = []
    for drug_in_order in drugs_in_order:
        estimation_items.append({
            'id': drug_in_order.drug.id,
            'name': drug_in_order.drug.name,
            'concentration': f'{drug_in_order.drug.concentration} мг/мл',
            'volume': f'{drug_in_order.drug.volume} мл',
            'image': drug_in_order.drug.image_url or 'http://localhost:9000/images/default.png',
            'infusion_speed': f'{drug_in_order.infusion_speed}' if drug_in_order.infusion_speed else '',
            'drug_rate': f'{drug_in_order.drug_rate}' if drug_in_order.drug_rate else '',
        })
    
    estimation_params = {
        'ampoules': draft_order.ampoules_count if draft_order.ampoules_count else '',
        'solvent_volume': str(draft_order.solvent_volume).replace(',', '.') if draft_order.solvent_volume else '',
        'patient_weight': str(draft_order.patient_weight).replace(',', '.') if draft_order.patient_weight else '',
    }
    
    data = {
        'estimation_items': estimation_items, 
        'estimation_params': estimation_params, 
        'order_id': draft_order.id,
        'order_status': draft_order.status
    }
    return render(request, 'estimation_infusion_speed.html', {'data': data})


def update_order_params(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    order = get_object_or_404(Order, id=order_id, status=Order.OrderStatus.DRAFT)
    
    ampoules_count = request.POST.get('ampoules_count', '').strip()
    solvent_volume = request.POST.get('solvent_volume', '').strip()
    patient_weight = request.POST.get('patient_weight', '').strip()
    
    if not ampoules_count or not solvent_volume or not patient_weight:
        return redirect('estimation_infusion_speed_with_id', order_id=order_id)
    
    try:
        order.ampoules_count = int(ampoules_count)
        order.solvent_volume = float(solvent_volume)
        order.patient_weight = float(patient_weight)
    except (ValueError, TypeError):
        return redirect('estimation_infusion_speed_with_id', order_id=order_id)
    
    order.status = Order.OrderStatus.FORMED
    order.formation_datetime = timezone.now()
    order.save()
    
    drugs_in_order = DrugInOrder.objects.filter(order=order)
    for drug_in_order in drugs_in_order:
        drug_in_order.calculate_infusion_speed()
        drug_in_order.save()
    
    return redirect('estimation_infusion_speed_with_id', order_id=order_id)


def delete_order_html(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    with connection.cursor() as cursor:
        cursor.execute('UPDATE "ssr_inDb_order" SET status = %s WHERE id = %s', [Order.OrderStatus.DELETED, order_id])
    
    return redirect('search')


def complete_order_html(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    order = get_object_or_404(Order, id=order_id, status__in=[Order.OrderStatus.DRAFT, Order.OrderStatus.FORMED])
    
    order.status = Order.OrderStatus.COMPLETED
    order.completion_datetime = timezone.now()
    order.save()
    
    return redirect('search')
