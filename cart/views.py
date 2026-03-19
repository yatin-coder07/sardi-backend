from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart
from orders.models import Order, OrderItem
from .serializers import CartSerializer

class GetCartView(APIView):

    def get(self, request):

        cart, created = Cart.objects.get_or_create(user=request.user)

        serializer = CartSerializer(cart)

        return Response(serializer.data)

from .models import CartItem
from products.models import Product


class AddToCartView(APIView):

    def post(self, request):

        cart, _ = Cart.objects.get_or_create(user=request.user)

        product_id = request.data.get("product_id")
        quantity = int(request.data.get("quantity", 1))

        product = Product.objects.get(id=product_id)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product
        )

        if not created:
            item.quantity += quantity
        else:
            item.quantity = quantity

        item.save()

        return Response({"message": "Added to cart"})

class RemoveCartItemView(APIView):

    def delete(self, request, pk):

        item = CartItem.objects.get(id=pk, cart__user=request.user)

        item.delete()

        return Response({"message": "Item removed"})

class UpdateCartItemView(APIView):

    def patch(self, request, pk):

        item = CartItem.objects.get(id=pk, cart__user=request.user)

        quantity = int(request.data.get("quantity", 1))

        item.quantity = quantity
        item.save()

        return Response({"message": "Cart updated"})
    



class CheckoutView(APIView):

    def post(self, request):

        cart = Cart.objects.get(user=request.user)

        order = Order.objects.create(
            user=request.user,
            name=request.data["name"],
            phone_number=request.data["phone_number"],
            address=request.data["address"],
            total_amount=0
        )

        total = 0

        for item in cart.items.all():

            total += item.product.price * item.quantity

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        order.total_amount = total
        order.save()

        cart.items.all().delete()  # 🔥 clear cart

        return Response({"message": "Order created"})