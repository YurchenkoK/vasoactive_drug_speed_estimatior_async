
from rest_framework.response import Response
from django.shortcuts import get_object_or_404, render, redirect
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import Http404, HttpResponse
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from stocks.serializers import (
    DrugSerializer, FullDrugSerializer, OrderSerializer, 
    FullOrderSerializer, DrugInOrderSerializer, UserSerializer, UserRegistrationSerializer
)
from stocks.models import Drug, Order, DrugInOrder
from minio import Minio
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from stocks.permissions import IsManager, IsAdmin


def get_user(request):
    if request.user.is_authenticated:
        return request.user
    return None


def process_file_upload(file_object: InMemoryUploadedFile, client, image_name):
    try:
        bucket_name = 'images'
        
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
        
        client.put_object(bucket_name, image_name, file_object, file_object.size)
        
        return f"http://localhost:9000/{bucket_name}/{image_name}"
    except Exception as e:
        return {"error": str(e)}


def add_pic(drug, pic):
    endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
    client = Minio(
        endpoint=endpoint,
        access_key=settings.AWS_ACCESS_KEY_ID,
        secret_key=settings.AWS_SECRET_ACCESS_KEY,
        secure=settings.MINIO_USE_SSL
    )
    
    img_obj_name = pic.name
    
    if not pic:
        return Response({"error": "Нет файла для изображения логотипа."})
    
    result = process_file_upload(pic, client, img_obj_name)
    
    if isinstance(result, dict) and 'error' in result:
        return Response(result)
    
    drug.image_url = result
    drug.save()
    
    return Response({"message": "success"})


def delete_pic(drug):
    if not drug.image_url:
        return
    
    try:
        endpoint = settings.AWS_S3_ENDPOINT_URL.replace('http://', '').replace('https://', '')
        client = Minio(
            endpoint=endpoint,
            access_key=settings.AWS_ACCESS_KEY_ID,
            secret_key=settings.AWS_SECRET_ACCESS_KEY,
            secure=settings.MINIO_USE_SSL
        )
        
        img_obj_name = drug.image_url.split('/')[-1]
        client.remove_object('images', img_obj_name)
    except Exception as e:
        print(f"Error deleting image: {e}")


class UserRegistration(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    
    @swagger_auto_schema(
        request_body=UserRegistrationSerializer,
        responses={201: UserSerializer, 400: 'Bad Request'}
    )
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
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получить информацию о профиле пользователя. Пользователь может просматривать только свой профиль.",
        responses={200: UserSerializer, 403: 'Forbidden', 404: 'Not Found'}
    )
    def get(self, request, pk, format=None):
        if request.user.id != pk:
            return Response({"error": "Доступ запрещен"}, 
                          status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: 'Bad Request', 403: 'Forbidden'}
    )
    def put(self, request, pk, format=None):
        if request.user.id != pk:
            return Response({"error": "Доступ запрещен"}, 
                          status=status.HTTP_403_FORBIDDEN)
        user = get_object_or_404(User, pk=pk)
        serializer = UserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(
    method='post',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['username', 'password'],
        properties={
            'username': openapi.Schema(type=openapi.TYPE_STRING, description='Имя пользователя'),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description='Пароль')
        }
    ),
    responses={200: UserSerializer, 400: 'Bad Request', 401: 'Unauthorized'}
)
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def user_login(request):
    username = request.data.get('username')
    password = request.data.get('password')
    
    if not username or not password:
        return Response({"error": "Укажите username и password"}, 
                       status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(request, username=username, password=password)
    
    if user is not None:
        login(request, user)
        return Response({
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "is_staff": user.is_staff,
            "is_superuser": user.is_superuser,
            "message": "Успешная аутентификация"
        })
    else:
        return Response({"error": "Неверные учетные данные"}, 
                       status=status.HTTP_401_UNAUTHORIZED)


@swagger_auto_schema(
    method='post',
    responses={200: 'Success'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    logout(request)
    return Response({"message": "Деавторизация выполнена"})


@swagger_auto_schema(
    method='get',
    responses={200: openapi.Response('Cart info', schema=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'order_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            'count': openapi.Schema(type=openapi.TYPE_INTEGER),
        }
    ))}
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cart_icon(request):
    user = request.user
    try:
        order = Order.objects.get(creator=user, status=Order.OrderStatus.DRAFT)
        count = DrugInOrder.objects.filter(order=order).count()
        return Response({"order_id": order.id, "count": count})
    except Order.DoesNotExist:
        return Response({"order_id": None, "count": 0})


class OrderList(APIView):
    """
    Список заявок текущего пользователя
    GET: только для аутентифицированных пользователей (свои заявки) или менеджеров (все заявки)
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('date_from', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date'),
            openapi.Parameter('date_to', openapi.IN_QUERY, type=openapi.TYPE_STRING, format='date'),
            openapi.Parameter('status', openapi.IN_QUERY, type=openapi.TYPE_STRING),
        ],
        responses={200: OrderSerializer(many=True)}
    )
    def get(self, request, format=None):
        user = request.user
        
        if user.is_staff or user.is_superuser:
            orders = Order.objects.exclude(
                status__in=[Order.OrderStatus.DELETED, Order.OrderStatus.DRAFT]
            )
        else:
            orders = Order.objects.filter(creator=user).exclude(
                status__in=[Order.OrderStatus.DELETED, Order.OrderStatus.DRAFT]
            )
        
        date_from = request.query_params.get('date_from', None)
        date_to = request.query_params.get('date_to', None)
        if date_from:
            orders = orders.filter(formation_datetime__gte=date_from)
        if date_to:
            orders = orders.filter(formation_datetime__lte=date_to)
        
        order_status = request.query_params.get('status', None)
        if order_status:
            orders = orders.filter(status=order_status)
        
        orders = orders.order_by('status', '-creation_datetime')
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetail(APIView):
    """
    Детальная информация о заявке
    GET: просмотр заявки
    PUT: изменение полей заявки (только создатель в статусе DRAFT)
    DELETE: логическое удаление заявки (только создатель)
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]
    
    @swagger_auto_schema(
        operation_description="Получить детальную информацию о заявке. Доступно создателю и модераторам.",
        responses={200: FullOrderSerializer, 403: 'Forbidden', 404: 'Not Found'}
    )
    def get(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        if order.creator != request.user and not (request.user.is_staff or request.user.is_superuser):
            return Response({"error": "Нет доступа к этой заявке"}, 
                          status=status.HTTP_403_FORBIDDEN)
        if order.status == Order.OrderStatus.DELETED:
            return Response({"error": "Заявка удалена"}, status=status.HTTP_404_NOT_FOUND)
        serializer = FullOrderSerializer(order)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=OrderSerializer,
        responses={200: OrderSerializer, 400: 'Bad Request', 403: 'Forbidden'}
    )
    def put(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        if order.creator != request.user:
            return Response({"error": "Можно редактировать только свои заявки"}, 
                          status=status.HTTP_403_FORBIDDEN)
        if order.status != Order.OrderStatus.DRAFT:
            return Response({"error": "Можно редактировать только черновики"}, 
                          status=status.HTTP_403_FORBIDDEN)
        serializer = OrderSerializer(order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        order = get_object_or_404(Order, pk=pk)
        if order.creator != request.user:
            return Response({"error": "Можно удалять только свои заявки"}, 
                          status=status.HTTP_403_FORBIDDEN)
        order.status = Order.OrderStatus.DELETED
        order.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='put',
    responses={200: FullOrderSerializer, 400: 'Bad Request', 403: 'Forbidden'}
)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def form_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.creator != request.user:
        return Response({"error": "Можно формировать только свои заявки"}, 
                       status=status.HTTP_403_FORBIDDEN)
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


@swagger_auto_schema(
    method='put',
    responses={200: FullOrderSerializer, 403: 'Forbidden'}
)
@api_view(['PUT'])
@permission_classes([IsManager])
def complete_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status != Order.OrderStatus.FORMED:
        return Response({"error": "Можно завершать только сформированную заявку"}, 
                       status=status.HTTP_403_FORBIDDEN)
    order.status = Order.OrderStatus.COMPLETED
    order.completion_datetime = timezone.now()
    order.moderator = request.user
    order.save()
    for drug_in_order in DrugInOrder.objects.filter(order=order):
        drug_in_order.calculate_infusion_speed()
        drug_in_order.save()
    serializer = FullOrderSerializer(order)
    return Response(serializer.data)


@swagger_auto_schema(
    method='put',
    responses={200: FullOrderSerializer, 403: 'Forbidden'}
)
@api_view(['PUT'])
@permission_classes([IsManager])
def reject_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if order.status != Order.OrderStatus.FORMED:
        return Response({"error": "Можно отклонять только сформированную заявку"}, 
                       status=status.HTTP_403_FORBIDDEN)
    order.status = Order.OrderStatus.REJECTED
    order.completion_datetime = timezone.now()
    order.moderator = request.user
    order.save()
    serializer = FullOrderSerializer(order)
    return Response(serializer.data)




@swagger_auto_schema(
    method='delete',
    responses={204: 'No Content', 403: 'Forbidden'},
    tags=['M-M']
)
@swagger_auto_schema(
    method='put',
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        properties={
            'ampoule_volume': openapi.Schema(type=openapi.TYPE_NUMBER, description='Объём ампулы (мл)'),
            'drug_rate': openapi.Schema(type=openapi.TYPE_NUMBER, description='Скорость введения препарата')
        }
    ),
    responses={200: 'Success', 403: 'Forbidden'},
    tags=['M-M']
)
@api_view(['DELETE', 'PUT'])
@permission_classes([IsAuthenticated])
def drug_in_order_actions(request, order_pk, drug_pk):
    order = get_object_or_404(Order, pk=order_pk)
    if order.creator != request.user:
        return Response({"error": "Можно изменять только свои заявки"}, 
                       status=status.HTTP_403_FORBIDDEN)
    if order.status != Order.OrderStatus.DRAFT:
        return Response({"error": "Можно изменять препараты только в черновике"}, 
                       status=status.HTTP_403_FORBIDDEN)
    
    drug_in_order = get_object_or_404(DrugInOrder, order=order, drug_id=drug_pk)
    
    if request.method == 'DELETE':
        drug_in_order.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    elif request.method == 'PUT':
        ampoule_volume = request.data.get('ampoule_volume')
        drug_rate = request.data.get('drug_rate')
        
        if ampoule_volume is not None:
            try:
                ampoule_volume_str = str(ampoule_volume).replace(',', '.')
                drug_in_order.ampoule_volume = float(ampoule_volume_str)
            except (ValueError, TypeError):
                return Response({"error": "Неверный формат объёма ампулы"}, 
                               status=status.HTTP_400_BAD_REQUEST)
        
        if drug_rate is not None:
            try:
                drug_rate_str = str(drug_rate).replace(',', '.')
                drug_in_order.drug_rate = float(drug_rate_str)
            except (ValueError, TypeError):
                return Response({"error": "Неверный формат скорости введения"}, 
                               status=status.HTTP_400_BAD_REQUEST)
        
        drug_in_order.save()
        drug_in_order.calculate_infusion_speed()
        drug_in_order.save()
        
        serializer = DrugInOrderSerializer(drug_in_order)
        return Response(serializer.data)




class DrugList(APIView):
    """
    Список всех активных препаратов
    GET: доступно всем (включая гостей)
    POST: только для администраторов
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_description="Получить список всех активных препаратов. Доступно без авторизации.",
        manual_parameters=[
            openapi.Parameter('name', openapi.IN_QUERY, type=openapi.TYPE_STRING, 
                            description='Фильтр по названию препарата')
        ],
        responses={200: DrugSerializer(many=True)}
    )
    def get(self, request, format=None):
        drugs = Drug.objects.filter(is_active=True)
        name = request.query_params.get('name', None)
        if name:
            drugs = drugs.filter(name__icontains=name)
        serializer = DrugSerializer(drugs, many=True)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=DrugSerializer,
        responses={201: DrugSerializer, 400: 'Bad Request'}
    )
    def post(self, request, format=None):
        if not request.user.is_superuser:
            return Response({"error": "Только администратор может добавлять препараты"}, 
                          status=status.HTTP_403_FORBIDDEN)
        serializer = DrugSerializer(data=request.data)
        if serializer.is_valid():
            drug = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DrugDetail(APIView):
    """
    Детальная информация о препарате
    GET: доступно всем
    PUT: только для администраторов
    DELETE: только для администраторов
    """
    authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    @swagger_auto_schema(
        operation_description="Получить детальную информацию о препарате. Доступно без авторизации.",
        responses={200: FullDrugSerializer, 404: 'Not Found'}
    )
    def get(self, request, pk, format=None):
        drug = get_object_or_404(Drug, pk=pk, is_active=True)
        serializer = FullDrugSerializer(drug)
        return Response(serializer.data)
    
    @swagger_auto_schema(
        request_body=DrugSerializer,
        responses={200: DrugSerializer, 400: 'Bad Request', 403: 'Forbidden'}
    )
    def put(self, request, pk, format=None):
        if not request.user.is_superuser:
            return Response({"error": "Только администратор может редактировать препараты"}, 
                          status=status.HTTP_403_FORBIDDEN)
        drug = get_object_or_404(Drug, pk=pk)
        serializer = DrugSerializer(drug, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk, format=None):
        if not request.user.is_superuser:
            return Response({"error": "Только администратор может удалять препараты"}, 
                          status=status.HTTP_403_FORBIDDEN)
        drug = get_object_or_404(Drug, pk=pk)
        drug.is_active = False
        drug.save()
        delete_pic(drug)
        return Response(status=status.HTTP_204_NO_CONTENT)


@swagger_auto_schema(
    method='post',
    responses={200: DrugSerializer, 400: 'Bad Request', 403: 'Forbidden'}
)
@api_view(['POST'])
@permission_classes([IsAdmin])
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


@swagger_auto_schema(
    method='post',
    responses={201: 'Created', 200: 'Already exists', 401: 'Unauthorized'}
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_drug_to_order(request, pk):
    drug = get_object_or_404(Drug, pk=pk, is_active=True)
    user = request.user
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
    if request.user.is_authenticated:
        user = request.user
    else:
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
        ampoule_vol = drug_in_order.ampoule_volume if drug_in_order.ampoule_volume else drug_in_order.drug.volume
        ampoule_vol_str = str(ampoule_vol).replace(',', '.')
        
        estimation_items.append({
            'id': drug_in_order.drug.id,
            'drug_id': drug_in_order.drug.id,
            'name': drug_in_order.drug.name,
            'concentration': f'{drug_in_order.drug.concentration} мг/мл',
            'volume': f'{drug_in_order.drug.volume} мл',
            'ampoule_volume': ampoule_vol_str,
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

