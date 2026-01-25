from datetime import timedelta, date
from django.utils import timezone
from apps.orders.models import Order


def get_db_launch_date():

    first_order = Order.objects.order_by("created_at").first()
    if first_order:
        return first_order.created_at.date()
    return timezone.now().date()


def get_date_range(filter_key=None, year=None, start_date=None, end_date=None):
   
    today = timezone.now().date()
    db_start = get_db_launch_date()

    if filter_key == "last_7_days":
        return today - timedelta(days=6), today

    if filter_key == "last_1_month":
        return today - timedelta(days=30), today

    if filter_key == "last_3_months":
        return today - timedelta(days=90), today

    if filter_key == "last_7_months":
        return today - timedelta(days=210), today

    if filter_key == "last_year":
        return today - timedelta(days=365), today

    if filter_key == "since_launch":
        return db_start, today

    if filter_key == "year" and year:
        return date(year, 1, 1), date(year, 12, 31)

    if filter_key == "custom" and start_date and end_date:
        return start_date, end_date

 
    return today - timedelta(days=30), today
