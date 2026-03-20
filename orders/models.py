from django.db import models
from django.conf import settings
from products.models import Product
import uuid



class Order(models.Model):

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        
        ("DELIVERED", "Delivered"),
        ("CANCELLED", "Cancelled"),
        ("FAILED", "Failed"),
         ("OUT_FOR_DELIVERY", "Out for Delivery"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)

    address = models.TextField()
    secondary_address = models.TextField(blank=True, null=True)
    landmark = models.CharField(max_length=255, blank=True, null=True)

    # ✅ NEW FIELDS
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    order_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)

    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.TextField(blank=True, null=True)

    is_paid = models.BooleanField(default=False)
    order_number = models.CharField(max_length=20, unique=True)
    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.id} - {self.name}"

class OrderItem(models.Model):

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")

    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity}"