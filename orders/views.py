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
from django.shortcuts import get_object_or_404
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, Count
from utils.emails import send_order_emails
import threading


class CreateOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("📥 REQUEST DATA:", request.data)

            user = request.user
            data = request.data
            items = data.get("items", [])

            total_amount = 0

            # ✅ CREATE ORDER
            order = Order.objects.create(
                user=user,
                name=data.get("name"),
                phone_number=data.get("phone_number"),
                address=data.get("address"),
                secondary_address=data.get("secondary_address"),
                landmark=data.get("landmark"),
                city=data.get("city"),        # ✅ ADDED
                state=data.get("state"),      # ✅ ADDED
                pincode=data.get("pincode"),  # ✅ ADDED
                total_amount=0,
               
            )
            print("🆕 Order created:", order.id)

            # ✅ PROCESS ITEMS
            for item in items:
                try:
                    product = Product.objects.get(id=item["product_id"])
                except Exception as e:
                    print("❌ PRODUCT ERROR:", str(e))
                    raise

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
           

            print("💰 Total amount:", total_amount)

            # ✅ RAZORPAY ORDER
            try:
                print("🔑 RAZORPAY KEY:", settings.RAZORPAY_KEY_ID)

                client = razorpay.Client(auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET
                ))

                payment = client.order.create({
                    "amount": int(total_amount * 100),
                    "currency": "INR",
                    "payment_capture": 1
                })

                print("✅ Razorpay order created:", payment)

            except Exception as e:
                print("❌ RAZORPAY ERROR:", str(e))
                import traceback
                traceback.print_exc()
                return Response(
                    {"error": f"Razorpay failed: {str(e)}"},
                    status=500
                )

            order.razorpay_order_id = payment["id"]
            order.save()

            return Response({
                "order_id": order.id,
                "razorpay_order_id": payment["id"],
                "amount": total_amount
            })

        except Exception as e:
            print("💥 FINAL ERROR:", str(e))
            import traceback
            traceback.print_exc()

            return Response(
                {"error": str(e)},
                status=500
            )


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
            send_order_emails(order)

            return Response({"status": "Payment successful"})

        except Exception as e:
            try:
                order = Order.objects.get(
                    razorpay_order_id=params_dict.get("razorpay_order_id")
                )

                order.is_paid = False
                order.order_status = "FAILED"
                order.save()

            except Order.DoesNotExist:
                pass

            return Response(
                {"status": "Payment failed"},
                status=400
            )


class MyOrdersView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user).order_by("-created_at")
        serializer = OrderSerializer(orders, many=True, context={"request": request} )
        return Response(serializer.data)

    def delete(self, request, order_id):
        order = get_object_or_404(Order, id=order_id, user=request.user)

        if order.order_status not in ["FAILED", "CANCELLED","DELIVERED"]:
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

            if order.order_status == "DELIVERED":
                return Response(
                    {"error": "Delivered orders cannot be cancelled"},
                    status=400
                )

            if order.order_status == "CANCELLED":
                return Response(
                    {"error": "Order already cancelled"},
                    status=400
                )

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

    def get(self, request):

        orders = Order.objects.filter(
            Q(is_paid=True) |
            Q(order_status__in=["OUT_FOR_DELIVERY", "DELIVERED", "CANCELLED"])
        ).order_by("-created_at")

        serializer = OrderSerializer(orders, many=True, context={"request": request} )
        return Response(serializer.data)

    def patch(self, request, order_id=None):

        if not order_id:
            return Response({"error": "Order ID required"}, status=400)

        try:
            order = Order.objects.get(id=order_id)

            status = request.data.get("order_status")

            allowed_status = ["PAID", "OUT_FOR_DELIVERY", "DELIVERED"]

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

    def delete(self, request, order_id=None):

        if not order_id:
            return Response({"error": "Order ID required"}, status=400)

        try:
            order = Order.objects.get(id=order_id)

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
        


class WeeklyAnalyticsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        today = timezone.now()
        start_week = today - timedelta(days=7)

        orders = Order.objects.filter(
            created_at__gte=start_week,
            is_paid=True
        )

        total_sales = orders.aggregate(total=Sum("total_amount"))["total"] or 0
        total_orders = orders.count()

        total_products = OrderItem.objects.filter(
            order__in=orders
        ).aggregate(total=Sum("quantity"))["total"] or 0

        # daily breakdown
        daily_data = []
        for i in range(7):
            day = start_week + timedelta(days=i)
            next_day = day + timedelta(days=1)

            day_orders = orders.filter(created_at__gte=day, created_at__lt=next_day)

            daily_sales = day_orders.aggregate(
                total=Sum("total_amount")
            )["total"] or 0

            daily_data.append({
                "day": day.strftime("%a"),
                "sales": float(daily_sales)
            })

        return Response({
            "total_sales": total_sales,
            "total_orders": total_orders,
            "total_products": total_products,
            "daily": daily_data
        })  