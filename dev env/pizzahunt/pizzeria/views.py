from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import *
from .forms import FeedbackForm, OrderForm
from .utils import *

class HomeView(TemplateView):
    template_name = 'pizzeria/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['popular_pizzas'] = Pizza.objects.filter(is_popular=True)[:8]
        context['new_pizzas'] = Pizza.objects.filter(is_new=True)[:4]
        context['combos'] = Combo.objects.all()[:4]
        context['promotions'] = Promotion.objects.filter(is_active=True)[:3]
        return context

class AboutView(TemplateView):
    template_name = 'pizzeria/about.html'

class MenuView(ListView):
    model = Pizza
    template_name = 'pizzeria/menu.html'
    context_object_name = 'pizzas'
    
    def get_queryset(self):
        queryset = super().get_queryset()
        category = self.request.GET.get('category')
        sort = self.request.GET.get('sort', 'popular')
        
        # Фильтрация по категории
        if category and category != 'all':
            if category == 'meat':
                queryset = queryset.filter(~Q(is_vegetarian=True))
            elif category == 'vegetarian':
                queryset = queryset.filter(is_vegetarian=True)
            elif category == 'spicy':
                queryset = queryset.filter(is_spicy=True)
            elif category == 'cheese':
                from .models import Category
                try:
                    cheese_category = Category.objects.filter(name__icontains='сыр').first()
                    if cheese_category:
                        queryset = queryset.filter(category=cheese_category)
                    else:
                        queryset = queryset.filter(
                            Q(name__icontains='сыр') | 
                            Q(description__icontains='сыр')
                        )
                except:
                    queryset = queryset.filter(name__icontains='сыр')
            elif category == 'special':
                queryset = queryset.filter(Q(is_popular=True) | Q(is_new=True))
        
        # Сортировка
        if sort == 'price-asc':
            queryset = queryset.order_by('price_30')
        elif sort == 'price-desc':
            queryset = queryset.order_by('-price_30')
        elif sort == 'name':
            queryset = queryset.order_by('name')
        else:  
            queryset = queryset.order_by('-is_popular', 'order')
        
        return queryset

class FeedbackView(CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'pizzeria/feedback.html'
    success_url = reverse_lazy('feedback')
    
    def form_valid(self, form):
        messages.success(self.request, 'Спасибо за ваше сообщение! Мы ответим вам в ближайшее время.')
        return super().form_valid(form)

# Корзина и заказы
def cart_view(request):
    cart = get_cart(request)
    cart_items = cart.items.all() if cart else []
    
    return render(request, 'pizzeria/cart.html', {
        'cart': cart,
        'cart_items': cart_items,
    })

def add_to_cart_view(request):
    if request.method == 'POST':
        item_type = request.POST.get('item_type')
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        if item_type == 'pizza':
            size = request.POST.get('size', '30')
            success, message = add_to_cart(request, 'pizza', item_id, size, quantity)
        elif item_type == 'combo':
            success, message = add_to_cart(request, 'combo', item_id, quantity=quantity)
        else:
            success, message = False, "Неизвестный тип товара"
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = get_cart(request)
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_quantity': cart.total_quantity() if cart else 0,
                'cart_total': float(cart.total_price()) if cart else 0,
            })
        else:
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    return redirect('home')

def update_cart_view(request):
    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        
        success, message = update_cart_item(request, item_id, quantity)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            cart = get_cart(request)
            item = None
            if success:
                try:
                    item = CartItem.objects.get(id=item_id)
                except CartItem.DoesNotExist:
                    pass
            
            return JsonResponse({
                'success': success,
                'message': message,
                'cart_quantity': cart.total_quantity() if cart else 0,
                'cart_total': float(cart.total_price()) if cart else 0,
                'item_total': float(item.total_price()) if item else 0,
            })
        else:
            if success:
                messages.success(request, message)
            else:
                messages.error(request, message)
            return redirect('cart')
    
    return redirect('cart')

def remove_from_cart_view(request, item_id):
    success, message = remove_from_cart(request, item_id)
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        cart = get_cart(request)
        return JsonResponse({
            'success': success,
            'message': message,
            'cart_quantity': cart.total_quantity() if cart else 0,
            'cart_total': float(cart.total_price()) if cart else 0,
        })
    else:
        if success:
            messages.success(request, message)
        else:
            messages.error(request, message)
        return redirect('cart')

def clear_cart_view(request):
    success, message = clear_cart(request)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('cart')

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'pizzeria/order.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart = get_cart(self.request)
        context['cart'] = cart
        context['cart_items'] = cart.items.all() if cart else []
        return context
    
    def form_valid(self, form):
        cart = get_cart(self.request)
        
        if not cart or cart.items.count() == 0:
            messages.error(self.request, 'Ваша корзина пуста!')
            return redirect('cart')
        
        order = form.save(commit=False)
        order.cart = cart
        order.total_price = cart.total_price()
        order.save()
        

        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                item_type=cart_item.item_type,
                item_name=cart_item.get_name(),
                size=cart_item.size if cart_item.item_type == 'pizza' else '',
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price(),
                total_price=cart_item.total_price()
            )
        

        cart.items.all().delete()

        self.request.session['last_order_id'] = order.id
        
        return redirect('order_success')

def order_success(request):
    order_id = request.session.get('last_order_id')
    order = None
        
    if order_id:
        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            pass
        

    if 'last_order_id' in request.session:
        del request.session['last_order_id']
        
    return render(request, 'pizzeria/order_success.html', {
        'order': order,
    })

def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
        
    cart = get_cart(request)
    if order.cart != cart:
        messages.error(request, 'У вас нет доступа к этому заказу.')
        return redirect('home')
        
    return render(request, 'pizzeria/order_detail.html', {
        'order': order,
    })