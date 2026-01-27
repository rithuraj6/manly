from django.db.models import  Q, Sum, Count , DecimalField
from django.db.models.functions import Coalesce
from django.utils.timezone import make_aware, datetime
from django.db.models import F


from apps.orders.models import OrderItem
from apps.orders.models import Payment


def get_sales_report(start_date, end_date):
    
    
    start_datetime = make_aware(
        datetime.combine(start_date, datetime.min.time())
    )
    end_datetime = make_aware(
        datetime.combine(end_date, datetime.max.time())
    )

    
    items_qs = (
        OrderItem.objects
        .select_related(
            "order",
            "order__user",
            "product",
            "product__category",
        )
        .filter(
            status="delivered",
            order__status="delivered",
            order__payment__status="success",
            order__payment__created_at__range=(start_datetime, end_datetime),
        )
    )
   
    totals = items_qs.aggregate(
        total_orders=Count("order", distinct=True),
        gross_amount=Coalesce(Sum("line_total"), 0, output_field=DecimalField()),
        net_revenue=Coalesce(Sum("final_price_paid"), 0, output_field=DecimalField()),
        total_coupon_discount=Coalesce(
            Sum("order__coupon_discount", distinct=True),
            0,
            output_field=DecimalField(),
        ),
        total_tax=Coalesce(
            Sum("order__tax", distinct=True),
            0,
            output_field=DecimalField(),
        ),
        total_shipping=Coalesce(
            Sum("order__shipping_charge", distinct=True),
            0,
            output_field=DecimalField(),
        ),
    )

   
    offer_breakdown = items_qs.aggregate(
        orders_with_coupon=Count(
            "order",
            filter=Q(order__coupon_discount__gt=0),
            distinct=True,
        ),
        orders_without_coupon=Count(
            "order",
            filter=Q(order__coupon_discount=0),
            distinct=True,
        ),
        revenue_with_coupon=Coalesce(
            Sum("final_price_paid", filter=Q(order__coupon_discount__gt=0)),
            0,
            output_field=DecimalField(),
        ),
        revenue_without_coupon=Coalesce(
            Sum("final_price_paid", filter=Q(order__coupon_discount=0)),
            0,
            output_field=DecimalField(),
        ),
        coupon_loss=Coalesce(
            Sum("order__coupon_discount", distinct=True),
            0,
            output_field=DecimalField(),
        ),
    )

    top_products = (
        items_qs
        .values("product__id", "product__name")
        .annotate(
            units_sold=Sum("quantity"),
            revenue=Coalesce(
                Sum("final_price_paid"),
                0,
                output_field=DecimalField(),
            ),
        )
        .order_by("-units_sold")[:10]
    )

   
    top_categories = (
        items_qs
        .values("product__category__id", "product__category__name")
        .annotate(
            units_sold=Sum("quantity"),
            revenue=Coalesce(
                Sum("final_price_paid"),
                0,
                output_field=DecimalField(),
            ),
        )
        .order_by("-units_sold")[:10]
    )
    
    
    orders_qs = (
        items_qs
        .values(
            "order__id",
            "order__order_id",
            "order__created_at",
            "order__user__email",
            "order__coupon_discount",
            "order__tax",
            "order__shipping_charge",
        )
        .annotate(
            items_count=Count("id"),
            gross_amount=Coalesce(
                Sum("line_total"),
                0,
                output_field=DecimalField(),
            ),
            net_revenue=Coalesce(
                Sum("final_price_paid"),
                0,
                output_field=DecimalField(),
            ),
        )
        .order_by("-order__created_at")
    )
    total_items_sold=Coalesce(Sum("quantity"), 0),

    return {
        "orders": orders_qs,
        "totals": totals,
        "offer_breakdown": offer_breakdown,
        "top_products": list(top_products),
        "top_categories": list(top_categories),
        "start_date": start_date,
        "end_date": end_date,
    }
