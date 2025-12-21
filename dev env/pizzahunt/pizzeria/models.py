from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

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
    image = models.ImageField(upload_to='pizzas/', verbose_name="Изображение")
    order = models.IntegerField(default=0, verbose_name="Порядок отображения")
    
    class Meta:
        verbose_name = "Пицца"
        verbose_name_plural = "Пиццы"
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

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

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('cooking', 'Готовится'),
        ('delivering', 'Доставляется'),
        ('completed', 'Завершен'),
        ('cancelled', 'Отменен'),
    ]
    
    name = models.CharField(max_length=100, verbose_name="Имя")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    email = models.EmailField(verbose_name="Email")
    address = models.TextField(verbose_name="Адрес")
    comment = models.TextField(blank=True, verbose_name="Комментарий")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Статус")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Заказ #{self.id} - {self.name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    pizza_name = models.CharField(max_length=200, verbose_name="Название пиццы")
    size = models.CharField(max_length=10, verbose_name="Размер")
    quantity = models.IntegerField(verbose_name="Количество")
    price = models.DecimalField(max_digits=8, decimal_places=2, verbose_name="Цена")
    
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказа"
    
    def __str__(self):
        return f"{self.pizza_name} ({self.size}) - {self.quantity} шт."
