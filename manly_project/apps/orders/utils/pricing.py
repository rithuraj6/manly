from decimal import Decimal, ROUND_HALF_UP

def distribute_amount(total_amount, items):
    if not items:
        return []

    total_base = sum(item["base"] for item in items)

    if total_base == 0:
        return [Decimal("0.00")] * len(items)

    distributed = []
    running_total = Decimal("0.00")

    for index, item in enumerate(items):
        if index == len(items) - 1:
            share = total_amount - running_total
        else:
            share = (
                (item["base"] / total_base) * total_amount
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            running_total += share

        distributed.append(share)

    return distributed
