from .models import Cart

def cart_item_count(request):
    if request.user.is_authenticated:
        try:
            count = request.user.cart.items.count()
        except Cart.DoesNotExist:
            count = 0
    else:
        count = 0
    return {'cart_item_count': count}
