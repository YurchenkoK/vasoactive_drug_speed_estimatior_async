from django.shortcuts import render, redirect, get_object_or_404
from django.db import connection
from django.contrib.auth.models import User
from .models import Drug, Order, DrugInOrder


def index(request):
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


def add_to_order(request, drug_id):
    if request.method != 'POST':
        return redirect('index')
    
    drug = get_object_or_404(Drug, id=drug_id, is_active=True)
    user = User.objects.first()
    if not user:
        user = User.objects.create_user(username='testuser', password='testpass')
    
    dosage = request.POST.get('dosage', 5.0)
    try:
        dosage = float(dosage)
    except:
        dosage = 5.0
    
    draft_order, created = Order.objects.get_or_create(
        creator=user,
        status=Order.OrderStatus.DRAFT
    )
    
    drug_in_order, created = DrugInOrder.objects.get_or_create(
        order=draft_order,
        drug=drug,
        defaults={'dosage': dosage}
    )
    
    if not created:
        drug_in_order.dosage = dosage
        drug_in_order.save()
    
    return redirect('vasoactive_drug_detail', drug_id=drug_id)


def estimation_infusion_speed(request, order_id=None):
    user = User.objects.first()
    if not user:
        data = {'estimation_items': [], 'estimation_params': {'ampoules': 0, 'solvent_volume': 0, 'patient_weight': 0}}
        return render(request, 'estimation_infusion_speed.html', {'data': data})
    
    # Если передан order_id, ищем конкретную заявку
    if order_id:
        draft_order = Order.objects.filter(
            id=order_id,
            creator=user, 
            status__in=[Order.OrderStatus.DRAFT, Order.OrderStatus.FORMED]
        ).first()
    else:
        # Ищем заявку в статусе DRAFT или FORMED
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
    
    # Получаем параметры заявки
    ampoules_count = request.POST.get('ampoules_count', '').strip()
    solvent_volume = request.POST.get('solvent_volume', '').strip()
    patient_weight = request.POST.get('patient_weight', '').strip()
    
    # Проверяем, что все поля заполнены
    if not ampoules_count or not solvent_volume or not patient_weight:
        # Если хотя бы одно поле пустое, перенаправляем обратно без изменений
        return redirect('estimation_infusion_speed_with_id', order_id=order_id)
    
    # Обновляем параметры заявки
    try:
        order.ampoules_count = int(ampoules_count)
        order.solvent_volume = float(solvent_volume)
        order.patient_weight = float(patient_weight)
    except (ValueError, TypeError):
        # Если произошла ошибка конвертации, перенаправляем обратно
        return redirect('estimation_infusion_speed_with_id', order_id=order_id)
    
    # Сохраняем заявку (статус остается DRAFT)
    order.save()
    
    # Пересчитываем скорость инфузии для всех препаратов в заявке
    drugs_in_order = DrugInOrder.objects.filter(order=order)
    for drug_in_order in drugs_in_order:
        drug_in_order.calculate_infusion_speed()
        drug_in_order.save()
    
    return redirect('estimation_infusion_speed_with_id', order_id=order_id)


def delete_order(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    with connection.cursor() as cursor:
        cursor.execute('UPDATE "ssr_inDb_order" SET status = %s WHERE id = %s', [Order.OrderStatus.DELETED, order_id])
    
    return redirect('index')


def complete_order(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    from django.utils import timezone
    order = get_object_or_404(Order, id=order_id, status__in=[Order.OrderStatus.DRAFT, Order.OrderStatus.FORMED])
    
    # Завершаем заявку (сразу переводим в COMPLETED)
    order.status = Order.OrderStatus.COMPLETED
    order.completion_datetime = timezone.now()
    order.save()
    
    return redirect('index')
