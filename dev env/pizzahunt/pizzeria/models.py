from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Pizza(models.Model):
    SIZE_CHOICES = [
        ('30', '30 см'),
        ('35', '35 см'),
        ('40', '40 см'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название пиццы")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL")
    description = models.TextField(verbose_name="Описание")
    ingredients = models.TextField(verbose_name="Ингредиенты")
    price_30 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена 30 см")
    price_35 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена 35 см")
    price_40 = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена 40 см")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='pizzas', verbose_name="Категория")
    is_popular = models.BooleanField(default=False, verbose_name="Популярная")
    is_new = models.BooleanField(default=False, verbose_name="Новинка")
    is_spicy = models.BooleanField(default=False, verbose_name="Острая")
    is_vegetarian = models.BooleanField(default=False, verbose_name="Вегетарианская")
    image_url = models.URLField(blank=True, verbose_name="URL изображения")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Пицца"
        verbose_name_plural = "Пиццы"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name
    
    def get_price_by_size(self, size):
        if size == '30':
            return self.price_30
        elif size == '35':
            return self.price_35
        elif size == '40':
            return self.price_40
        return self.price_30

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    session_key = models.CharField(max_length=40, null=True, blank=True, verbose_name="Ключ сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
    
    def __str__(self):
        if self.user:
            return f"Корзина пользователя {self.user.username}"
        return f"Корзина (сессия: {self.session_key})"
    
    def total_price(self):
        return sum(item.total_price() for item in self.items.all())
    
    def total_quantity(self):
        return sum(item.quantity for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    pizza = models.ForeignKey(Pizza, on_delete=models.CASCADE, verbose_name="Пицца")
    size = models.CharField(max_length=10, choices=Pizza.SIZE_CHOICES, default='30', verbose_name="Размер")
    quantity = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="Количество")
    added_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ['cart', 'pizza', 'size']
    
    def __str__(self):
        return f"{self.pizza.name} ({self.size}) - {self.quantity} шт."
    
    def unit_price(self):
        return self.pizza.get_price_by_size(self.size)
    
    def total_price(self):
        return self.unit_price() * self.quantity

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('confirmed', 'Подтвержден'),
        ('preparing', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    PAYMENT_CHOICES = [
        ('cash', 'Наличными при получении'),
        ('card_online', 'Картой онлайн'),
        ('card_courier', 'Картой курьеру'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email", blank=True)
    address = models.TextField(verbose_name="Адрес доставки")
    comment = models.TextField(blank=True, verbose_name="Комментарий к заказу")
    
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Корзина")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cash', verbose_name="Способ оплаты")
    payment_status = models.BooleanField(default=False, verbose_name="Оплачен")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.name} ({self.get_status_display()})"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    pizza_name = models.CharField(max_length=200, verbose_name="Название пиццы")
    size = models.CharField(max_length=10, verbose_name="Размер")
    quantity = models.PositiveIntegerField(verbose_name="Количество")
    unit_price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена за единицу")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая цена")
    
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
    
    def __str__(self):
        return f"{self.pizza_name} ({self.size}) - {self.quantity} шт."

class Combo(models.Model):
    name = models.CharField(max_length=200, verbose_name="Название комбо")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    image = models.ImageField(upload_to='combos/', verbose_name="Изображение")
    includes = models.TextField(verbose_name="Что входит")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Комбо"
        verbose_name_plural = "Комбо"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Promotion(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    description = models.TextField(verbose_name="Описание")
    image = models.ImageField(upload_to='promotions/', verbose_name="Изображение")
    end_date = models.DateTimeField(verbose_name="Дата окончания")
    is_active = models.BooleanField(default=True, verbose_name="Активна")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    
    class Meta:
        verbose_name = "Акция"
        verbose_name_plural = "Акции"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.title

class Feedback(models.Model):
    SUBJECT_CHOICES = [
        ('complaint', 'Жалоба'),
        ('suggestion', 'Предложение'),
        ('question', 'Вопрос'),
        ('delivery', 'Доставка'),
        ('cooperation', 'Сотрудничество'),
        ('other', 'Другое'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Имя")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name="Тема")
    message = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата отправки")
    is_processed = models.BooleanField(default=False, verbose_name="Обработано")
    
    class Meta:
        verbose_name = "Обратная связь"
        verbose_name_plural = "Обратная связь"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} - {self.get_subject_display()}"
