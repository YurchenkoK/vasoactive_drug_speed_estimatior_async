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
        db_table = 'ssr_inDb_drug'
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
    ampoules_count = models.IntegerField(blank=True, null=True, verbose_name="Количество ампул")
    solvent_volume = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Объём растворителя (мл)")
    patient_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True, verbose_name="Масса пациента (кг)")
    
    class Meta:
        db_table = 'ssr_inDb_order'
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
    
    def __str__(self):
        return f"Заявка № {self.id} ({self.get_status_display()})"


class DrugInOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.DO_NOTHING, verbose_name="Заявка")
    drug = models.ForeignKey(Drug, on_delete=models.DO_NOTHING, verbose_name="Препарат")
    ampoule_volume = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Объём ампулы (мл)")
    infusion_speed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Скорость инфузии (мл/мин)")
    drug_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="Скорость введения (мг/кг/час)")
    
    class Meta:
        db_table = 'ssr_inDb_druginorder'
        verbose_name = "Препарат в заявке"
        verbose_name_plural = "Препараты в заявках"
        unique_together = ('order', 'drug')
    
    def __str__(self):
        return f"{self.order.id}-{self.drug.name}"
    
    def save(self, *args, **kwargs):
        if not self.ampoule_volume:
            self.ampoule_volume = self.drug.volume
        super().save(*args, **kwargs)
    
    def calculate_infusion_speed(self):
        if self.order and self.order.solvent_volume and self.order.patient_weight:
            volume = self.ampoule_volume if self.ampoule_volume else self.drug.volume
            total_drug_mg = self.drug.concentration * self.order.ampoules_count * volume
            infusion_speed_ml_min = self.order.solvent_volume / 60
            infusion_speed_ml_hour = infusion_speed_ml_min * 60
            drug_mg_per_hour = (infusion_speed_ml_hour / self.order.solvent_volume) * total_drug_mg
            drug_rate_mg_kg_hour = drug_mg_per_hour / self.order.patient_weight
            
            self.infusion_speed = round(infusion_speed_ml_min, 2)
            self.drug_rate = round(drug_rate_mg_kg_hour, 2)
            return self.infusion_speed, self.drug_rate
        return None, None
