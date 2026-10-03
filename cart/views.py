from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import CartSerializer

from products.models import Product

class CartView(APIView):
  permission_classes = [IsAuthenticated]

  def get(self, request):
    cart, created = Cart.objects.get_or_create(user=request.user)

    serializer = CartSerializer(cart)

    return Response(serializer.data)

  def post(self, request):
    product_id = request.data.get("product")
    quantity = request.data.get("quantity", 1)

    try:
      quantity = int(quantity)

      if quantity <= 0:
        return Response({"error": "Quantity must be greater than 0"}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
      return Response({"error": "Quantity must be a valid number"}, status=status.HTTP_400_BAD_REQUEST)



    try:
      product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
      return Response({"error": "Product not found"}, status=status.HTTP_404_NOT_FOUND)

    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)

    if created:
      new_quantity = quantity
    else:
      new_quantity = cart_item.quantity + quantity

    if new_quantity > product.stock:
      return Response({"error": f"Only {product.stock} units of this product are available"}, status=status.HTTP_400_BAD_REQUEST)

    cart_item.quantity = new_quantity

    cart_item.save()

    serializer = CartSerializer(cart)

    return Response(serializer.data, status=status.HTTP_201_CREATED)


class CartItemView(APIView):
  def patch(self, request, item_id):
    try:
      cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
      return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    quantity = request.data.get("quantity")

    try:
      quantity = int(quantity)

      if quantity <= 0:
        return Response({"error": "There must be at least one quantity"}, status=status.HTTP_400_BAD_REQUEST)
    except (ValueError, TypeError):
      return Response({"error": "Qauntity must be valid"}, status=status.HTTP_400_BAD_REQUEST)

    if quantity > cart_item.product.stock:
      return Response({"error": f"Only {cart_item.product.stock} units of this product are available"}, status=status.HTTP_400_BAD_REQUEST)
    cart_item.quantity = quantity
    cart_item.save()

    serializer = CartSerializer(cart_item.cart)

    return Response(serializer.data)

  def delete(self, request, item_id):
    try:
      cart_item = CartItem.objects.get(id=item_id, cart__user=request.user)
    except CartItem.DoesNotExist:
      return Response({"error": "Cart item not found"}, status=status.HTTP_404_NOT_FOUND)

    cart = cart_item.cart
    cart_item.delete()

    serializer = CartSerializer(cart)
    return Response(serializer.data)

class ClearCartView(APIView):
  permisssion_classes = [IsAuthenticated]

  def delete(self, request):
    try:
      cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
      return Response({"message": "Cart is already empty"})

    cart.items.all().delete()

    serializer = CartSerializer(cart)
    return Response(serializer.data)

