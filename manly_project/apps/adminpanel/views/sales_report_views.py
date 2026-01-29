from datetime import date, timedelta
from django.utils import timezone
from apps.accounts.decorators import admin_required
from django.core.paginator import Paginator
from django.shortcuts import render

from apps.adminpanel.services.sales_report_service import get_sales_report
from django.utils import timezone
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML

from openpyxl import Workbook




def resolve_date_range(request):
    today = timezone.now().date()

    filter_type = request.GET.get("filter", "")
    from_date = request.GET.get("from_date")
    to_date = request.GET.get("to_date")

    if filter_type == "today":
        return today, today

    if filter_type == "last_7_days":
        return today - timedelta(days=6), today

    if filter_type == "this_month":
        return today.replace(day=1), today

    if filter_type == "this_year":
        return today.replace(month=1, day=1), today


    if from_date and to_date:
        try:
            return (
                date.fromisoformat(from_date),
                date.fromisoformat(to_date),
            )
        except ValueError:
            pass

  
    return today - timedelta(days=6), today

@admin_required
def admin_sales_report(request):
    start_date, end_date = resolve_date_range(request)

    report_data = get_sales_report(start_date, end_date)

    orders_qs = report_data["orders"]

  
    paginator = Paginator(orders_qs, 20)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "orders": page_obj,
        "totals": report_data["totals"],
        "start_date": start_date,
        "end_date": end_date,
        "top_products": report_data["top_products"],
    "top_categories": report_data["top_categories"],
    "offer_breakdown": report_data["offer_breakdown"], 
        "active_filter": request.GET.get("filter", ""),
        "from_date": request.GET.get("from_date", ""),
        "to_date": request.GET.get("to_date", ""),
        "printed_on": timezone.now(),   
    }

    return render(
        request,
        "adminpanel/salesreport/sales_report.html",
        context
    )
    
    
@admin_required
def admin_sales_report_print(request):
    start_date, end_date = resolve_date_range(request)

    report_data = get_sales_report(start_date, end_date)

    context = {
 
        "orders": report_data["orders"],
            "totals": report_data["totals"],
              "top_products": report_data["top_products"],
            "top_categories": report_data["top_categories"],
            "offer_breakdown": report_data["offer_breakdown"],
            "start_date": start_date,
            "end_date": end_date,
            "printed_on": timezone.now(),   
    }

    return render(
        request,
        "adminpanel/salesreport/sales_report_print.html",
        context
    )


@admin_required
def admin_sales_report_pdf(request):
    start_date, end_date = resolve_date_range(request)
    report_data = get_sales_report(start_date, end_date)

    html_string = render_to_string(
        "adminpanel/salesreport/sales_report_print.html",
        {
            "orders": report_data["orders"],
            "totals": report_data["totals"],
              "top_products": report_data["top_products"],
            "top_categories": report_data["top_categories"],
            "offer_breakdown": report_data["offer_breakdown"],
            "start_date": start_date,
            "end_date": end_date,
            "printed_on": timezone.now(),   
        },
    )

    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type="application/pdf")
    response["Content-Disposition"] = "inline; filename='sales_report.pdf'"
    return response


@admin_required
def admin_sales_report_excel(request):
    start_date, end_date = resolve_date_range(request)
    report_data = get_sales_report(start_date, end_date)

    wb = Workbook()
    ws = wb.active
    ws.title = "Sales Report"

  
    ws.append([
        "Order ID",
        "Date",
        "Items",
        "Gross",
        "Coupon",
        "Tax",
        "Shipping",
        "Final Amount",
    ])

 
    for order in report_data["orders"]:
        ws.append([
            order["order__order_id"],
            order["order__created_at"].strftime("%d-%m-%Y"),
            order["items_count"],
            float(order["gross_amount"]),
            float(order["order__coupon_discount"]),
            float(order["order__tax"]),
            float(order["order__shipping_charge"]),
            float(order["net_revenue"]),
        ])

  
    ws.append([])
    ws.append(["SUMMARY"])
    ws.append(["Total Orders", report_data["totals"]["total_orders"]])
    ws.append(["Gross Revenue", float(report_data["totals"]["gross_amount"])])
    ws.append(["Coupon Discount", float(report_data["totals"]["total_coupon_discount"])])
    ws.append(["Tax Collected", float(report_data["totals"]["total_tax"])])
    ws.append(["Shipping", float(report_data["totals"]["total_shipping"])])
    ws.append(["Net Revenue", float(report_data["totals"]["net_revenue"])])

  
    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    filename = f"sales_report_{start_date}_to_{end_date}.xlsx"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    wb.save(response)
    return response
