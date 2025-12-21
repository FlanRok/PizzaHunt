from .models import Cart, CartItem

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

def add_to_cart(request, item_type, item_id, size='30', quantity=1):
    """Добавить товар в корзину"""
    from .models import Pizza, Combo, CartItem
    
    cart = get_cart(request)
    
    try:
        if item_type == 'pizza':
            item = Pizza.objects.get(id=item_id)

            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='pizza',
                pizza=item,
                size=size,
                defaults={'quantity': quantity}
            )
            
            item_name = item.name
            
        elif item_type == 'combo':
            item = Combo.objects.get(id=item_id)
            
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                item_type='combo',
                combo=item,
                defaults={'quantity': quantity}
            )
            
            item_name = item.name
        else:
            return False, "Неизвестный тип товара"
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        return True, f"{item_name} добавлен(о) в корзину"
    
    except (Pizza.DoesNotExist, Combo.DoesNotExist):
        return False, "Товар не найден"
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