from .utils import get_cart

def cart_context(request):
    cart = get_cart(request)
    cart_total = cart.total_price() if cart else 0
    cart_quantity = cart.total_quantity() if cart else 0
    
    return {
        'cart': cart,
        'cart_total': cart_total,
        'cart_quantity': cart_quantity,
    }