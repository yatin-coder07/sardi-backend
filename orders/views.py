import razorpay
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from .serializers import OrderSerializer
from .models import Order, OrderItem
from products.models import Product
from rest_framework.permissions import IsAuthenticated
from rest_framework.permissions import IsAdminUser

from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
import razorpay
from django.shortcuts import get_object_or_404
from rest_framework import status

class CreateOrderView(APIView):

    def post(self, request):

        user = request.user

        data = request.data

        items = data.get("items", [])

        total_amount = 0

        order = Order.objects.create(
            user=user,
            name=data["name"],
            phone_number=data["phone_number"],
            address=data["address"],
            secondary_address=data.get("secondary_address"),
            landmark=data.get("landmark"),
            total_amount=0
        )

        for item in items:
            product = Product.objects.get(id=item["product_id"])
            quantity = item.get("quantity", 1)

            price = product.price
            total_amount += price * quantity

            OrderItem.objects.create(
                order=order,
                product=product,
                quantity=quantity,
                price=price
            )

        order.total_amount = total_amount
        order.save()

        # Razorpay order
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        payment = client.order.create({
            "amount": int(total_amount * 100),  # paise
            "currency": "INR",
            "payment_capture": 1
        })

        order.razorpay_order_id = payment["id"]
        order.save()

        # ✅ PROFESSIONAL EMAIL (ADDED ONLY THIS)
        try:
            subject = "Your Order is Confirmed 🛍️✨"
            to_email = user.email

            text_content = f"""
Hi {user},

Your order has been successfully placed!

Order ID: {order.id}
Total Amount: ₹{total_amount}

We’ll process your order shortly and keep you updated.

Thank you for shopping with us 💖
"""

            html_content = f"""
<div style="font-family: Arial, sans-serif; padding: 20px;">
  <h2 style="color:#c8a165;">Order Confirmed 🛍️✨</h2>

  <p>Hi {user},</p>

  <p>Your order has been placed successfully.</p>

  <div style="background:#f8f8f8; padding:15px; border-radius:10px; margin:15px 0;">
    <p><strong>Order ID:</strong> {order.id}</p>
    <p><strong>Total Amount:</strong> ₹{total_amount}</p>
  </div>

  <p>We’re preparing your order and will deliver it soon 🚚</p>

  <p style="margin-top:20px;">Thank you for choosing <strong>Premium Kurtis</strong> 💖</p>
</div>
"""

            email = EmailMultiAlternatives(
                subject,
                text_content,
                settings.DEFAULT_FROM_EMAIL,
                [to_email]
            )

            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)

        except Exception as e:
            print("EMAIL ERROR:", str(e))

        return Response({
            "order_id": order.id,
            "razorpay_order_id": payment["id"],
            "amount": total_amount
        })
    
class VerifyPaymentView(APIView):

    def post(self, request):

        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

        params_dict = {
            "razorpay_order_id": request.data.get("razorpay_order_id"),
            "razorpay_payment_id": request.data.get("razorpay_payment_id"),
            "razorpay_signature": request.data.get("razorpay_signature"),
        }

        try:
            client.utility.verify_payment_signature(params_dict)

            order = Order.objects.get(razorpay_order_id=params_dict["razorpay_order_id"])

            order.is_paid = True
            order.order_status = "PAID"
            order.razorpay_payment_id = params_dict["razorpay_payment_id"]
            order.razorpay_signature = params_dict["razorpay_signature"]

            order.save()

            return Response({"status": "Payment successful"})

        except:
            return Response({"status": "Payment failed"}, status=400)
    
class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def delete(self, request, order_id):
     order = get_object_or_404(Order, id=order_id, user=request.user)

     if order.order_status not in ["PENDING", "CANCELLED"]:
        return Response(
            {"error": "Only failed or cancelled orders can be deleted"},
            status=status.HTTP_400_BAD_REQUEST
        )

     order.delete()
     return Response(
        {"message": "Order deleted successfully"},
        status=status.HTTP_200_OK
    )


class CancelOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, order_id):

        try:
            order = Order.objects.get(id=order_id, user=request.user)

            # ❌ Prevent cancelling delivered orders
            if order.order_status == "DELIVERED":
                return Response(
                    {"error": "Delivered orders cannot be cancelled"},
                    status=400
                )

            # ❌ Prevent cancelling already cancelled orders
            if order.order_status == "CANCELLED":
                return Response(
                    {"error": "Order already cancelled"},
                    status=400
                )

            # ✅ Update status
            order.order_status = "CANCELLED"
            order.save()

            return Response({
                "message": "Order cancelled successfully",
                "order_id": order.id,
                "status": order.order_status
            })

        except Order.DoesNotExist:
            return Response(
                {"error": "Order not found"},
                status=404
            )
        




class AdminOrdersView(APIView):
    permission_classes = [IsAdminUser]

    # ✅ GET → Fetch Orders
    def get(self, request):

        orders = Order.objects.filter(
    Q(is_paid=True) |
    Q(order_status__in=["OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"])
).order_by("-created_at")

        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    # ✅ PATCH → Update Status
    def patch(self, request, order_id=None):

        if not order_id:
            return Response({"error": "Order ID required"}, status=400)

        try:
            order = Order.objects.get(id=order_id)

            status = request.data.get("order_status")

            allowed_status = ["PAID", "OUT_FOR_DELIVERY", "DELIVERED",]

            if status not in allowed_status:
                return Response({"error": "Invalid status"}, status=400)

            order.order_status = status
            order.save()

            return Response({
                "message": "Status updated",
                "status": order.order_status
            })

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)

    # ✅ DELETE → Remove Cancelled Orders
    def delete(self, request, order_id=None):

        if not order_id:
            return Response({"error": "Order ID required"}, status=400)

        try:
            order = Order.objects.get(id=order_id)

            # ❌ Only allow deleting cancelled orders
            if order.order_status != "CANCELLED":
                return Response({
                    "error": "Only cancelled orders can be deleted"
                }, status=400)

            order.delete()

            return Response({
                "message": "Order deleted successfully"
            })

        except Order.DoesNotExist:
            return Response({"error": "Order not found"}, status=404)