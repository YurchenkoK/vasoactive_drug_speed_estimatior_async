from django.db import models
from django.contrib.auth.models import User


class Drug(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    description = models.TextField(verbose_name="Показания")
    image_url = models.URLField(max_length=500, null=True, blank=True, verbose_name="URL изображения")
    concentration = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Концентрация (мг/мл)")
    volume = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Объём ампулы (мл)")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    class Meta:
        verbose_name = "Препарат"
        verbose_name_plural = "Препараты"
    
    def __str__(self):
        return self.name


class Order(models.Model):
    class OrderStatus(models.TextChoices):
        DRAFT = "DRAFT", "Черновик"
        DELETED = "DELETED", "Удалён"
        FORMED = "FORMED", "Сформирован"
        COMPLETED = "COMPLETED", "Завершён"
        REJECTED = "REJECTED", "Отклонён"
    
    status = models.CharField(max_length=10, choices=OrderStatus.choices, default=OrderStatus.DRAFT, verbose_name="Статус")
    creation_datetime = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    formation_datetime = models.DateTimeField(blank=True, null=True, verbose_name="Дата формирования")
    completion_datetime = models.DateTimeField(blank=True, null=True, verbose_name="Дата завершения")
    creator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_orders', verbose_name="Создатель")
    moderator = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='moderated_orders', blank=True, null=True, verbose_name="Модератор")
    ampoules_count = models.IntegerField(default=1, verbose_name="Количество ампул")
    solvent_volume = models.DecimalField(max_digits=10, decimal_places=2, default=100.0, verbose_name="Объём растворителя (мл)")
    patient_weight = models.DecimalField(max_digits=10, decimal_places=2, default=70.0, verbose_name="Масса пациента (кг)")
    
    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
    
    def __str__(self):
        return f"Заявка № {self.id} ({self.get_status_display()})"


class DrugInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, verbose_name="Заявка")
    drug = models.ForeignKey(Drug, on_delete=models.DO_NOTHING, verbose_name="Препарат")
    dosage = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Дозировка (мкг/кг/мин)")
    infusion_speed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Скорость инфузии (мл/ч)")
    
    class Meta:
        verbose_name = "Препарат в заявке"
        verbose_name_plural = "Препараты в заявках"
        unique_together = ('order', 'drug')
    
    def __str__(self):
        return f"{self.order.id}-{self.drug.name}"
    
    def calculate_infusion_speed(self):
        if self.order and self.drug:
            total_drug_mg = self.drug.concentration * self.order.ampoules_count * self.drug.volume
            concentration_in_solution = total_drug_mg / self.order.solvent_volume
            infusion_speed = (self.dosage * self.order.patient_weight * 60) / (concentration_in_solution * 1000)
            self.infusion_speed = round(infusion_speed, 2)
            return self.infusion_speed
        return None
