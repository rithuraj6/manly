from apps.sizeguide.models import SizeGuide


def calculate_user_size(*, chest=None, shoulder=None):
    if not chest:
        return None

    queryset = SizeGuide.objects.filter(is_active=True).order_by("chest_min")

    if shoulder:
        size = queryset.filter(
            chest_min__lte=chest,
            chest_max__gte=chest,
            shoulder_min__lte=shoulder,
            shoulder_max__gte=shoulder,
        ).first()

        if size:
            return size.size_name

    size = queryset.filter(
        chest_min__lte=chest,
        chest_max__gte=chest,
    ).first()

    return size.size_name if size else None
