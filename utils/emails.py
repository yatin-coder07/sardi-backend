import resend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

resend.api_key = settings.RESEND_API_KEY


def send_order_emails(order):
    user = order.user

    items_html = ""
    for item in order.items.all():
        items_html += f"<li>{item.product.product_name} × {item.quantity} — ₹{item.price}</li>"

    # ✅ EMAIL TO CUSTOMER
    try:
        resend.Emails.send({
            "from": "Sardi Store <onboarding@resend.dev>",
            "to": [user.email],
            "subject": f"Your Order #{order.id} Has been Confirmed 🛍️",
            "html": f"""
                <h2>Thanks for your order, {user.username} 🎉</h2>
                <p><b>Order ID:</b> {order.id}</p>
                <p><b>Total:</b> ₹{order.total_amount}</p>
                <h3>Items:</h3>
                <ul>{items_html}</ul>
                <p>We'll notify you once it's shipped 🚚</p>
                <p>— Team Sardi ❤️</p>
            """
        })
        logger.info(f"✅ Customer email sent to {user.email} for order {order.id}")

    except Exception as e:
        logger.error(f"❌ Customer email FAILED for order {order.id}: {str(e)}", exc_info=True)

    # ✅ EMAIL TO ADMIN
    try:
        resend.Emails.send({
            "from": "Sardi Store <onboarding@resend.dev>",
            "to": [settings.ADMIN_EMAIL],
            "subject": f"🚨 New Order #{order.id}",
            "html": f"""
                <h2>New Order Received 🚨</h2>
                <p><b>User:</b> {user.email}</p>
                <p><b>Order ID:</b> {order.id}</p>
                <p><b>Total:</b> ₹{order.total_amount}</p>
                <h3>Items:</h3>
                <ul>{items_html}</ul>
            """
        })
        logger.info(f"✅ Admin email sent for order {order.id}")

    except Exception as e:
        logger.error(f"❌ Admin email FAILED for order {order.id}: {str(e)}", exc_info=True)