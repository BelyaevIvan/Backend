from django.shortcuts import render, get_object_or_404, redirect
from .models import Rent_Service, Rent_Order, Rent_OrderService
from django.db.models import Q
from django.utils import timezone
from django.db import connection

# Главная страница с услугами, включая поиск по названию
def hello(request):
    query = request.GET.get('rent_title')  # Получаем параметр поиска из запроса
    if query:
        # Фильтруем услуги по началу названия
        filtered_services = Rent_Service.objects.filter(title__icontains=query)
    else:
        # Если запроса нет, показываем все услуги
        filtered_services = Rent_Service.objects.all()
    
    # Получаем первую заявку со статусом DRAFT
    # draft_order = Order.objects.filter(status='DRAFT').first()  # Измените на .first() для получения первой заявки
    # draft_order_id = draft_order.id if draft_order else None  # Получаем id заявки, если она существует
    draft_order, created = Rent_Order.objects.get_or_create(status='DRAFT', defaults={
        'order_date': timezone.now(),
        'address': '',  # Оставляем пустым, как указано
    })

    draft_order_id = draft_order.id if draft_order else None  # Получаем id заявки, если она существует
    
    # Считаем количество услуг в заявке со статусом DRAFT
    service_count = Rent_OrderService.objects.filter(order=draft_order).count()

    added_services = []
    if draft_order:
        added_services = Rent_OrderService.objects.filter(order=draft_order).values_list('service_id', flat=True)
    
    # Если это POST-запрос, обрабатываем добавление услуги
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        if service_id:
            service = get_object_or_404(Rent_Service, id=service_id)
            
            # Проверяем, была ли услуга уже добавлена в заявку
            if not Rent_OrderService.objects.filter(order=draft_order, service=service).exists():
                Rent_OrderService.objects.create(order=draft_order, service=service)

            # После добавления услуги можно снова перенаправить на ту же страницу
            return redirect('services_search')

    # Получаем список добавленных услуг в заявку, если она существует
    
    return render(request, 'index.html', 
                  {'data': {
                      'page_name': 'Услуги', 
                      'services': filtered_services, 
                      'order_id': draft_order_id,
                      'added_services': added_services,
                      'service_count': service_count
                    }})


# Страница с подробной информацией об услуге
def GetService(request, service_id):
    service = get_object_or_404(Rent_Service, id=service_id)
    # Получаем первую заявку со статусом DRAFT
    draft_order = Rent_Order.objects.filter(status='DRAFT').first()  # Измените на .first() для получения первой заявки
    draft_order_id = draft_order.id if draft_order else None  # Получаем id заявки, если она существует

    # Считаем количество услуг в заявке со статусом DRAFT
    service_count = Rent_OrderService.objects.filter(order=draft_order).count()

    return render(request, 'service_detail.html', {'data': { 
                                                        'service': service,
                                                        'order_id': draft_order_id,
                                                        'service_count': service_count
                                                        }})


# Страница заказа с деталями по выбранным услугам
def GetOrder(request, order_id):
    order = get_object_or_404(Rent_Order, id=order_id)
    order_services = Rent_OrderService.objects.filter(order=order)
    
    return render(request, 'order.html', {
        'data': order_services,  # Услуги, связанные с заказом
        'order': order,            # Информация о заказе (например, адрес и дата)
        'order_id': order_id
    })

def order_detail(request, order_id):
    order = get_object_or_404(Rent_Order, id=order_id)
    services = order.rent_orderservice_set.all()  # Получаем все услуги для этой заявки

    # Получаем заявку со статусом DRAFT
    draft_order, created = Rent_Order.objects.get_or_create(status='DRAFT', defaults={
        'order_date': timezone.now(),
        'address': '',
    })

    # Считаем количество услуг в заявке со статусом DRAFT
    service_count = Rent_OrderService.objects.filter(order=draft_order).count()

    if request.method == 'POST':
        # Обработка изменения адреса
        address = request.POST.get('address')
        if address:
            order.address = address  # Обновляем адрес
            order.save()  # Сохраняем изменения в БД
            for service in services:
                service.save() 
            
        for service in services:
            current_reading_field = f'current_reading_{service.id}'
            if current_reading_field in request.POST:
                current_reading = request.POST.get(current_reading_field)
                if current_reading:
                    service.current_reading = current_reading  # Обновляем показания
                    service.save()  # Сохраняем изменения в БД
        
        # Если нажата кнопка удаления заявки
        if 'delete_order' in request.POST:
            with connection.cursor() as cursor:
                cursor.execute("UPDATE main_screen_order SET status = 'DELETED' WHERE id = %s", [order_id])
            return redirect('services_search')  # Перенаправление на главную страницу после удаления
    
    
    return render(request, 'order.html',{'data': { 
                                                'order': order,
                                                'datas': services,
                                                'order_id': order_id,
                                                'service_count': service_count
                                                }})