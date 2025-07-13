from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
app_name = 'myapp'

urlpatterns = [
    path('', views.home, name='home'),
    path('home', views.home, name='home'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/apply-coupon/', views.apply_coupon, name='apply_coupon'),
    path('product_detail/<int:pk>/', views.product_detail, name='product_detail'),
    path('register/', views.register, name='register'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('contact/', views.contact, name='contact'),
    path('review/add/<int:product_id>/', views.add_review, name='add_review'),
    path('accounts/', views.account, name='accounts'),
    path('checkout/', views.checkout, name='checkout'),
    path('products/', views.products, name='products'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('upload-product/', views.product_upload, name='product_upload'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path("confirm_payment/<str:pk>", views.confirm_payment, name="add"),
    path('password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html'
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]

# Custom 404 handler
handler404 = 'myapp.views.custom_404'