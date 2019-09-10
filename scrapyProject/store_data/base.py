import requests
import tempfile
import re

from django.core import files

from store_data.models import Competitor, ProductType, Product, Variant, ProductImage, VariantImage, Specification, Pricing


def create_competitor(comperitor_name, url, name):
    competitor, created = Competitor.objects.get_or_create(name=name)
    if created:
        return competitor
    competitor.name = comperitor_name
    competitor.url = url
    competitor.save()
    return competitor


def create_product_type(competitor, name, image_url, description, parent=None):
    product_type = ProductType()
    product_type.competitor = competitor
    product_type.name = name
    product_type.description = description
    if image_url:
        save_image_from_url(image_url, product_type.image)
    if parent:
        product_type.parent = parent
    product_type.save()
    return product_type

def create_product(product_name, product_title, product_description, product_images, product_in_stock, meta, product_type=None):
    product = Product()
    product.name = product_name
    if not product_type:
        print("Product should be assigned to a product type")
        return
    product.product_type = product_type
    product.title = product_title
    product.description = product_description
    product.stock_status = product_in_stock
    product.meta = meta
    product.save()
    if product_images:
        save_product_images(product, product_images)
    return product


def create_variant(product, v_title, v_descripiton, v_images, v_item_code, v_availability, v_standard_pack, v_pricing, v_specifications):
    variant = Variant()
    variant.title = v_title
    variant.product = product
    variant.description = v_descripiton
    variant.item_code = v_item_code
    variant.availability = v_availability
    variant.standard_pack_size = v_standard_pack
    variant.specification = v_specifications
    variant.save()
    for name, value in v_specifications.items():
        spec = Specification()
        spec.name = name
        spec.value = value
        spec.variant = variant
        spec.save()
    for i in range(len(v_pricing['quantity'])):
        pricing = Pricing()
        pricing.quantity = v_pricing['quantity'][i]
        primary_string = re.sub('\$', '', v_pricing['unit_price'][i])
        pricing.unitPprice = primary_string.replace(',','')
        pricing.variant = variant
        pricing.save()
    if v_images:
        save_variant_images(variant, v_images)
    return  variant


def get_response(url):
    response = None
    try:
        print("connecting...-->  {0}".format(url))
        response = requests.get(url)
    except Exception as e:
        print("could not connect to -->  {0}".format(url))
    finally:
        return response


def save_image_from_url(image_url, image_field):
    try:
        request = requests.get(image_url, stream=True)
    except Exception as e:
        print("No image found with this url {0}".format(image_url))
        return
    if request.status_code != requests.codes.ok:
        print("No image found with this url {0}".format(image_url))
        return

    # Get the filename from the url, used for saving later
    file_name = image_url.split('/')[-1] + '.jpeg'
    temp_file = tempfile.NamedTemporaryFile()
    for block in request.iter_content(1024 * 8):
        if not block:
            break
        temp_file.write(block)
    image_field.save(file_name, files.File(temp_file))


def save_product_images(product, image_urls):
    for url in image_urls:
        product_image = ProductImage()
        product_image.title = product.name
        product_image.product = product
        save_image_from_url(url, product_image.image)


def save_variant_images(variant, image_urls):
    for url in image_urls:
        variant_image = VariantImage()
        variant_image.title = variant.title
        variant_image.variant = variant
        save_image_from_url(url, variant_image.image)