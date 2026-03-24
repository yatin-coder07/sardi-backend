from django.urls import path
from .views import (
    CreateOrderView,
    VerifyPaymentView,
    MyOrdersView, CancelOrderView,AdminOrdersView, WeeklyAnalyticsView
)

urlpatterns = [

    # 🧾 Create order (optional if using cart checkout)
    path("create/", CreateOrderView.as_view(), name="create-order"),

    # 💳 Verify Razorpay payment
    path("verify-payment/", VerifyPaymentView.as_view(), name="verify-payment"),

    # 📦 User orders
    path("my-orders/", MyOrdersView.as_view(), name="my-orders"),
    path("my-orders/delete/<int:order_id>/", MyOrdersView.as_view()),
     path("cancel/<int:order_id>/", CancelOrderView.as_view()),
      path("admin/orders/", AdminOrdersView.as_view()),
    path("admin/orders/<int:order_id>/", AdminOrdersView.as_view()),
    path("admin/analytics/", WeeklyAnalyticsView.as_view()),
]