from django.shortcuts import render, redirect, get_object_or_404
from django.http import Http404
from django.db import connection
from django.contrib.auth.models import User
from .models import Drug, Order, DrugInOrder


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


def add_to_order(request, drug_id):
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
    
    order.save()
    
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
    
    return redirect('search')


def complete_order(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    from django.utils import timezone
    order = get_object_or_404(Order, id=order_id, status__in=[Order.OrderStatus.DRAFT, Order.OrderStatus.FORMED])
    
    order.status = Order.OrderStatus.COMPLETED
    order.completion_datetime = timezone.now()
    order.save()
    
    return redirect('search')
