from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from .models import Product, CustomUser,Review

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
            'address',  # Assuming address is a field in CustomUser
            'city',     # Assuming city is a field in CustomUser
        ]


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
  
        fields = [
            'first_name', 
            'last_name', 
            'email',
            'mobile',           # Correct field name
            
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
        fields = ['address', 'city', 'state', 'country', 'zip_code','first_name', 'last_name', ]

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        # The user only needs to submit a rating and a comment
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(
                choices=[('1', '1'), ('2', '2'), ('3', '3'), ('4', '4'), ('5', '5')],
                attrs={'class': 'star-rating'} # Optional class for styling
            ),
            'comment': forms.Textarea(
                attrs={'rows': 4, 'placeholder': 'Write your review here...'}
            ),
        }