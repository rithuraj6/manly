from django.db import transaction


@transaction.atomic
def restore_stock(order_item):
  
 
    variant = order_item.variant
    variant.stock += order_item.quantity
    variant.save(update_fields=["stock"])
