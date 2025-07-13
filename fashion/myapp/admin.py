from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import (
    CustomUser, Product, Category, Brand, SliderImage,
    Order, OrderItem, NewsletterSubscription,Review
)

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'mobile', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('mobile',)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('mobile',)}),
    )
    search_fields = ('username', 'first_name', 'last_name', 'email', 'mobile')
    ordering = ('username',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'icon', 'image_preview')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock', 'available', 'featured', 'category', 'created_at', 'image_preview')
    list_filter = ('available', 'featured', 'created_at', 'category')
    list_editable = ('price', 'stock', 'available', 'featured')
    search_fields = ('name', 'description')
    date_hierarchy = 'created_at'
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'image_preview')
    search_fields = ('name',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


@admin.register(SliderImage)
class SliderImageAdmin(admin.ModelAdmin):
    list_display = ('caption', 'order', 'active', 'image_preview')
    list_editable = ('order', 'active')
    search_fields = ('caption',)
    ordering = ('order',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" style="object-fit: cover; border-radius: 4px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Image"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_amount', 'created_at', 'list_products')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    search_fields = ('user__username', 'user__email', 'id')

    def list_products(self, obj):
        """
        Returns a comma-separated list of product names with their quantities.
        """
        return ", ".join(
            f"{item.product.name} (x{item.quantity})" for item in obj.items.all()
        )
    list_products.short_description = "Products Ordered"


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'date_subscribed')
    search_fields = ('email',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    # CHANGED: 'reviewer_name' is now 'user'
    list_display = ('user', 'product', 'rating', 'is_approved', 'created_at')
    
    # REMOVED: 'is_verified' which no longer exists
    list_filter = ('is_approved', 'rating')
    
    list_editable = ('is_approved',)
    
    # CHANGED: Search by the user's username instead of the old field
    search_fields = ('user__username', 'product__name', 'comment')
    
    date_hierarchy = 'created_at'
