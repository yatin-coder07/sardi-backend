import resend
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def send_order_emails(order):
    resend.api_key = settings.RESEND_API_KEY
    user = order.user

    items_html = ""
    items_text = ""
    for item in order.items.all():
        items_html += f"<li>{item.product.product_name} × {item.quantity} — ₹{item.price}</li>"
        items_text += f"- {item.product.product_name} × {item.quantity} — ₹{item.price}\n"

    # ✅ EMAIL TO CUSTOMER
    try:
        resend.Emails.send({
            "from": "Sardi Store <onboarding@resend.dev>",
            "to": [user.email],
            "subject": f"Your Order #{order.order_number} Has been Confirmed 🛍️",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #333;">Thanks for your order, {user.username} 🎉</h2>
                <p style="color: #666;">Your order has been confirmed and is being processed.</p>

                <hr style="border: none; border-top: 1px solid #eee;" />

                <h3 style="color: #333;">Order Details</h3>
                <table style="width: 100%; font-size: 14px; color: #444;">
                    <tr><td><b>Order Number</b></td><td>{order.order_number}</td></tr>
                    <tr><td><b>Order ID</b></td><td>{order.id}</td></tr>
                    <tr><td><b>Total Amount</b></td><td>₹{order.total_amount}</td></tr>
                    <tr><td><b>Payment Status</b></td><td style="color: green;">✅ Paid</td></tr>
                </table>

                <hr style="border: none; border-top: 1px solid #eee;" />

                <h3 style="color: #333;">Items Ordered</h3>
                <ul style="font-size: 14px; color: #444;">
                    {items_html}
                </ul>

                <hr style="border: none; border-top: 1px solid #eee;" />

                <h3 style="color: #333;">Delivery Address</h3>
                <table style="width: 100%; font-size: 14px; color: #444;">
                    <tr><td><b>Name</b></td><td>{order.name}</td></tr>
                    <tr><td><b>Phone</b></td><td>{order.phone_number}</td></tr>
                    <tr><td><b>Address</b></td><td>{order.address}</td></tr>
                    {"<tr><td><b>Secondary Address</b></td><td>" + order.secondary_address + "</td></tr>" if order.secondary_address else ""}
                    {"<tr><td><b>Landmark</b></td><td>" + order.landmark + "</td></tr>" if order.landmark else ""}
                    <tr><td><b>City</b></td><td>{order.city}</td></tr>
                    <tr><td><b>State</b></td><td>{order.state}</td></tr>
                    <tr><td><b>Pincode</b></td><td>{order.pincode}</td></tr>
                </table>

                <hr style="border: none; border-top: 1px solid #eee;" />

                <p style="color: #666; font-size: 13px;">We'll notify you once your order is shipped 🚚</p>
                <p style="color: #333;"><b>— Team Sardi ❤️</b></p>
            </div>
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
            "subject": f"🚨 New Order {order.order_number} — ₹{order.total_amount}",
            "html": f"""
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 24px; border: 1px solid #eee; border-radius: 8px;">
                <h2 style="color: #e53e3e;">🚨 New Order Received</h2>

                <h3 style="color: #333;">Order Details</h3>
                <table style="width: 100%; font-size: 14px; color: #444;">
                    <tr><td><b>Order Number</b></td><td>{order.order_number}</td></tr>
                    <tr><td><b>Order ID</b></td><td>{order.id}</td></tr>
                    <tr><td><b>Total Amount</b></td><td>₹{order.total_amount}</td></tr>
                    <tr><td><b>Razorpay Payment ID</b></td><td>{order.razorpay_payment_id}</td></tr>
                </table>

                <hr style="border: none; border-top: 1px solid #eee;" />

                <h3 style="color: #333;">Items Ordered</h3>
                <ul style="font-size: 14px; color: #444;">
                    {items_html}
                </ul>

                <hr style="border: none; border-top: 1px solid #eee;" />

                <h3 style="color: #333;">Customer Details</h3>
                <table style="width: 100%; font-size: 14px; color: #444;">
                    <tr><td><b>Username</b></td><td>{user.username}</td></tr>
                    <tr><td><b>Email</b></td><td>{user.email}</td></tr>
                    <tr><td><b>Name</b></td><td>{order.name}</td></tr>
                    <tr><td><b>Phone</b></td><td>{order.phone_number}</td></tr>
                    <tr><td><b>Address</b></td><td>{order.address}</td></tr>
                    {"<tr><td><b>Secondary Address</b></td><td>" + order.secondary_address + "</td></tr>" if order.secondary_address else ""}
                    {"<tr><td><b>Landmark</b></td><td>" + order.landmark + "</td></tr>" if order.landmark else ""}
                    <tr><td><b>City</b></td><td>{order.city}</td></tr>
                    <tr><td><b>State</b></td><td>{order.state}</td></tr>
                    <tr><td><b>Pincode</b></td><td>{order.pincode}</td></tr>
                </table>
            </div>
            """
        })
        logger.info(f"✅ Admin email sent for order {order.id}")

    except Exception as e:
        logger.error(f"❌ Admin email FAILED for order {order.id}: {str(e)}", exc_info=True)