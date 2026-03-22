from django.db import models
from django.conf import settings


class Product(models.Model):

    COLLECTION_CHOICES = (
        ("summer", "Summer"),
        ("winter", "Winter"),
        ("all", "All Season"),
    )

    product_name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    product_description = models.TextField()
    product_availability = models.CharField(max_length=30)

    material_type = models.CharField(max_length=100)
    sleeves_type = models.CharField(max_length=100)

    # ✅ NEW FIELD (FILTER)
    collection = models.CharField(
        max_length=20,
        choices=COLLECTION_CHOICES,
        default="all"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product_name

    # ⭐ OPTIONAL: average rating
    def average_rating(self):
        reviews = self.reviews.all()
        if reviews.exists():
            return round(sum([r.rating for r in reviews]) / reviews.count(), 1)
        return 0


class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.URLField()

    def __str__(self):
        return f"Image for {self.product.product_name}"


# ⭐ REVIEW MODEL (IMPORTANT)
class Review(models.Model):

    RATING_CHOICES = [
        (1, "1 Star"),
        (2, "2 Stars"),
        (3, "3 Stars"),
        (4, "4 Stars"),
        (5, "5 Stars"),
    ]

    product = models.ForeignKey(
        Product,
        related_name="reviews",
        on_delete=models.CASCADE
    )

    # ✅ Custom user model support
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    rating = models.IntegerField(choices=RATING_CHOICES)

    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"

class ReviewImage(models.Model):

    review = models.ForeignKey(
        Review,
        related_name="images",
        on_delete=models.CASCADE
    )

    image = models.URLField()

    def __str__(self):
        return f"Image for Review {self.review.id}"