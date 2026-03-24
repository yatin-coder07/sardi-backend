from django.core.mail import EmailMultiAlternatives
from django.conf import settings


def send_order_emails(order):
    user = order.user

    # 🧾 Build items list
    items_html = ""
    for item in order.items.all():
        items_html += f"""
        <li>{item.product.product_name} × {item.quantity} — ₹{item.price}</li>
        """

    # =========================
    # ✅ EMAIL TO CUSTOMER
    # =========================
    subject_user = f"Your Order #{order.id} Has been Confirmed 🛍️"

    html_user = f"""
    <h2>Thanks for your order, {user.username} 🎉</h2>

    <p><b>Order ID:</b> {order.id}</p>
    <p><b>Total:</b> ₹{order.total_amount}</p>

    <h3>Items:</h3>
    <ul>{items_html}</ul>

    <p>We’ll notify you once it's shipped 🚚</p>

    <br/>
    <p>— Team Sardi ❤️</p>
    """

    msg_user = EmailMultiAlternatives(
        subject_user,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    msg_user.attach_alternative(html_user, "text/html")
    msg_user.send()

    # =========================
    # ✅ EMAIL TO ADMIN
    # =========================
    subject_admin = f"🚨 New Order #{order.id}"

    html_admin = f"""
    <h2>New Order Received 🚨</h2>

    <p><b>User:</b> {user.email}</p>
    <p><b>Order ID:</b> {order.id}</p>
    <p><b>Total:</b> ₹{order.total_amount}</p>

    <h3>Items:</h3>
    <ul>{items_html}</ul>
    """

    msg_admin = EmailMultiAlternatives(
        subject_admin,
        "",
        settings.DEFAULT_FROM_EMAIL,
        [settings.ADMIN_EMAIL],
    )
    msg_admin.attach_alternative(html_admin, "text/html")
    msg_admin.send()