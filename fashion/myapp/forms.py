from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Product, CustomUser

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    mobile = forms.CharField(max_length=15, required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = [
            'username', 
            'first_name',
            'last_name',
            'email',
            'mobile',
            'password1',
            'password2',
        ]

class ProfileUpdateForm(forms.ModelForm):
    """
    Updates user profile basic details (excluding address fields).
    """
    class Meta:
        model = User
        fields = [
            'first_name', 
            'last_name', 
            'email', 
            'mobile'
        ]

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['name', 'description', 'category', 'price', 'image', 'stock', 'available']

class AddressForm(forms.ModelForm):
    """
    Updates only the address information for the user.
    """
    class Meta:
        model = CustomUser
        fields = ['address', 'city', 'state', 'country', 'zip_code']
