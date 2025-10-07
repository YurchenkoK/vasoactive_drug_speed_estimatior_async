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
    try:
        user = User.objects.first()
        if user:
            draft_order = Order.objects.filter(creator=user, status=Order.OrderStatus.DRAFT).first()
            if draft_order:
                estimation_count = DrugInOrder.objects.filter(order=draft_order).count()
    except:
        pass
    
    data = {'drugs': drugs_data, 'estimation_count': estimation_count}
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
    try:
        user = User.objects.first()
        if user:
            draft_order = Order.objects.filter(creator=user, status=Order.OrderStatus.DRAFT).first()
            if draft_order:
                estimation_count = DrugInOrder.objects.filter(order=draft_order).count()
    except:
        pass
    
    return render(request, 'vasoactive_drug.html', {'drug': drug_data, 'estimation_count': estimation_count})


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
        status=Order.OrderStatus.DRAFT,
        defaults={'ampoules_count': 2, 'solvent_volume': 100.0, 'patient_weight': 70.0}
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


def estimation_infusion_speed(request):
    user = User.objects.first()
    if not user:
        data = {'estimation_items': [], 'estimation_params': {'ampoules': 0, 'solvent_volume': 0, 'patient_weight': 0}}
        return render(request, 'estimation_infusion_speed.html', {'data': data})
    
    draft_order = Order.objects.filter(creator=user, status=Order.OrderStatus.DRAFT).first()
    if not draft_order:
        data = {'estimation_items': [], 'estimation_params': {'ampoules': 0, 'solvent_volume': 0, 'patient_weight': 0}}
        return render(request, 'estimation_infusion_speed.html', {'data': data})
    
    drugs_in_order = DrugInOrder.objects.filter(order=draft_order).select_related('drug')
    estimation_items = []
    for drug_in_order in drugs_in_order:
        drug_in_order.calculate_infusion_speed()
        drug_in_order.save()
        estimation_items.append({
            'id': drug_in_order.drug.id,
            'name': drug_in_order.drug.name,
            'concentration': f'{drug_in_order.drug.concentration} мг/мл',
            'volume': f'{drug_in_order.drug.volume} мл',
            'image': drug_in_order.drug.image_url or 'http://localhost:9000/images/default.png',
            'infusion_speed': f'{drug_in_order.infusion_speed}' if drug_in_order.infusion_speed else '0',
        })
    
    estimation_params = {
        'ampoules': draft_order.ampoules_count,
        'solvent_volume': float(draft_order.solvent_volume),
        'patient_weight': float(draft_order.patient_weight),
    }
    
    data = {'estimation_items': estimation_items, 'estimation_params': estimation_params, 'order_id': draft_order.id}
    return render(request, 'estimation_infusion_speed.html', {'data': data})


def delete_order(request, order_id):
    if request.method != 'POST':
        return redirect('estimation_infusion_speed')
    
    with connection.cursor() as cursor:
        cursor.execute("UPDATE ssr_indb_order SET status = %s WHERE id = %s", [Order.OrderStatus.DELETED, order_id])
    
    return redirect('index')
