from django.urls import path
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from . import views
from .views import (
    register_view, 
    login_view, 
    logout_view, 
    profile_view, 
    profile_edit_view, 
)

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('menu/', views.MenuView.as_view(), name='menu'),
    path('feedback/', views.FeedbackView.as_view(), name='feedback'),
    
    path('cart/', views.cart_view, name='cart'),
    path('cart/add/', views.add_to_cart_view, name='add_to_cart'),
    path('cart/update/', views.update_cart_view, name='update_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    path('cart/clear/', views.clear_cart_view, name='clear_cart'),
    
    path('order/', views.OrderCreateView.as_view(), name='order'),
    path('order/success/', views.order_success, name='order_success'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),

    path('register/', register_view, name='register'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    
    path('password-reset/', 
         auth_views.PasswordResetView.as_view(
             template_name='pizzeria/auth/password_reset.html',
             email_template_name='pizzeria/auth/password_reset_email.html',
             success_url=reverse_lazy('password_reset_done')
         ), 
         name='password_reset'),
    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(
             template_name='pizzeria/auth/password_reset_done.html'
         ), 
         name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(
             template_name='pizzeria/auth/password_reset_confirm.html',
             success_url=reverse_lazy('password_reset_complete')
         ), 
         name='password_reset_confirm'),
    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(
             template_name='pizzeria/auth/password_reset_complete.html'
         ), 
         name='password_reset_complete'),
    
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', profile_edit_view, name='profile_edit'),
     path('profile/orders/', views.order_history_view, name='order_history'),
]