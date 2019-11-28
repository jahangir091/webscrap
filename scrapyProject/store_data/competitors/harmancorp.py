from selenium import webdriver
import unicodedata
from selenium.webdriver.chrome.options import Options
from django.conf import settings
from time import sleep
from store_data.base import create_competitor, create_product_type, create_product, create_variant
from store_data.base import  get_soup, get_response, get_browser, save_svg_diagram


HARMANCORP_BASE_URL = 'https://www.harmancorp.com'
competitor_name = 'harmancorp'
base_url = 'https://www.harmancorp.com'

product_type_urls = ['https://www.harmancorp.com/caps-grips',
                     'https://www.harmancorp.com/stoppers-tape-more',
                     'https://www.harmancorp.com/plugs',
                     'https://www.harmancorp.com/mini-packs'
                     ]



def load_harmancorp_products():
    competitor = create_competitor(competitor_name, base_url)
    for url in product_type_urls:
        product_type_name = url.split('/')[3]
        product_type = create_product_type(competitor, product_type_name, None, '')
        response = get_response(url)
        product_urls = get_product_urls(response)
        for product_url in product_urls:
            variants, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(
                product_url)
            product = create_product(product_name, product_title, product_description, product_images,
                                     product_stock_status, meta, product_url, product_type=product_type)
            variant_count = 0
            print("Loading product {0}-->{1}".format(product_type, product))
            for variant in variants:
                variant = create_variant(product, variant['title'], variant['descripiton'],
                                         variant['variant_images'], variant['item_code'], variant['availability'],
                                         variant['standard_pack'], variant['pricing'], variant['specifications'])
                variant_count += 1
            print("loaded {0} variants of product {1}".format(variant_count, product.name))

def get_product_urls(response):
    soup = get_soup(response)
    products = soup.find_all('div', {'class': 'cp-category-grid--small-item'})
    product_urls = []
    for product in products:
        product_url = product.a['href']
        product_urls.append(product_url)

    return product_urls

def get_product_info(url):
    browser = get_browser(url)
    product_name = ''
    if browser.find_elements_by_class_name('cp-page-heading'):
        product_name = browser.find_elements_by_class_name('cp-page-heading')[0].text.strip()
    product_title = product_name
    meta = browser.find_element_by_xpath('/html/head/meta[12]').get_attribute('content')

    stock_status = ''

    # fetch product images
    product_images = []
    if browser.find_elements_by_class_name('cp-info__image'):
        image_url = browser.find_elements_by_class_name('cp-info__image')[0].find_element_by_tag_name('img').get_attribute('src')
        product_images.append(image_url)
    if browser.find_elements_by_class_name('__mce_add_custom__'):
        image_url = browser.find_elements_by_class_name('__mce_add_custom__')[0].get_attribute('src')
        product_images.append(image_url)
    if browser.find_elements_by_class_name('js-category-diagram-img'):
        if browser.find_elements_by_class_name('js-category-diagram-img')[0].find_elements_by_tag_name('img'):
            image_url = browser.find_elements_by_class_name('js-category-diagram-img')[0].find_element_by_tag_name('img').get_attribute('src')
            product_images.append(image_url)

    # fetch product description
    product_description = ''
    response = get_response(url)
    soup = get_soup(response)
    product_descriptions = soup.find('table', {'class':'category-description'}).text.strip().split('\n')
    for description in product_descriptions:
        product_description += description
    # fetch product variants
    variants = []
    variants_table = browser.find_element_by_class_name('js-category-chart-full').find_element_by_tag_name('table')
    theads = variants_table.find_element_by_class_name('js-products-chart-head').find_elements_by_tag_name('tr')[0].find_elements_by_tag_name('th')

    trs = variants_table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
    for tr in trs:
        variant = {}

        tds = tr.find_elements_by_tag_name('td')
        variant['title'] = tds[0].text.strip()
        variant['descripiton'] = ''
        variant['variant_images'] = []
        variant['item_code'] = tds[0].text.strip()
        variant['availability'] = ''
        variant['standard_pack'] = 0
##-----------------------------------------------------------------------------------------------------------
        pricing = {}
        quantities = []
        unit_prices = []
        # variant_unit_price = tr.find('div', {'itemprop': 'price'}).text.strip() if tr.find('div', {
        #     'itemprop': 'price'}) else None
        # quantities.append(variant_unit_price.split('/')[1] if variant_unit_price else '0')
        # unit_prices.append(variant_unit_price.split('/')[0] if variant_unit_price else '0')
        # pricing['quantity'] = quantities
        # pricing['unit_price'] = unit_prices
        variant['pricing'] = []
##-------------------------------------------------------------------------------------------------------------
        specifications = {}
        spec_keys = []
        for thead in theads[1:-2]:
            spec_keys.append(thead.text.strip())

        i = 1
        for spec_key in spec_keys:
            if spec_key.lower() == 'quantity' and tds[i].text:
                quantity = tds[i].text.split('\n')[2].split(' ')[-1]
                unit_price = tds[i].text.split('\n')[3].split(' ')[-1]
                quantities.append(quantity)
                unit_prices.append(unit_price)
                pricing['quantity'] = quantities
                pricing['unit_price'] = unit_prices
                variant['pricing'] = pricing
                continue
            key = spec_key
            value = tds[i].text.strip()
            i += 1
            specifications[key] = value
        variant['specifications'] = specifications

        variants.append(variant)
    browser.quit()
    return variants, product_name, product_title, product_description, product_images, stock_status, meta

