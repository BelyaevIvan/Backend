from django.db import models
from datetime import datetime, timedelta


class Rent_Service(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название услуги")
    price = models.CharField(max_length=50, verbose_name="Цена")  # Цена в формате строки (например, "37 ₽/м3")
    description = models.TextField(verbose_name="Описание")
    icon = models.URLField(max_length=200, verbose_name="Иконка")
    icon1 = models.URLField(max_length=200, verbose_name="Дополнительная иконка")
    status = models.CharField(max_length=20, verbose_name="Статус услуги", default=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Услуга"
        verbose_name_plural = "Услуги"


class Rent_Order(models.Model):
    class StaTus(models.TextChoices):
        DRAFT = 'DRAFT'
        DELETED = 'DELETED'
        REJECTED = 'REJECTED'
        COMPLETED = 'COMPLETED'
        FOMED = 'FORMED'

    order_date = models.DateField(verbose_name="Дата создания")
    address = models.CharField(max_length=255, verbose_name="Адрес")
    status = models.CharField(max_length=10, choices=StaTus.choices, default=StaTus.DRAFT)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Итоговая стоимость")

    # Новые поля
    formation_date = models.DateField(verbose_name="Дата формирования", blank=True, null=True)
    completion_date = models.DateField(verbose_name="Дата завершения", blank=True, null=True)
    moderator = models.CharField(max_length=255, verbose_name="Модератор", default="Moderator1")

    def save(self, *args, **kwargs):
        # Установка значений по умолчанию для новых полей
        if not self.formation_date:
            self.formation_date = self.order_date
        if not self.completion_date:
            self.completion_date = self.order_date
        super().save(*args, **kwargs)

    def recalculate_total(self):
        total = self.rent_orderservice_set.aggregate(total=models.Sum('amount_due'))['total'] or 0
        self.total_amount = total
        self.save()

    def recalculate_total(self):
        total = sum([service.calculate_amount_due() for service in self.rent_orderservice_set.all()])
        self.total_amount = total
        self.save()

    def __str__(self):
        return f"Заявка #{self.id} - {self.address}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"


class Rent_OrderService(models.Model):
    order = models.ForeignKey(Rent_Order, on_delete=models.CASCADE, verbose_name="Заявка")
    service = models.ForeignKey(Rent_Service, on_delete=models.CASCADE, verbose_name="Услуга")
    last_reading = models.CharField(null=True, blank=True, verbose_name="Последние показания/Дата последней оплаты")
    current_reading = models.CharField(null=True, blank=True, verbose_name="Текущие показания/Дата")

    def calculate_amount_due(self):
        try:
            price = float(self.service.price.split()[0])  # Извлечение числового значения из цены
            # Для водоснабжения и электроэнергии
            if self.service.title in ["Горячее водоснабжение", "Холодное водоснабжение", "Электроэнергия"]:
                if self.current_reading and self.last_reading:
                    current_reading = float(self.current_reading)
                    last_reading = float(self.last_reading)
                    consumption = current_reading - last_reading
                    return consumption * price
            # Для остальных услуг (по месяцам)
            else:
                if self.current_reading and self.last_reading:
                    current_date = datetime.strptime(self.current_reading, '%d.%m.%Y')
                    last_date = datetime.strptime(self.last_reading, '%d.%m.%Y')
                    month_diff = (current_date.year - last_date.year) * 12 + (current_date.month - last_date.month)
                    if month_diff >= 0:
                        return month_diff * price
        except ValueError:
            return 0
        return 0
    
    def save(self, *args, **kwargs):

        
        # Получаем предыдущие показания и дату для этой услуги по адресу
        last_order_service = (
            Rent_OrderService.objects
            .filter(
                order__address=self.order.address,
                service=self.service,
                order__status__in=[status for status in Rent_Order.StaTus if status not in [Rent_Order.StaTus.DRAFT, Rent_Order.StaTus.DELETED]]
            )
            .order_by('-order__order_date')  # Сортируем по дате заявки
            .first()
        )

        current_date_str = datetime.now().strftime('%d.%m.%Y')  # Текущая дата в формате строка
        if last_order_service:
            # Если есть предыдущая заявка
            self.last_reading = last_order_service.current_reading
        else:
            # Если предыдущих заявок нет
            if self.service.title in ["Горячее водоснабжение", "Холодное водоснабжение", "Электроэнергия"]:
                self.last_reading = '0'  # Установить 0 для водоснабжения и электроэнергии
            else:
                # Для остальных услуг устанавливаем на один месяц назад
                one_month_ago = self.order.order_date - timedelta(days=30)
                self.last_reading = one_month_ago.strftime('%d.%m.%Y')

        if self.service.title not in ["Горячее водоснабжение", "Холодное водоснабжение", "Электроэнергия"]:
            self.current_reading = self.order.order_date.strftime('%d.%m.%Y')  # Устанавливаем текущую дату в поле current_reading

        # # Если current_reading пусто, устанавливаем его в значение last_reading
        # if not self.current_reading:
        #     self.current_reading = self.last_reading
            
        try:
            price = float(self.service.price.split()[0])  # Извлечение числового значения цены из строки (например, "37 ₽/м3")

            # Для услуг водоснабжения и электроэнергии
            if self.service.title in ["Горячее водоснабжение", "Холодное водоснабжение", "Электроэнергия"]:
                if self.current_reading and self.last_reading:
                    current_reading = float(self.current_reading)
                    last_reading = float(self.last_reading)
                    consumption = current_reading - last_reading
                    self.amount_due = consumption * price

            # Для остальных услуг (по месяцам)
            else:
                if self.current_reading and self.last_reading:
                    # Преобразование строкового формата даты "20.09.2024" в объект datetime
                    current_date = datetime.strptime(self.current_reading, '%d.%m.%Y')
                    last_date = datetime.strptime(self.last_reading, '%d.%m.%Y')

                    # Разница в месяцах
                    month_diff = (current_date.year - last_date.year) * 12 + (current_date.month - last_date.month)
                    
                    if month_diff >= 0:
                        self.amount_due = month_diff * price

        except ValueError:
            # Обработка случая, если данные некорректны (например, если показания не числа или даты)
            self.amount_due = 0

        super().save(*args, **kwargs)

        # Пересчет стоимости заявки
        self.order.recalculate_total()

    def __str__(self):
        return f"{self.service.title} для Заявки #{self.order.id}"

    class Meta:
        verbose_name = "Услуга заявки"
        verbose_name_plural = "Услуги заявок"

        constraints = [
        models.UniqueConstraint(fields=['order', 'service'], name='unique_order_service')
    ]
