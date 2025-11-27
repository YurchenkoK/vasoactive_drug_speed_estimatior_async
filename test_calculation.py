"""
Тестовый скрипт для проверки корректности расчётов скорости введения
"""

# Тестовые данные
drug_concentration = 1.0  # мг/мл
ampoules_count = 2  # шт
ampoule_volume = 10.0  # мл
solvent_volume = 50.0  # мл
patient_weight = 70.0  # кг

# Расчёт по новой формуле
# 1. Общее количество препарата в мг
total_drug_mg = drug_concentration * ampoules_count * ampoule_volume
print(f"Общее количество препарата: {total_drug_mg} мг")

# 2. Скорость инфузии в мл/час (растворитель вводится за 60 минут)
infusion_speed_ml_hour = solvent_volume
print(f"Скорость инфузии раствора: {infusion_speed_ml_hour} мл/час")

# 3. Количество препарата, вводимое за час (мг/час)
drug_mg_per_hour = (infusion_speed_ml_hour / solvent_volume) * total_drug_mg
print(f"Количество препарата за час: {drug_mg_per_hour} мг/час")

# 4. Скорость введения препарата (мг/кг/час)
infusion_speed = drug_mg_per_hour / patient_weight
print(f"\n=== РЕЗУЛЬТАТ ===")
print(f"Скорость введения: {infusion_speed:.2f} мг/кг/час")

print("\n=== ПРОВЕРКА ===")
print(f"Концентрация: {drug_concentration} мг/мл")
print(f"Количество ампул: {ampoules_count} шт")
print(f"Объём ампулы: {ampoule_volume} мл")
print(f"Объём растворителя: {solvent_volume} мл")
print(f"Масса пациента: {patient_weight} кг")
