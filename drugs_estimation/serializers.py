from rest_framework import serializers
from stocks.models import Drug, Order, DrugInOrder
from collections import OrderedDict


class DrugSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Drug
        fields = ["id", "name", "description", "concentration", "volume", "image_url"]
        read_only_fields = ['id', 'image_url']
    
    def get_image_url(self, obj):
        return obj.image_url if obj.image_url else None


class DrugInOrderSerializer(serializers.ModelSerializer):
    drug = serializers.PrimaryKeyRelatedField(
        queryset=Drug.objects.filter(is_active=True)
    )
    order = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all()
    )
    
    class Meta:
        model = DrugInOrder
        fields = [
            'id',
            'order',
            'drug',
            'ampoule_volume',
            'infusion_speed',
            'async_calculation_result',
        ]
        read_only_fields = ['id']
    
    def update(self, instance, validated_data):
        validated_data.pop('drug', None)
        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    # Removed nested 'items' from all Order responses per API requirement
    class Meta:
        model = Order
        fields = [
            'id',
            'creator',
            'moderator',
            'status',
            'creation_datetime',
            'formation_datetime',
            'completion_datetime',
            'ampoules_count',
            'solvent_volume',
            'patient_weight'
        ]
        read_only_fields = ['id', 'creator', 'moderator', 'status', 'creation_datetime', 'formation_datetime', 'completion_datetime']


class OrderListSerializer(serializers.ModelSerializer):
    """Serializer for order list view — excludes item details to keep list compact."""
    async_results_count = serializers.SerializerMethodField()
    items = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = [
            'id',
            'creator',
            'moderator',
            'status',
            'creation_datetime',
            'formation_datetime',
            'completion_datetime',
            'ampoules_count',
            'solvent_volume',
            'patient_weight',
            'async_results_count',
            'items'
        ]
        read_only_fields = ['id', 'creator', 'moderator', 'status', 'creation_datetime', 'formation_datetime', 'completion_datetime']
    
    def get_async_results_count(self, obj):
        """Возвращает количество DrugInOrder с заполненным async_calculation_result"""
        return obj.items.filter(async_calculation_result__isnull=False).exclude(async_calculation_result='').count()
    
    def get_items(self, obj):
        """Возвращает массив ID препаратов в заявке"""
        return list(obj.items.values_list('drug_id', flat=True))


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(read_only=True)
    is_superuser = serializers.BooleanField(read_only=True)
