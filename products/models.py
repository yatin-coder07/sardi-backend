from django.db import models


class Product(models.Model):

    product_name = models.CharField(max_length=255)

    price = models.DecimalField(max_digits=10, decimal_places=2)

    product_description = models.TextField()

    product_availability = models.CharField(max_length=30)

    # ✅ NEW FIELDS
    material_type = models.CharField(max_length=100)
    sleeves_type = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.URLField()

    def __str__(self):
        return f"Image for {self.product.product_name}"