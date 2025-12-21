from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, ListView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from .models import *
from .forms import FeedbackForm, OrderForm

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
        else:  # popular
            queryset = queryset.order_by('-is_popular', 'order')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        context['selected_category'] = self.request.GET.get('category', 'all')
        context['selected_sort'] = self.request.GET.get('sort', 'popular')
        return context

class FeedbackView(CreateView):
    model = Feedback
    form_class = FeedbackForm
    template_name = 'pizzeria/feedback.html'
    success_url = reverse_lazy('feedback')
    
    def form_valid(self, form):
        messages.success(self.request, 'Спасибо за ваше сообщение! Мы ответим вам в ближайшее время.')
        return super().form_valid(form)

class OrderCreateView(CreateView):
    model = Order
    form_class = OrderForm
    template_name = 'pizzeria/order.html'
    success_url = reverse_lazy('order_success')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ваш заказ принят! Мы свяжемся с вами для подтверждения.')
        return response

def order_success(request):
    return render(request, 'pizzeria/order_success.html')