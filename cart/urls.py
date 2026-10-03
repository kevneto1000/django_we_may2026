from django.urls import path
from .views import CartView, ClearCartView, CartItemView

urlpatterns = [
  path("", CartView.as_view(), name="cart"),
  path("items/<int:item_id>/", CartItemView.as_view(), name="cart-item"),
  path("clear/", ClearCartView.as_view(), name="clear-cart"),
]