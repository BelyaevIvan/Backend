from main_screen.models import Rent_Service, Rent_Order, Rent_OrderService
from rest_framework import serializers


class Rent_ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rent_Service
        fields = ["pk", "title", "price", "description", "icon", "icon1", "status"]


class Rent_OrderServiceSerializer(serializers.ModelSerializer):
    service = Rent_ServiceSerializer(read_only=True)

    class Meta:
        model = Rent_OrderService
        fields = ["order", "service", "last_reading", "current_reading"]


class Rent_OrderSerializer(serializers.ModelSerializer):
    services = Rent_OrderServiceSerializer(source='rent_orderservice_set', many=True, read_only=True)

    class Meta:
        model = Rent_Order
        fields = ["pk", "order_date", "address", "status", "total_amount", "formation_date", "completion_date", "moderator", "services"]
