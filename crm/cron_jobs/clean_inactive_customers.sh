#!/bin/bash
cd "$(dirname "$0")/../.."
deleted_count=$(python manage.py shell -c "
from crm.models import Customer, Order
from django.utils import timezone
from datetime import timedelta
one_year_ago = timezone.now() - timedelta(days=365)
inactive_customers = Customer.objects.exclude(orders__order_date__gte=one_year_ago)
count = inactive_customers.count()
inactive_customers.delete()
print(count)
")
echo "$(date): Deleted $deleted_count inactive customers" >> /tmp/customer_cleanup_log.txt