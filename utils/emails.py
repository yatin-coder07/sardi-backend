from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_order_emails(order):
    user = order.user

    items_html = ""
    for item in order.items.all():
        items_html += f"<li>{item.product.product_name} × {item.quantity} — ₹{item.price}</li>"

    # ✅ EMAIL TO CUSTOMER
    try:
        html_user = f"""
        <h2>Thanks for your order, {user.username} 🎉</h2>
        <p><b>Order ID:</b> {order.id}</p>
        <p><b>Total:</b> ₹{order.total_amount}</p>
        <h3>Items:</h3>
        <ul>{items_html}</ul>
        <p>We'll notify you once it's shipped 🚚</p>
        <p>— Team Sardi ❤️</p>
        """
        send_mail(
            subject=f"Your Order #{order.id} Has been Confirmed 🛍️",
            message=f"Order #{order.id} confirmed. Total: ₹{order.total_amount}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_user,
            fail_silently=False,
        )
        logger.info(f"✅ Customer email sent to {user.email} for order {order.id}")

    except Exception as e:
        logger.error(f"❌ Customer email FAILED for order {order.id}: {str(e)}", exc_info=True)

    # ✅ EMAIL TO ADMIN
    try:
        html_admin = f"""
        <h2>New Order Received 🚨</h2>
        <p><b>User:</b> {user.email}</p>
        <p><b>Order ID:</b> {order.id}</p>
        <p><b>Total:</b> ₹{order.total_amount}</p>
        <h3>Items:</h3>
        <ul>{items_html}</ul>
        """
        send_mail(
            subject=f"🚨 New Order #{order.id}",
            message=f"New order from {user.email}. Total: ₹{order.total_amount}",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            html_message=html_admin,
            fail_silently=False,
        )
        logger.info(f"✅ Admin email sent for order {order.id}")

    except Exception as e:
        logger.error(f"❌ Admin email FAILED for order {order.id}: {str(e)}", exc_info=True)