from rest_framework import viewsets, status
from rest_framework.response import Response
from django.contrib.auth.models import User
from rest_framework.permissions import IsAuthenticated
from minio import Minio
from rest_framework.views import APIView
from django.conf import settings
from .models import Rent_Service, Rent_Order, Rent_OrderService
from .serializers import Rent_ServiceSerializer, Rent_OrderSerializer
from datetime import datetime, timedelta, timezone
from .minio import add_pic  # Импортируем функцию для работы с MinIO
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import action


class RentServiceViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        services = Rent_Service.objects.all()
        draft_order = Rent_Order.objects.filter(status=Rent_Order.StaTus.DRAFT).first()
        serializer = Rent_ServiceSerializer(services, many=True)
        return Response({
            "services": serializer.data,
            "draft_order_id": draft_order.id if draft_order else None
        })

    def retrieve(self, request, pk=None):
        try:
            service = Rent_Service.objects.get(pk=pk)
            serializer = Rent_ServiceSerializer(service)
            return Response(serializer.data)
        except Rent_Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def create(self, request):
        serializer = Rent_ServiceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, pk=None):
        try:
            service = Rent_Service.objects.get(pk=pk)
            serializer = Rent_ServiceSerializer(service, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Rent_Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def destroy(self, request, pk=None):
        try:
            service = Rent_Service.objects.get(pk=pk)

            # Удаляем изображение из MinIO
            client = Minio(
                endpoint=settings.AWS_S3_ENDPOINT_URL,
                access_key=settings.AWS_ACCESS_KEY_ID,
                secret_key=settings.AWS_SECRET_ACCESS_KEY,
                secure=settings.MINIO_USE_SSL
            )
            img_obj_name = f"{service.id}.svg"  # Имя изображения, основанное на ID услуги

            # Удаляем объект из MinIO
            client.remove_object('lab3', img_obj_name)

            # Удаляем услугу из базы данных
            service.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Rent_Service.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def add_to_draft_order(self, request, pk=None):
        draft_order, created = Rent_Order.objects.get_or_create(
            status=Rent_Order.StaTus.DRAFT,
            defaults={
                "moderator": "Moderator1",  # автоматически создается
                "formation_date": datetime.now(),
                "order_date": datetime.now(),
            },
        )
        service = Rent_Service.objects.get(pk=pk)
        Rent_OrderService.objects.create(order=draft_order, service=service)
        return Response({"message": "Service added to draft order"}, status=status.HTTP_201_CREATED)

    def add_image(self, request, pk=None):
            try:
                service = Rent_Service.objects.get(pk=pk)
                image = request.FILES.get('icon')  # Получаем изображение из запроса
                if image:
                    response = add_pic(service, image)  # Используем функцию для загрузки изображения
                    return response
                return Response({"error": "Нет изображения для загрузки."}, status=status.HTTP_400_BAD_REQUEST)
            except Rent_Service.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)


class RentOrderViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def list(self, request):
        # Получение всех заявок, кроме удаленных и черновиков
        orders = Rent_Order.objects.exclude(status=Rent_Order.StaTus.DELETED).exclude(status=Rent_Order.StaTus.DRAFT)
        serializer = Rent_OrderSerializer(orders, many=True)
        return Response(serializer.data)
    
    def retrieve(self, request, pk=None):
        try:
            order = Rent_Order.objects.get(pk=pk)
            serializer = Rent_OrderSerializer(order)
            return Response(serializer.data)
        except Rent_Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def update(self, request, pk=None):
        try:
            order = Rent_Order.objects.get(pk=pk)
            serializer = Rent_OrderSerializer(order, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Rent_Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
    
    def finalize(self, request, pk=None):
        try:
            order = Rent_Order.objects.get(pk=pk)

            # Проверка на непустоту обязательных полей
            if not order.order_date or not order.address:
                return Response({"error": "Поля 'Дата создания' и 'Адрес' не могут быть пустыми."}, 
                                status=status.HTTP_400_BAD_REQUEST)

            # Подтверждение заявки создателем
            order.moderator = request.user  # Установка модератора как текущего пользователя
            order.completion_date = datetime.now()
            order.status = Rent_Order.StaTus.FOMED  # Устанавливаем статус как 'FOMED'
            
            order.save()
            return Response({"message": "Заявка успешно подтверждена и ожидает модерации."}, 
                            status=status.HTTP_200_OK)
        except Rent_Order.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    def reject(self, request, pk=None):
            try:
                order = Rent_Order.objects.get(pk=pk)
                order.moderator = request.user
                order.completion_date = datetime.now()
                order.status = Rent_Order.StaTus.REJECTED
                order.save()
                return Response({"message": "Заявка отклонена."}, status=status.HTTP_200_OK)
            except Rent_Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

    def destroy(self, request, pk=None):
            try:
                order = Rent_Order.objects.get(pk=pk)
                order.status = Rent_Order.StaTus.DELETED
                order.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except Rent_Order.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            
class RentServiceOrderViewSet(viewsets.ViewSet):
    # permission_classes = [IsAuthenticated]

    def delete_service_from_order(self, request, order_id, service_id):
        try:
            # Поиск заявки и услуги по их ID
            order_service = Rent_OrderService.objects.get(order_id=order_id, service_id=service_id)
            
            # Удаляем услугу из заявки
            order_service.delete()
            
            # Пересчитываем общую сумму заявки
            order_service.order.recalculate_total()
            
            return Response({"message": "Услуга успешно удалена из заявки."}, status=status.HTTP_204_NO_CONTENT)
        except Rent_OrderService.DoesNotExist:
            return Response({"error": "Услуга не найдена в заявке."}, status=status.HTTP_404_NOT_FOUND)
    
    def update_current_reading(self, request, order_id, service_id):
        try:
            # Поиск услуги в заявке
            order_service = Rent_OrderService.objects.get(order_id=order_id, service_id=service_id)
            
            # Обновляем поле current_reading
            new_reading = request.data.get('current_reading')
            if not new_reading:
                return Response({"error": "Поле 'current_reading' обязательно для обновления."}, status=status.HTTP_400_BAD_REQUEST)
            
            order_service.current_reading = new_reading
            order_service.save()  # Автоматический пересчет общей стоимости заявки
            
            return Response({"message": "Текущие показания успешно обновлены."}, status=status.HTTP_200_OK)
        except Rent_OrderService.DoesNotExist:
            return Response({"error": "Услуга не найдена в заявке."}, status=status.HTTP_404_NOT_FOUND)

# POST регистрация
class UserRegistrationView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        email = request.data.get('email')
        
        if not username or not password or not email:
            return Response({"error": "Все поля обязательны"}, status=status.HTTP_400_BAD_REQUEST)
        
        if User.objects.filter(username=username).exists():
            return Response({"error": "Пользователь с таким именем уже существует"}, status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.create_user(username=username, password=password, email=email)
        user.save()
        return Response({"message": "Регистрация прошла успешно"}, status=status.HTTP_201_CREATED)
    
# PUT изменение профиля (личный кабинет)

class UserProfileUpdateView(APIView):
    # permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        username = request.data.get('username', user.username)
        email = request.data.get('email', user.email)

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            return Response({"error": "Пользователь с таким именем уже существует"}, status=status.HTTP_400_BAD_REQUEST)
        
        user.username = username
        user.email = email
        user.save()
        return Response({"message": "Профиль обновлен успешно"}, status=status.HTTP_200_OK)
    
# POST аутентификация
class UserLoginView(APIView):
    # @action(detail=False, methods=['post'], url_path='login')
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response({"message": "Аутентификация прошла успешно"}, status=status.HTTP_200_OK)
        else:
            return Response({"error": "Неверные данные для входа"}, status=status.HTTP_400_BAD_REQUEST)
        # return Response({"message": "Аутентификация прошла успешно"}, status=status.HTTP_200_OK)
        
# POST деавторизация

class UserLogoutView(APIView):
    # @action(detail=False, methods=['post'], url_path='logout')
    def post(self, request):
        # logout(request)  # Удаление сессии пользователя
        return Response({"message": "Успешная деавторизация."}, status=status.HTTP_200_OK)