from django.contrib import admin
from .models import Drug, Order, DrugInOrder


@admin.register(Drug)
class DrugAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'concentration', 'volume', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'creator', 'creation_datetime', 'formation_datetime', 'completion_datetime')
    list_filter = ('status', 'creation_datetime')
    search_fields = ('creator__username',)
    readonly_fields = ('creation_datetime',)


@admin.register(DrugInOrder)
class DrugInOrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'order', 'drug', 'dosage', 'infusion_speed')
    list_filter = ('order__status',)
    search_fields = ('drug__name', 'order__id')
