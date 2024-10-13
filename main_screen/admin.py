from django.contrib import admin

# Register your models here.
from .models import Rent_Order, Rent_OrderService, Rent_Service
admin.site.register(Rent_Order)
admin.site.register(Rent_OrderService)
admin.site.register(Rent_Service)