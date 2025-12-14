from django.contrib import admin
from .models import Drug, Order, DrugInOrder


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'concentration', 'volume', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    actions = ['make_active', 'make_inactive']
    
    @admin.action(description='Сделать активными')
    def make_active(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} препарат(ов) помечены как активные.')
    
    @admin.action(description='Сделать неактивными')
    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} препарат(ов) помечены как неактивные.')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'creator', 'ampoules_count', 'solvent_volume', 'patient_weight', 'creation_datetime', 'formation_datetime', 'completion_datetime')
    list_filter = ('status', 'creation_datetime')
    search_fields = ('creator__username',)
    readonly_fields = ('creation_datetime',)
    fieldsets = (
        ('Общая информация', {
            'fields': ('status', 'creator', 'moderator', 'creation_datetime', 'formation_datetime', 'completion_datetime')
        }),
        ('Параметры расчета', {
            'fields': ('ampoules_count', 'solvent_volume', 'patient_weight')
        }),
    )
    actions = ['mark_as_formed', 'mark_as_completed', 'mark_as_rejected', 'mark_as_deleted']
    
    @admin.action(description='Пометить как "Сформирован"')
    def mark_as_formed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status=Order.OrderStatus.FORMED, formation_datetime=timezone.now())
        self.message_user(request, f'{updated} заявок помечены как сформированные.')
    
    @admin.action(description='Пометить как "Завершён"')
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(status=Order.OrderStatus.COMPLETED, completion_datetime=timezone.now())
        self.message_user(request, f'{updated} заявок помечены как завершённые.')
    
    @admin.action(description='Пометить как "Отклонён"')
    def mark_as_rejected(self, request, queryset):
        updated = queryset.update(status=Order.OrderStatus.REJECTED)
        self.message_user(request, f'{updated} заявок помечены как отклонённые.')
    
    @admin.action(description='Пометить как "Удалён"')
    def mark_as_deleted(self, request, queryset):
        updated = queryset.update(status=Order.OrderStatus.DELETED)
        self.message_user(request, f'{updated} заявок помечены как удалённые.')


@admin.register(DrugInOrder)
class DrugInOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'drug', 'ampoule_volume', 'infusion_speed')
    list_filter = ('order__status',)
    search_fields = ('drug__name', 'order__id')
