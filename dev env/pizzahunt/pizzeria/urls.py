from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    path('order/', views.OrderCreateView.as_view(), name='order'),
    path('order/success/', views.order_success, name='order_success'),
]