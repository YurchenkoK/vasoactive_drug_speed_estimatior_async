from django.shortcuts import render
from .static.static_data import drugs_data, estimation_data

def get_data():
    drugs = []
    for drug in drugs_data:
        drugs.append({
            'id': drug[0],
            'name': drug[1],
            'description': drug[2],
            'image': drug[3],
            'concentration': f'{drug[4]} мг/мл',
            'volume': f'{drug[5]} мл',
        })
    
    return {'drugs': drugs}

def get_estimation_data():
    estimation_drugs = estimation_data[0]
    estimation_items = []
    
    for estimation_drug in estimation_drugs:
        drug_id = estimation_drug[0]
        infusion_speed = estimation_drug[2]
        for drug in drugs_data:
            if drug[0] == drug_id:
                estimation_items.append({
                    'id': drug[0],
                    'name': drug[1],
                    'concentration': f'{drug[4]} мг/мл',
                    'volume': f'{drug[5]} мл',
                    'image': drug[3],
                    'infusion_speed': infusion_speed,
                })
                break
    
    return {'estimation_items': estimation_items}

def index(request):
    data = get_data()
    search_query = request.GET.get('search', '')
    
    if search_query:
        filtered_drugs = []
        for drug in data['drugs']:
            if search_query.lower() in drug['name'].lower():
                filtered_drugs.append(drug)
        data['drugs'] = filtered_drugs
    
    estimation_count = len(estimation_data[0])
    data['estimation_count'] = estimation_count
    
    return render(request, 'main.html', {'data': data, 'search_query': search_query})

def vasoactive_drug_detail(request, drug_id):
    data = get_data()
    drug = None
    
    for d in data['drugs']:
        if d['id'] == drug_id:
            drug = d
            break
    
    estimation_count = len(estimation_data[0])
    
    return render(request, 'vasoactive_drug.html', {'drug': drug, 'estimation_count': estimation_count})

def estimation_infusion_speed(request):
    data = get_estimation_data()
    
    estimation_params = {
        'ampoules': int(estimation_data[1][0]),
        'solvent_volume': estimation_data[1][1],
        'patient_weight': estimation_data[1][2],
    }
    
    data['estimation_params'] = estimation_params
    return render(request, 'estimation_infusion_speed.html', {'data': data})