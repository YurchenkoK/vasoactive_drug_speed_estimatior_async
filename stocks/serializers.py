from rest_framework import serializers
from stocks.models import Drug, Order, DrugInOrder
from django.contrib.auth.models import User
from collections import OrderedDict


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ["id", "name", "description", "image_url", "concentration", "volume", "is_active"]
    
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields


class FullDrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ["id", "name", "description", "image_url", "concentration", "volume", "is_active"]


class DrugInOrderSerializer(serializers.ModelSerializer):
    drug_id = serializers.IntegerField(source='drug.id', read_only=True)
    drug_name = serializers.CharField(source='drug.name', read_only=True)
    
    class Meta:
        model = DrugInOrder
        fields = ["id", "drug_id", "drug_name", "ampoule_volume", "infusion_speed"]


class OrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "status", "creation_datetime", "formation_datetime", 
                  "completion_datetime", "creator", "moderator", "ampoules_count", 
                  "solvent_volume", "patient_weight"]
        read_only_fields = ["creation_datetime", "formation_datetime", "completion_datetime", 
                           "creator", "moderator", "status"]
    
    def get_fields(self):
        new_fields = OrderedDict()
        for name, field in super().get_fields().items():
            field.required = False
            new_fields[name] = field
        return new_fields


class FullOrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    drugs = serializers.SerializerMethodField()
    
    class Meta:
        model = Order
        fields = ["id", "status", "creation_datetime", "formation_datetime", 
                  "completion_datetime", "creator", "moderator", "ampoules_count", 
                  "solvent_volume", "patient_weight", "drugs"]
        read_only_fields = ["creation_datetime", "formation_datetime", "completion_datetime", 
                           "creator", "moderator"]
    
    def get_drugs(self, obj):
        drug_in_orders = DrugInOrder.objects.filter(order=obj)
        return [{
            "id": dio.id,
            "drug_id": dio.drug.id,
            "drug_name": dio.drug.name,
            "ampoule_volume": dio.ampoule_volume,
            "infusion_speed": dio.infusion_speed
        } for dio in drug_in_orders]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "first_name", "last_name", "email"]


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email"]
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
