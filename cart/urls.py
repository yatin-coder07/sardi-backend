from django.urls import path
from .views import (
    GetCartView,
    AddToCartView,
    RemoveCartItemView,
    UpdateCartItemView,
    CheckoutView,
)


urlpatterns = [

    # 🛒 Get all cart items
    path("", GetCartView.as_view(), name="get-cart"),

    # ➕ Add to cart
    path("add/", AddToCartView.as_view(), name="add-to-cart"),

    # ❌ Remove item
    path("remove/<int:pk>/", RemoveCartItemView.as_view(), name="remove-cart-item"),

    # 🔄 Update quantity
    path("update/<int:pk>/", UpdateCartItemView.as_view(), name="update-cart-item"),

    # 💳 Checkout → create order
    path("checkout/", CheckoutView.as_view(), name="checkout"),

]