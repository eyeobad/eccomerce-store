import time
import requests  # Ensure this library is installed (pip install requests)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as auth_login, logout
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from decimal import Decimal
from .forms import CustomUserCreationForm, ProfileUpdateForm, ProductForm, AddressForm
from django_countries import countries
from django.views.decorators.csrf import csrf_protect 
from .utils import initiate_flutterwave_payment
from django.shortcuts import render
from django.db.models import Q
from .models import Product, Category
from django.core.paginator import Paginator

from .models import (
    CustomUser, Product, Category, Brand, SliderImage, Coupon,
    Cart, CartItem, Order,OrderItem,NewsletterSubscription
)

import requests
import time

def home(request):
    context = {
        'categories': Category.objects.order_by('?'),
        'featured_products': Product.objects.filter(featured=True),
        'recent_products': Product.objects.order_by('-created_at')[:8],
        'brands': Brand.objects.all(),
        'slider_images': SliderImage.objects.filter(active=True).order_by('order'),
    }
    
    if request.method == "POST":
        email = request.POST.get("email", "").strip()
        if email:
            # Check if email is already subscribed
            if not NewsletterSubscription.objects.filter(email=email).exists():
                NewsletterSubscription.objects.create(email=email)
                messages.success(request, "Thank you for subscribing to our newsletter!")
            else:
                messages.info(request, "You're already subscribed!")
        else:
            messages.error(request, "Please provide a valid email address.")
        # Redirect after processing the POST request to prevent resubmission
        return redirect('myapp:home')
    
    return render(request, 'index.html', context)


@login_required(login_url='myapp:login')
def cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all()
    subtotal = cart.get_subtotal()
    shipping_cost = Decimal('5.00')
    grand_total = subtotal - cart.get_discount() + shipping_cost
    context = {
        'cart': cart,
        'cart_items': cart_items,
        'cart_subtotal': subtotal,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
    }
    return render(request, 'cart.html', context)


def custom_404(request, exception):
    return render(request, '404.html', status=404)

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    related_products = Product.objects.filter(category=product.category).exclude(pk=pk)[:4]
    context = {
        'product': product,
        'related_products': related_products,
    }
    return render(request, 'product-detail.html', context)

def wishlist(request):
    return render(request, 'wishlist.html')

def contact(request):
    return render(request, 'contact.html')

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account has been created. Please log in.")
            return redirect('myapp:login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                messages.success(request, f"You are now logged in as {username}.")
                return redirect('myapp:home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.success(request, "You have successfully logged out.")
    return redirect('myapp:home')
@login_required
def account(request):
    user = request.user
    # Retrieve dynamic orders for the user, ordered by newest first.
    orders = Order.objects.filter(user=user).order_by('-created_at')
    
    if request.method == 'POST':
        if 'update_account' in request.POST:
            # Update basic account details.
            profile_form = ProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your account details have been updated!")
                return redirect('myapp:accounts')
            else:
                for field, errors in profile_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            # Reinstantiate the other forms for display.
            address_form = AddressForm(instance=user)
            password_form = PasswordChangeForm(user=user)
        
        elif 'update_address' in request.POST:
            # Update only the address fields.
            address_form = AddressForm(request.POST, instance=user)
            if address_form.is_valid():
                address_form.save()
                messages.success(request, "Your address has been updated!")
                return redirect('myapp:accounts')
            else:
                for field, errors in address_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            profile_form = ProfileUpdateForm(instance=user)
            password_form = PasswordChangeForm(user=user)
        
        elif 'change_password' in request.POST:
            password_form = PasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, user)
                messages.success(request, "Your password was successfully updated!")
                return redirect('myapp:accounts')
            else:
                for field, errors in password_form.errors.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
            profile_form = ProfileUpdateForm(instance=user)
            address_form = AddressForm(instance=user)
    else:
        profile_form = ProfileUpdateForm(instance=user)
        address_form = AddressForm(instance=user)
        password_form = PasswordChangeForm(user=user)
        
    context = {
        'profile_form': profile_form,
        'address_form': address_form,
        'password_form': password_form,
        'countries': countries,  # For dynamic country select in the template
        'user': user,
        'orders': orders,        # Dynamic orders for the logged-in user
    }
    return render(request, 'my-account.html', context)

def product_upload(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Product uploaded successfully!")
            return redirect('myapp:product_upload')
        else:
            messages.error(request, "There was an error uploading the product. Please check the form.")
    else:
        form = ProductForm()
    return render(request, 'product-upload.html', {'form': form})

from django.core.paginator import Paginator

# views.py
from django.core.paginator import Paginator
from django.shortcuts import render
from .models import Product, Category, Brand

def products(request):
    # Start with available products
    products_list = Product.objects.filter(available=True)
    
    # Filter by category if provided
    category_slug = request.GET.get('category')
    if category_slug:
        products_list = products_list.filter(category__slug=category_slug)
    
    # Filter by price range if provided
    min_price = request.GET.get('min')
    max_price = request.GET.get('max')
    if min_price and max_price:
        try:
            min_price = int(min_price)
            max_price = int(max_price)
            products_list = products_list.filter(price__gte=min_price, price__lte=max_price)
        except ValueError:
            pass  # If conversion fails, ignore the price filter
    
    # Filter by brand if provided (assuming your Product model has a ForeignKey to Brand)
    brand_id = request.GET.get('brand')
    if brand_id:
        try:
            brand_id = int(brand_id)
            products_list = products_list.filter(brand_id=brand_id)
        except ValueError:
            pass  # If conversion fails, ignore the brand filter

    # Set up pagination – for example, 10 products per page
    paginator = Paginator(products_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get additional context data
    categories = Category.objects.all()
    slider_products = Product.objects.filter(available=True)[:5]
    
    price_ranges = [
        (1000, 10000),
        (10000, 50000),
        (50000, 100000),
        (100000, 200000),
        (200000, 500000),
        (5000000, 100000000),
    ]
    
    # Get all brands to use in your sidebar or for filtering
    brands = Brand.objects.all()
    
    context = {
        'price_ranges': price_ranges,
        'brands': brands,
        'products': page_obj.object_list,  # List of products for the current page
        'page_obj': page_obj,               # Pagination object for controls
        'paginator': paginator,
        'categories': categories,
        'slider_products': slider_products,
    }
    
    return render(request, 'product-list.html', context)



@login_required(login_url='myapp:login')
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    messages.success(request, f"{product.name} was added to your cart.")
    return redirect('myapp:cart')

@login_required(login_url='myapp:login')
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    cart_item.delete()
    messages.success(request, "Item removed from your cart.")
    return redirect('myapp:cart')

@login_required
def apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code', '').strip()
        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, active=True)
            cart, created = Cart.objects.get_or_create(user=request.user)
            cart.coupon = coupon
            cart.save()
            messages.success(request, f"Coupon '{coupon.code}' applied successfully!")
        except Coupon.DoesNotExist:
            messages.error(request, "Invalid coupon code.")
    return redirect('myapp:cart')

@login_required(login_url='myapp:login')
def update_cart(request):
    if request.method == 'POST':
        cart = request.user.cart
        for item in cart.items.all():
            new_quantity = request.POST.get(f'quantity_{item.id}')
            if new_quantity:
                try:
                    new_quantity = int(new_quantity)
                    if new_quantity > 0:
                        item.quantity = new_quantity
                        item.save()
                    else:
                        item.delete()
                except ValueError:
                    continue
        messages.success(request, "Cart updated successfully!")
    return redirect('myapp:cart')

def billing_address(request):
    # Replace this with your actual billing object or dictionary.
    billing = {'country': 'NG'}  
    context = {
        'billing': billing,
        'countries': countries,
    }
    return render(request, 'checkout.html', context)

    




def search(request):
    query = request.GET.get('q', '').strip()
    product_results = Product.objects.none()
    category_results = Category.objects.none()

    if query:
        # Search products by name, description, or related category name.
        product_results = Product.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query)
        ).distinct()

        # Search categories by name or description.
        category_results = Category.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        ).distinct()

    context = {
        'query': query,
        'product_results': product_results,
        'category_results': category_results,
    }
    return render(request, 'search_results.html', context)


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    # Optionally, fetch products in this category:
    products = category.products.all()
    context = {
        'category': category,
        'products': products,
    }
    return render(request, 'category_detail.html', context)  

@login_required(login_url='myapp:')
def staff_dashboard(request):
    # Ensure only staff can access the dashboard.
    if not request.user.is_staff:
        return redirect('myapp:home')

    context = {
        'user_count': CustomUser.objects.count(),
        'product_count': Product.objects.count(),
        'category_count': Category.objects.count(),
        'brand_count': Brand.objects.count(),
        'slider_count': SliderImage.objects.count(),
        'order_count': Order.objects.count(), 
        'countries': list(countries),  
    }
    return render(request, 'staff_dashboard.html', context)


def checkout(request):
    user = request.user
    profile = user  # If you have a separate profile model, adjust accordingly
    cart, created = Cart.objects.get_or_create(user=user)
    cart_items = cart.items.all()
    subtotal = cart.get_subtotal()
    discount = cart.get_discount()
    shipping_cost = Decimal('5.00')
    grand_total = max(subtotal - discount + shipping_cost, Decimal('0.00'))

    if request.method == "POST":
        # Process the address update form
        address_form = AddressForm(request.POST, instance=profile)
        if address_form.is_valid():
            address_form.save()
            messages.success(request, "Your address has been updated.")
            return redirect('myapp:checkout')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        address_form = AddressForm(instance=profile)

    context = {
        'billing': profile,
        'shipping': profile,
        'address_form': address_form,
        'countries': countries,
        'cart_items': cart_items,
        'cart_subtotal': subtotal,
        'discount': discount,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
        'payment_methods': [{'value': 'flutterwave', 'label': 'Flutterwave'}],
        'cart': cart,
    }
    return render(request, 'checkout.html', context)

def confirm_payment(request, pk):
    """
    This view is called by Flutterwave after payment is attempted.
    It verifies the payment and dynamically creates an Order.
    
    - If the payment is verified as successful, the order status is set to "paid".
    - If not, the order status is set to "pending".
    """
    cart = get_object_or_404(Cart, id=pk)
    
    # Retrieve GET parameters from Flutterwave redirect
    tx_ref = request.GET.get('tx_ref')
    status_param = request.GET.get('status')  # Might be "successful", "pending", etc.
    transaction_id = request.GET.get('transaction_id')
    
    # Flutterwave secret key (replace with your actual secret key)
    flutterwave_secret_key = "FLWSECK_TEST-d34828dfc71e4f7a9b233a498ca8a577-X"
    verification_url = f"https://api.flutterwave.com/v3/transactions/{transaction_id}/verify"
    
    order = None
    try:
        headers = {"Authorization": f"Bearer {flutterwave_secret_key}"}
        response = requests.get(verification_url, headers=headers)
        result = response.json()
        
        if result.get("status") == "success":
            verified_status = result["data"].get("status")
            # Determine order status based on the verified status.
            order_status = "paid" if verified_status == "successful" else "pending"
                
            # Create the order with the determined status and extract the transaction_id.
            order = Order.objects.create(
                user=cart.user,
                total_amount=cart.get_total(),
                status=order_status,
                payment_method="flutterwave",
                transaction_id=transaction_id
            )
            # Create OrderItems for each item in the cart.
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price=item.product.price
                )
            # Mark the cart as completed and clear its items.
            cart.completed = True
            cart.save()
            cart.items.all().delete()
            messages.success(request, f"Payment verification complete. Your order is {order_status}.")
        else:
            messages.error(request, "Payment verification failed. Please contact support.")
    except Exception as e:
        messages.error(request, f"Error verifying payment: {e}")
    
    # Redirect to the My Account page regardless of order creation
    return redirect('myapp:accounts')
