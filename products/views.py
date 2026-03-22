from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q
from rest_framework.permissions import AllowAny, IsAuthenticated

from .models import Product, ProductImage, Review ,ReviewImage
from .serializers import ProductSerializer, ReviewSerializer

from utils.supabase import upload_product_image


# =========================
# GET all products
# =========================
class ProductListView(APIView):
  
    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request):

        query = request.GET.get("search", "")
        collection = request.GET.get("collection")  # ✅ NEW FILTER

        products = Product.objects.all()

        if query:
            products = products.filter(
                Q(product_name__icontains=query) |
                Q(product_description__icontains=query)
            )

        if collection:
            products = products.filter(collection=collection)

        serializer = ProductSerializer(products, many=True)

        return Response(serializer.data)


# =========================
# GET single product
# =========================
class ProductDetailView(APIView):

    permission_classes = [AllowAny]
    authentication_classes = []

    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        serializer = ProductSerializer(product)
        return Response(serializer.data)


# =========================
# CREATE product
# =========================
class ProductCreateView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):

        product = Product.objects.create(
            product_name=request.data.get("product_name"),
            price=request.data.get("price"),
            product_description=request.data.get("product_description"),
            product_availability=request.data.get("product_availability"),

            # ✅ NEW FIELDS SUPPORT
            material_type=request.data.get("material_type"),
            sleeves_type=request.data.get("sleeves_type"),
            collection=request.data.get("collection", "all"),
        )

        images = request.FILES.getlist("images")

        for img in images:
            image_url = upload_product_image(img , "product_image")

            ProductImage.objects.create(
                product=product,
                image=image_url
            )

        return Response({"message": "Product created"})


# =========================
# UPDATE product
# =========================
class ProductUpdateView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def put(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        data = request.data.copy()

        image = request.FILES.get("product_image")

        if image:
            image_url = upload_product_image(image)
            data["product_image"] = image_url

        serializer = ProductSerializer(product, data=data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)

        return Response(serializer.errors, status=400)


# =========================
# DELETE product
# =========================
class ProductDeleteView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        product.delete()

        return Response({"message": "Product deleted"})


# =====================================================
# ⭐ ADD REVIEW (MULTIPLE REVIEWS ALLOWED PER USER)
# =====================================================
class AddReviewView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        rating = request.data.get("rating")
        comment = request.data.get("comment")

        if not rating:
            return Response({"error": "Rating is required"}, status=400)

        try:
            rating = int(rating)
        except:
            return Response({"error": "Rating must be a number"}, status=400)

        if rating < 1 or rating > 5:
            return Response({"error": "Rating must be between 1 and 5"}, status=400)

        # ✅ CREATE REVIEW
        review = Review.objects.create(
            product=product,
            user=request.user,
            rating=rating,
            comment=comment
        )

        # =========================
        # ✅ HANDLE MULTIPLE IMAGES
        # =========================
        images = request.FILES.getlist("images")

        for img in images:
            image_url = upload_product_image(img, "review_image")

            ReviewImage.objects.create(
                review=review,
                image=image_url
            )

        return Response({
            "message": "Review added successfully",
            "review_id": review.id
        })
# =========================
# GET ALL REVIEWS OF PRODUCT
# =========================
class ProductReviewListView(APIView):

    permission_classes = [AllowAny]

    def get(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        reviews = product.reviews.all().order_by("-created_at")

        serializer = ReviewSerializer(reviews, many=True)

        return Response(serializer.data)


# =========================
# DELETE REVIEW (ONLY OWNER)
# =========================
class DeleteReviewView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, review_id):

        try:
            review = Review.objects.get(id=review_id)
        except Review.DoesNotExist:
            return Response({"error": "Review not found"}, status=404)

        if review.user != request.user:
            return Response({"error": "Not allowed"}, status=403)

        review.delete()

        return Response({"message": "Review deleted"})