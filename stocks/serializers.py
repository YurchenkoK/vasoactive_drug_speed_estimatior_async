from rest_framework import serializers
from stocks.models import Drug, Order, DrugInOrder
from django.contrib.auth.models import User


class DrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ["id", "name", "description", "image_url", "concentration", "volume", "is_active"]


class FullDrugSerializer(serializers.ModelSerializer):
    class Meta:
        model = Drug
        fields = ["id", "name", "description", "image_url", "concentration", "volume", "is_active"]


class DrugInOrderSerializer(serializers.ModelSerializer):
    drug = DrugSerializer(read_only=True)
    
    class Meta:
        model = DrugInOrder
        fields = ["id", "drug", "infusion_speed", "drug_rate"]


class OrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "status", "creation_datetime", "formation_datetime", 
                  "completion_datetime", "creator", "moderator", "ampoules_count", 
                  "solvent_volume", "patient_weight"]
        read_only_fields = ["creation_datetime", "formation_datetime", "completion_datetime", 
                           "creator", "moderator"]


class FullOrderSerializer(serializers.ModelSerializer):
    creator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    moderator = serializers.SlugRelatedField(slug_field='username', read_only=True)
    druginorder_set = DrugInOrderSerializer(many=True, read_only=True)
    
    class Meta:
        model = Order
        fields = ["id", "status", "creation_datetime", "formation_datetime", 
                  "completion_datetime", "creator", "moderator", "ampoules_count", 
                  "solvent_volume", "patient_weight", "druginorder_set"]
        read_only_fields = ["creation_datetime", "formation_datetime", "completion_datetime", 
                           "creator", "moderator"]


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
