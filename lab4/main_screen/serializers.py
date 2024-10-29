from main_screen.models import Rent_Service, Rent_Order, Rent_OrderService, CustomUser
from rest_framework import serializers
from collections import OrderedDict
from django.contrib.auth.hashers import make_password

class Rent_ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent_Service
        fields = ["pk", "title", "price", "description", "icon", "icon1", "status"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False  # Устанавливаем поле как необязательное
                new_fields[name] = field
            return new_fields

class Rent_OrderServiceSerializer(serializers.ModelSerializer):
    service = Rent_ServiceSerializer(read_only=True)

    class Meta:
        model = Rent_OrderService
        fields = ["order", "service", "last_reading", "current_reading"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False  # Устанавливаем поле как необязательное
                new_fields[name] = field
            return new_fields

class Rent_OrderSerializer(serializers.ModelSerializer):
    services = Rent_OrderServiceSerializer(source='rent_orderservice_set', many=True, read_only=True)

    class Meta:
        model = Rent_Order
        fields = ["pk", "order_date", "address", "status", "total_amount", "formation_date", "completion_date", "moderator", "client", "services"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False  # Устанавливаем поле как необязательное
                new_fields[name] = field
            return new_fields
        
class UserSerializer(serializers.ModelSerializer):
    is_staff = serializers.BooleanField(default=False, required=False)
    is_superuser = serializers.BooleanField(default=False, required=False)
    class Meta:
        model = CustomUser
        fields = ['email', 'password', 'is_staff', 'is_superuser']


class Rent_OrderrSerializer(serializers.ModelSerializer):

    class Meta:
        model = Rent_Order
        fields = ["pk", "order_date", "address", "status", "total_amount", "formation_date", "completion_date", "moderator", "client"]

        def get_fields(self):
            new_fields = OrderedDict()
            for name, field in super().get_fields().items():
                field.required = False  # Устанавливаем поле как необязательное
                new_fields[name] = field
            return new_fields