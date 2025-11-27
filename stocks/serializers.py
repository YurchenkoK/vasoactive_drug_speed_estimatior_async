from rest_framework import serializers
from stocks.models import Drug, Order, DrugInOrder
from django.contrib.auth.models import User
from collections import OrderedDict
from stocks.redis_client import redis_user_client


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


class UserSerializer(serializers.Serializer):
    """Serializer for Redis-based users"""
    id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(max_length=150)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    is_staff = serializers.BooleanField(read_only=True, default=False)
    is_superuser = serializers.BooleanField(read_only=True, default=False)
    
    def update(self, instance, validated_data):
        """Update user in Redis"""
        username = instance.get('username')
        # Remove username and id from updates
        validated_data.pop('username', None)
        validated_data.pop('id', None)
        
        updated_user = redis_user_client.update_user(username, **validated_data)
        return updated_user
    
    def to_representation(self, instance):
        """Convert user dict to representation"""
        if isinstance(instance, dict):
            return {
                'id': instance.get('id'),
                'username': instance.get('username'),
                'first_name': instance.get('first_name', ''),
                'last_name': instance.get('last_name', ''),
                'email': instance.get('email', ''),
                'is_staff': instance.get('is_staff', False),
                'is_superuser': instance.get('is_superuser', False),
            }
        return super().to_representation(instance)


class UserRegistrationSerializer(serializers.Serializer):
    """Serializer for user registration with Redis"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default='')
    email = serializers.EmailField(required=False, allow_blank=True, default='')
    
    def validate_username(self, value):
        """Check if username already exists in Redis"""
        if redis_user_client.user_exists(value):
            raise serializers.ValidationError("Пользователь с таким именем уже существует")
        return value
    
    def validate_password(self, value):
        """Validate password length"""
        if len(value) < 6:
            raise serializers.ValidationError("Пароль должен содержать минимум 6 символов")
        return value
    
    def create(self, validated_data):
        """Create user in Redis"""
        user = redis_user_client.register_user(
            username=validated_data['username'],
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', '')
        )
        return user


class UserLoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, max_length=128)
