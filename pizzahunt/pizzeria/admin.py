from django.contrib import admin
from .models import *

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Pizza)
class PizzaAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price_30', 'price_35', 'price_40', 'is_popular', 'is_new', 'order')
    list_editable = ('order', 'is_popular', 'is_new')
    list_filter = ('category', 'is_popular', 'is_new', 'is_spicy', 'is_vegetarian')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'session_key', 'created_at', 'total_price', 'total_quantity')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('cart', 'pizza', 'size', 'quantity', 'unit_price', 'total_price')
    list_filter = ('size',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'phone', 'total_price', 'status', 'payment_method', 'payment_status', 'created_at')
    list_filter = ('status', 'payment_method', 'payment_status', 'created_at')
    search_fields = ('name', 'phone', 'email', 'address')
    readonly_fields = ('created_at', 'updated_at')
    actions = ['mark_as_confirmed', 'mark_as_completed', 'mark_as_cancelled']
    
    def mark_as_confirmed(self, request, queryset):
        queryset.update(status='confirmed')
    mark_as_confirmed.short_description = "Подтвердить выбранные заказы"
    
    def mark_as_completed(self, request, queryset):
        queryset.update(status='completed')
    mark_as_completed.short_description = "Отметить как завершенные"
    
    def mark_as_cancelled(self, request, queryset):
        queryset.update(status='cancelled')
    mark_as_cancelled.short_description = "Отменить выбранные заказы"

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'item_name', 'item_type', 'size', 'quantity', 'unit_price', 'total_price']
    list_filter = ['item_type']
    search_fields = ['item_name', 'order__id']
    readonly_fields = ['order', 'item_type', 'item_name', 'size', 'quantity', 'unit_price', 'total_price']

@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'order')
    list_editable = ('order',)

@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ('title', 'end_date', 'is_active')
    list_filter = ('is_active',)

@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'created_at', 'is_processed')
    list_filter = ('subject', 'is_processed', 'created_at')
    search_fields = ('name', 'email', 'message')
