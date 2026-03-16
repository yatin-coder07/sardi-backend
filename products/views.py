from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.db.models import Q

from .models import Product ,ProductImage
from .serializers import ProductSerializer

from utils.supabase import upload_product_image


# GET all products
class ProductListView(APIView):

  def get(self, request):

    query = request.GET.get("search", "")

    if query:
        products = Product.objects.filter(
            Q(product_name__icontains=query) |
            Q(product_description__icontains=query)
        )
    else:
        products = Product.objects.all()

    serializer = ProductSerializer(products, many=True)

    return Response(serializer.data)

class ProductCreateView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def post(self, request):

        product = Product.objects.create(
            product_name=request.data.get("product_name"),
            price=request.data.get("price"),
            product_description=request.data.get("product_description"),
            product_availability=request.data.get("product_availability")
        )

        images = request.FILES.getlist("images")

        for img in images:

            image_url = upload_product_image(img)

            ProductImage.objects.create(
                product=product,
                image=image_url
            )

        return Response({"message": "Product created"})

# UPDATE product
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



# DELETE product
class ProductDeleteView(APIView):

    permission_classes = [permissions.IsAdminUser]

    def delete(self, request, pk):

        try:
            product = Product.objects.get(pk=pk)
        except Product.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        product.delete()

        return Response({"message": "Product deleted"})