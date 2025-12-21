from .models import Cart, CartItem
from django.contrib.sessions.models import Session
from django.utils import timezone

def get_cart(request):
    """Получить или создать корзину для пользователя/сессии"""
    cart = None
    
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)

    else:
        session_key = request.session.session_key
        if not session_key:
            request.session.create()
            session_key = request.session.session_key
        
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    
    return cart

def add_to_cart(request, pizza_id, size='30', quantity=1):
    """Добавить пиццу в корзину"""
    from .models import Pizza
    
    cart = get_cart(request)
    
    try:
        pizza = Pizza.objects.get(id=pizza_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            pizza=pizza,
            size=size,
            defaults={'quantity': quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return True, "Товар добавлен в корзину"
    except Pizza.DoesNotExist:
        return False, "Пицца не найдена"
    except Exception as e:
        return False, f"Ошибка: {str(e)}"

def update_cart_item(request, item_id, quantity):
    """Обновить количество товара в корзине"""
    try:
        cart_item = CartItem.objects.get(id=item_id)

        cart = get_cart(request)
        if cart_item.cart != cart:
            return False, "Этот товар не в вашей корзине"
        
        if quantity <= 0:
            cart_item.delete()
            return True, "Товар удален из корзины"
        else:
            cart_item.quantity = quantity
            cart_item.save()
            return True, "Количество обновлено"
    except CartItem.DoesNotExist:
        return False, "Элемент корзины не найден"

def remove_from_cart(request, item_id):
    """Удалить товар из корзины"""
    try:
        cart_item = CartItem.objects.get(id=item_id)
  
        cart = get_cart(request)
        if cart_item.cart != cart:
            return False, "Этот товар не в вашей корзине"
        
        cart_item.delete()
        return True, "Товар удален из корзины"
    except CartItem.DoesNotExist:
        return False, "Элемент корзины не найден"

def clear_cart(request):
    """Очистить корзину"""
    cart = get_cart(request)
    cart.items.all().delete()
    return True, "Корзина очищена"