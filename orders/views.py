from django.shortcuts import render
from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer

class CreateOrderView(APIView):
  prermission_classes = [IsAuthenticated]

  @transaction.atomic
  def post(self, request):
    try:
      cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
      return Response({"error": "Cart not found"}, status=status.HTTP_404_NOT_FOUND)

    if not cart.items.exists():
      return Response({"error": "Your cart is empty"}, status=status.HTTP_400_BAD_REQUEST)
    address = request.data.get("address")
    city = request.data.get("city")
    state = request.data.get("state")
    phone = request.data.get("phone")

    if not all([address, city, state, phone]):
      return Response({"error": "All information must be required"}, status=status.HTTP_400_BAD_REQUEST)

    for cart_item in cart.items.select_related("product"):
      if cart_item.quantity > cart_item.product.stock:
        return Response({"error": f"Only {cart_item.product.stock} units of {cart_item.product.name} are available"}, status=status.HTTP_400_BAD_REQUEST)

    total = 0

    for cart_item in cart.items.select_related("product"):
      total += cart_item.product.price * cart_item.quantity

    order = Order.objects.create(
      user=request.user,
      address=address,
      city=city,
      state=state,
      phone=phone,
      total=total,
    )

    for cart_item in cart.items.select_related("product"):
      product = cart_item.product

      OrderItem.objects.create(
        order=order,
        product=product,
        quantity=cart_item.quantity,
        price=product.price,
      )

      product.stock -= cart_item.quantity
      product.save()

    cart.items.all().delete()

    serializer = OrderSerializer(order)

    return Response(serializer.data, status=status.HTTP_201_CREATED)



