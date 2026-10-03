from django.db import models
from django.conf import settings

from products.models import Product

class Order(models.Model):
  STATUS_CHOICES = [
    {"pending", "Pending"},
    {"processing", "Processing"},
    {"shipped", "Shipped"},
    {"delivered", "Delivered"},
    {"cancelled", "Cancelled"},
  ]

  user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="orders")

  address = models.CharField(max_length=255)
  city = models.CharField(max_length=100)
  state = models.CharField(max_length=100)
  phone = models.CharField(max_length=20)

  total = models.DecimalField(max_digits=10, decimal_places=2)

  status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")

  created_at = models.DateTimeField(auto_now_add=True)

  def __str__(self):
    return f"Order #{self.id} - {self.user.email}"

class OrderItem(models.Model):
  order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
  product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
  quantity = models.PositiveIntegerField()
  price = models.DecimalField(max_digits=10, decimal_places=2)

  def __str__(self):
    return f"{self.product} x {self.quantity}"
