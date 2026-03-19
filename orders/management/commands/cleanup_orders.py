from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from orders.models import Order


class Command(BaseCommand):   # ✅ THIS LINE IS CRITICAL
    help = "Delete old completed/failed/cancelled orders"

    def handle(self, *args, **kwargs):
        threshold_date = timezone.now() - timedelta(days=7)

        orders = Order.objects.filter(
            order_status__in=["CANCELLED", "DELIVERED", "FAILED"],
            created_at__lt=threshold_date
        )

        count = orders.count()
        orders.delete()

        self.stdout.write(self.style.SUCCESS(f"Deleted {count} old orders"))