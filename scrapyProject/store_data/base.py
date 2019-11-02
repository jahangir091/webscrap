import requests
import tempfile
import re
from time import sleep

from bs4 import BeautifulSoup as soup

from django.core import files

from store_data.models import Competitor, ProductType, Product, Variant, ProductImage, VariantImage, Specification, Pricing
from store_data.models import ProductDocument

from selenium.webdriver.firefox.options import Options as FirefoxOptions
from django.conf import settings
from selenium import webdriver


def create_competitor(comperitor_name, url):
    competitor, created = Competitor.objects.get_or_create(name=comperitor_name)
    if created:
        competitor.url = url
        competitor.save()
    return competitor


def create_product_type(competitor, name, image_url, description, parent=None):
    product_type, created = ProductType.objects.get_or_create(name=name, competitor=competitor)
    if created:
        product_type.name = name
        product_type.description = description
    if image_url:
        save_image_from_url(image_url, product_type.image)
    if parent:
        product_type.parent = parent
    product_type.save()
    return product_type

def create_product(product_name, product_title, product_description, product_images, product_in_stock, meta, product_type=None, product_documents=None):
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
    if product_documents:
        save_product_documents(product, product_documents)
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
    #if v_images:
    #    save_variant_images(variant, v_images)
    return  variant


def get_response(url):
    response = None
    try:
        print("connecting...-->  {0}".format(url))
        response = requests.get(url)
    except Exception as e:
        print(e)
        print("could not connect to -->  {0}".format(url))
    finally:
        return response


def save_image_from_url(image_url, file_name, image_field):
    try:
        request = requests.get(image_url, stream=True)
    except Exception as e:
        print("No image found with this url {0}".format(image_url))
        return
    if request.status_code != requests.codes.ok:
        print("No image found with this url {0}".format(image_url))
        return

    # Get the filename from the url, used for saving later
    temp_file = tempfile.NamedTemporaryFile()
    for block in request.iter_content(1024 * 8):
        if not block:
            break
        temp_file.write(block)
    image_field.save(file_name, files.File(temp_file))


def save_document_from_url(url, file_name, document_field):

    try:
        request = requests.get(url, stream=True)
    except Exception as e:
        print("No document found with this url {0}".format(url))
        return
    if request.status_code != requests.codes.ok:
        print("No document found with this url {0}".format(url))
        return

    # Get the filename from the url, used for saving later
    temp_file = tempfile.NamedTemporaryFile()
    for block in request.iter_content(1024 * 8):
        if not block:
            break
        temp_file.write(block)
    document_field.save(file_name, files.File(temp_file))


def save_product_images(product, image_urls):
    for url in image_urls:
        product_image = ProductImage()
        product_image.title = product.name
        product_image.product = product
        file_name = url.split('/')[-1]
        #if file does not have any extention (like essectra) then use the following line
        #file_name = file_name.split('.')[0] + '.jpg'
        save_image_from_url(url, file_name, product_image.image)


def save_product_documents(product, document_urls):
    for url in document_urls:
        doc_url = url.split('@')[0]
        file_name = url.split('@')[1] + '.pdf'
        product_document = ProductDocument()
        product_document.title = product.name
        product_document.product = product
        save_document_from_url(doc_url, file_name, product_document.document)


def save_variant_images(variant, image_urls):
    for url in image_urls:
        variant_image = VariantImage()
        variant_image.title = variant.title
        variant_image.variant = variant
        file_name = url.split('/')[-1]
        save_image_from_url(url, file_name, variant_image.image)


def get_soup(response):
    html_page = response.text
    page_soup = soup(html_page, 'html.parser')
    return page_soup


def get_browser(url):
    print('connecting >> {0}'.format(url))
    # chrome_options = Options()
    # chrome_options.add_argument('--headless')
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # browser = webdriver.Chrome( settings.BASE_DIR + '/chromedriver', chrome_options = chrome_options)
    firefox_options = FirefoxOptions()
    firefox_options.headless = True
    browser = webdriver.Firefox(firefox_options=firefox_options, executable_path=settings.BASE_DIR + '/geckodriver')
    browser.get(url)
    print("Please wait 5 seconds")
    sleep(5)
    return browser


def save_svg_diagram(variant, svg_code):
    variant_image = VariantImage()
    variant_image.title = variant.title
    variant_image.variant = variant
    file_name = variant.title + 'svg'
    temp_file = tempfile.NamedTemporaryFile(suffix='.svg')
    temp_file.write(svg_code)
    variant_image.image.save(file_name, files.File(temp_file))
