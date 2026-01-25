from django.shortcuts import render
from apps.adminpanel.services.date_range import get_date_range
from apps.adminpanel.services.kpis import get_kpis_with_growth

from apps.adminpanel.services.charts import get_revenue_timeseries


def admin_dashboard(request):
    filter_key = request.GET.get("filter", "last_1_month")
    year = request.GET.get("year")

    start_date, end_date = get_date_range(
        filter_key=filter_key,
        year=int(year) if year else None
    )

    context = {
      "kpis": get_kpis_with_growth(start_date, end_date),

        "chart": get_revenue_timeseries(start_date, end_date),
        "start_date": start_date,
        "end_date": end_date,
        "filter": filter_key,
    }

    return render(request, "adminpanel/dashboard/dashboard.html", context)
