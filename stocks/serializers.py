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
    drug_detail = DrugSerializer(source='drug', read_only=True)
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
            'drug_detail',
            'ampoule_volume',
            'infusion_speed',
        ]
        read_only_fields = ['id', 'drug_detail']
    
    def update(self, instance, validated_data):
        validated_data.pop('drug', None)
        return super().update(instance, validated_data)


class OrderSerializer(serializers.ModelSerializer):
    items = DrugInOrderSerializer(many=True, read_only=True)
    
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
            'items',
            'ampoules_count',
            'solvent_volume',
            'patient_weight'
        ]
        read_only_fields = ['id', 'creator', 'moderator', 'status', 'creation_datetime', 'formation_datetime', 'completion_datetime']


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(read_only=True)
