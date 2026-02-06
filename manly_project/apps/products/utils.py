from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
from apps.orders.utils.pricing import apply_offer, get_best_offer

from decimal import Decimal

def crop_and_resize(image_file, size=(800, 1000)):
    img = Image.open(image_file).convert("RGB")

    width, height = img.size
    min_side = min(width, height)

    left = (width - min_side) / 2
    top = (height - min_side) / 2
    right = (width + min_side) / 2
    bottom = (height + min_side) / 2

    img = img.crop((left, top, right, bottom))
    img = img.resize(size, Image.LANCZOS)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=90)
    return ContentFile(buffer.getvalue(), name=image_file.name)


         
def attach_offer_data(products):
    for product in products:
        discounted_price = apply_offer(product, product.base_price)

        if discounted_price < product.base_price:
            product.discounted_price = discounted_price
            product.offer_percentage = (
                (product.base_price - discounted_price)
                / product.base_price * 100
            ).quantize(Decimal("1"))
        else:
            product.discounted_price = product.base_price
            product.offer_percentage = None
        
    