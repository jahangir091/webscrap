from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from store_data.models import ProductType

# Create your views here.

from store_data.forms import DataUploadForm
from store_data.models import Product, ProductImage, VariantImage, Variant, Specification


def upload(request):

    if request.method == 'GET':
        context_dict = {
            'form' : DataUploadForm,
            'name' : 'jaha',
        }
        return render(request,
            'upload.html', context_dict)

    elif request.method == 'POST':

        # import pdb;
        # pdb.set_trace()
        product_type_id = request.POST['product_type']
        product_type = ProductType.objects.get(id=product_type_id)
        product_name = request.POST['name']
        product_description = request.POST['description']
        product_helpful_hints = request.POST['helpful_hints']
        product = create_product(product_name, product_name, product_description, product_helpful_hints, 'yes', product_type)
        product_images = request.FILES.getlist('images')
        for image in product_images:
            save_product_images(product, image)
        variant_name = request.POST['variant_name']
        variants_csv = request.FILES.getlist('variants')
        file_data = variants_csv[0].read().decode("utf-8")
        headers = file_data.split('\n')[0]
        data = file_data.split('\n')[1:]
        specifications = {}
        spec_keys = headers.split(',')
        for item in data[:-1]:
            values = item.split(',')
            i = 1
            for spec_key in spec_keys[1:]:
                key = spec_key
                value = values[i]
                i += 1
                specifications[key] = value
            create_variant(product, variant_name, values[0], specifications)

        return HttpResponseRedirect(
                reverse(
                    'index',
                )
            )
def create_variant(product, v_title, v_item_code, v_specifications):
    variant = Variant()
    variant.title = v_title
    variant.product = product
    variant.item_code = v_item_code
    variant.save()
    for name, value in v_specifications.items():
        spec = Specification()
        spec.name = name
        spec.value = value
        spec.variant = variant
        spec.save()


def create_product(product_name, product_title, product_description, helpful_hints, product_in_stock, product_type):
    product = Product()
    product.name = product_name
    if not product_type:
        print("Product should be assigned to a product type")
        return
    product.product_type = product_type
    product.title = product_title
    product.description = product_description
    product.helpful_hints = helpful_hints
    product.stock_status = product_in_stock
    product.save()
    return product


def save_product_images(product, image):

    product_image = ProductImage()
    product_image.title = product.name
    product_image.product = product
    product_image.image = image
    product_image.save()
