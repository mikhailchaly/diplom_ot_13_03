from django.db import models

from new_user.models import User

STATE_CHOICES = (
    ('cart', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),)


class Shop(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Менеджер", null=True, blank=True )
    name = models.CharField(max_length=50, verbose_name="Магазин", unique=True)
    url = models.URLField(verbose_name='Ссылка', null=True, blank=True)
    address = models.ForeignKey("Contact", on_delete=models.CASCADE, related_name='address_shop',
                                verbose_name='Адрес')
    state = models.BooleanField(verbose_name='Статус магазина', default=True)
    product = models.ManyToManyField('Product', through='ProductInfo', related_name='shops')

    class Meta:
        verbose_name = 'Магазин'
        verbose_name_plural = 'Магазины'

    def __str__(self):
        return f"{self.name} {self.state}"


class Product(models.Model):
    name = models.CharField(max_length=50, verbose_name='Товар')
    category = models.ForeignKey("Category", on_delete=models.CASCADE, verbose_name='Категория', null=True)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, related_name='positions', blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='positions')
    product_parameters = models.ForeignKey("ProductParameter", on_delete=models.CASCADE, related_name="positions")
    external_id = models.PositiveIntegerField(verbose_name='Внешний ИД')
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    price = models.PositiveIntegerField(verbose_name="Цена", null=True)

    class Meta:
        verbose_name = 'Информация о продукте'
        verbose_name_plural = 'Информация о продуктах'
        constraints = [
            models.UniqueConstraint(fields=['product', 'shop', 'external_id'], name="unique_product")
        ]

    def __str__(self):
        return self.product.name


class Category(models.Model):
    name = models.CharField(max_length=50, verbose_name='Категория товара', unique=True)

    class Meta:
        verbose_name = 'Категория товара'
        verbose_name_plural = 'Категории товаров'

    def __str__(self):
        return self.name


class Parameter(models.Model):
    name = models.CharField(max_length=50, verbose_name='Название')

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = 'Параметры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    parameter = models.ForeignKey(Parameter, on_delete=models.CASCADE, related_name='product_parameters',
                                 verbose_name="Параметр", null=True, blank=True)
    value = models.CharField(max_length=150, verbose_name='Значение')

    class Meta:
        verbose_name = 'Параметры продукта'
        verbose_name_plural = 'Параметры продуктов'
        constraints = [
            models.UniqueConstraint(fields=['parameter'], name='unique_parameter')
        ]
    def __str__(self):
        return self.value


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders',
                             verbose_name="Получатель", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания заказа')
    update_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления заказа")
    state = models.TextField(choices=STATE_CHOICES, verbose_name='Статус заказа', default="new")
    address = models.ForeignKey("Contact", verbose_name="Адрес доставки", on_delete=models.CASCADE,
                                blank=True, null=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = 'Заказы'
        ordering = ("created_at",)

    def __str__(self):
        return f"Заказ создан {self.created_at}, статус {self.state}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="order_items",
                              verbose_name='Заказ', null=True, blank=True)
    product_info = models.ForeignKey(ProductInfo, on_delete=models.CASCADE, related_name="order_items",
                                verbose_name='Продукты', blank=True, null=True)
    quantity = models.PositiveIntegerField(verbose_name="Количество")

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = 'Заказанные позиции'


class Contact(models.Model):
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house = models.CharField(max_length=10, verbose_name='Дом', null=True, blank=True)
    structure = models.CharField(max_length=10, verbose_name='Строение', null=True, blank=True)
    apartment = models.CharField(max_length=10, verbose_name='Квартира', null=True, blank=True)
    phone = models.CharField(max_length=20, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Контакт пользователя'
        verbose_name_plural = 'Контакты пользователей'

    def __str__(self):
        return f"{self.city} {self.street} {self.apartment} {self.phone}"


