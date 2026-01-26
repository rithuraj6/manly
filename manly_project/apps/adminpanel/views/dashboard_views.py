from django.shortcuts import render
from datetime import date, timedelta
from django.utils import timezone

from apps.adminpanel.services.kpis import get_kpis_with_growth
from apps.adminpanel.services.charts import get_revenue_timeseries


def admin_dashboard(request):
    today = timezone.now().date()

    # ---- GET PARAMS ----
    filter_type = request.GET.get("filter", "last_7_days")
    year = int(request.GET.get("year", today.year))

    # ---- BASE YEAR BOUNDARIES ----
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    # ---- DATE RANGE LOGIC ----
    if filter_type == "last_7_days":
        end_date = min(today, year_end)
        start_date = end_date - timedelta(days=6)

    elif filter_type == "last_3_months":
        end_date = min(today, year_end)
        start_date = end_date - timedelta(days=90)

    elif filter_type == "last_7_months":
        end_date = min(today, year_end)
        start_date = end_date - timedelta(days=210)

    elif filter_type == "since_launch":
        start_date = year_start
        end_date = min(today, year_end)

    else:
        start_date = year_start
        end_date = min(today, year_end)

    # ---- CONTEXT ----
    context = {
        "kpis": get_kpis_with_growth(start_date, end_date),
        "chart": get_revenue_timeseries(start_date, end_date),
        "start_date": start_date,
        "end_date": end_date,
        "filter": filter_type,
    }

    return render(request, "adminpanel/dashboard/dashboard.html", context)
