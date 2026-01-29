from apps.adminpanel.services.date_range import get_date_range
from apps.adminpanel.services.exports import export_sales_csv

from apps.accounts.decorators import admin_required

@admin_required
def admin_sales_export(request):
    filter_key = request.GET.get("filter", "last_1_month")
    year = request.GET.get("year")

    start_date, end_date = get_date_range(
        filter_key=filter_key,
        year=int(year) if year else None
    )

    return export_sales_csv(start_date, end_date)
