from selenium import webdriver
from selenium.webdriver.support.ui import Select
import unicodedata
from selenium.webdriver.chrome.options import Options
from django.conf import settings
from time import sleep
from store_data.base import create_competitor, create_product_type, create_product, create_variant
from store_data.base import  get_soup, get_response, get_browser, save_svg_diagram


HARMANCORP_BASE_URL = 'https://www.stockcap.com'
competitor_name = 'stockcap'
base_url = 'https://www.stockcap.com'

product_type_urls = [
    'https://www.stockcap.com/store/caps.html',
    #'https://www.stockcap.com/store/plugs.html',
    #'https://www.stockcap.com/store/tubing-tapes-more.html'
    ]
done_urls = ['https://www.stockcap.com/store/short-caps.html',
             'https://www.stockcap.com/store/long-caps.html',
             'https://www.stockcap.com/store/rectangular-caps.html',
             'https://www.stockcap.com/store/square-caps.html'
             ]


def load_stockcap_products():
    competitor = create_competitor(competitor_name, base_url)
    for url in product_type_urls:
        product_type_name = url.split('/')[4].split('.')[0]
        product_type = create_product_type(competitor, product_type_name, None, '')
        response = get_response(url)
        product_urls = get_product_urls(response)
        flag = 0
        for product_url in product_urls:
            if product_url == 'https://www.stockcap.com/store/angle-caps.html':
                flag = 1
            if flag == 0:
                continue
            variants, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(
                product_url)
            product = create_product(product_name, product_title, product_description, product_images,
                                     product_stock_status, meta, product_url, product_type=product_type)
            variant_count = 0
            # import pdb; pdb.set_trace()
            print("Loading product {0}-->{1}".format(product_type, product))
            for variant in variants:
                variant = create_variant(product, variant['title'], variant['descripiton'],
                                         variant['variant_images'], variant['item_code'], variant['availability'],
                                         variant['standard_pack'], variant['pricing'], variant['specifications'])
                variant_count += 1
            print("loaded {0} variants of product {1}".format(variant_count, product.name))

def get_product_urls(response):
    soup = get_soup(response)
    products_div = soup.find("div", {"id":"rightText"})
    product_divs = products_div.find_all('span', {"class": "subcategories"})
    product_urls = []
    for product in product_divs:
        product_url = product.a['href']
        if 'https://www.stockcap.com' not in product_url:
            product_url = 'https://www.stockcap.com' + product_url
        product_urls.append(product_url)

    return product_urls


def get_product_info(url):
    browser = get_browser(url)

    product_name = get_product_name(browser)
    product_title = product_name
    meta = get_meta(browser)
    stock_status = get_stock_status(browser)
    product_images = get_product_images(browser)
    product_description = get_product_description(browser)

    variants = []

    select_tags = browser.find_elements_by_tag_name('select')
    attr_name = ''
    if select_tags:
        select_tag = select_tags[0]
        attr_name = select_tag.get_attribute('name')

    if browser.find_elements_by_id('scrollbar2'):
        variant_table_div = browser.find_elements_by_id('scrollbar2')[0]
        if variant_table_div:
            variant_tables = variant_table_div.find_elements_by_tag_name('table')
            if variant_tables:
                table_rows = variant_tables[0].find_elements_by_tag_name('tr')
                for row in table_rows[:-1]:
                    columns = row.find_elements_by_tag_name('td')
                    quantity = columns[-2]
                    options = quantity.find_elements_by_tag_name('option')
                    quantity_value = options[0].get_attribute('value')
                    variant_url = base_url + '/store/' + 'product.php?productid=' + quantity_value
                    variant = get_variant_details(variant_url)
                    variants.append(variant)
    elif 'efield' in attr_name:
        variant_urls = get_variant_urls(browser)
        for variant_url in variant_urls:
            variant = get_variant_details(variant_url)
            variants.append(variant)
    elif browser.find_elements_by_class_name('subcategory-descr'):
        variant_table_div = browser.find_elements_by_class_name('subcategory-descr')[0]
        if variant_table_div:
            variant_tables = variant_table_div.find_elements_by_tag_name('table')
            for table in variant_tables:
                if table.get_attribute('border') == '1':
                    variant_table = table
                    variants = get_variants(variant_table)

    browser.quit()
    return variants, product_name, product_title, product_description, product_images, stock_status, meta


def get_product_name(browser):
    product_name = ''
    if browser.find_elements_by_id('rightText'):
        product_name_tags = browser.find_elements_by_id('rightText')[0].find_elements_by_tag_name('h1')
        if product_name_tags:
            product_name = product_name_tags[0].text.strip()
    return product_name


def get_product_title(browser):
    pass


def get_product_description(browser):
    product_desc = browser.find_element_by_id('rightText').text.strip().split('\n')[2]
    return product_desc


def get_product_images(browser):
    images = []
    all_images = browser.find_element_by_id('rightText').find_elements_by_tag_name('img')
    for img in all_images:
        img_url = img.get_attribute('src')
        if 'btn' not in img_url:
            images.append(img_url)
    return images


def get_stock_status(browser):
    return ''


def get_meta(browser):
    try:
        meta = browser.find_element_by_xpath('/html/head/meta[6]').get_attribute('content')
    except Exception as e:
        meta = 'No meta info'

    return meta


def get_variant_details(url):
    response1 = get_response(url)
    browser = get_browser(response1.url)
    variant = {}
    variant['item_code'] = ''
    variant['availability'] = ''
    variant['specifications'] = {}
    variant['standard_pack'] = 0
    variant['pricing'] = {}

    title = browser.find_elements_by_id("rightText")
    if title:
        variant['title'] = title[0].find_element_by_tag_name('h1').text.strip()
    else:
        variant['title'] = ''

    variant_desc_div = browser.find_elements_by_id("productDesc")
    if variant_desc_div:
        desc_div = variant_desc_div[0].find_elements_by_tag_name('div')
        if desc_div:
            variant['descripiton'] = desc_div[0].find_element_by_tag_name('font').text.strip()
    else:
        variant['descripiton'] = ''
    variant['variant_images'] = []
    specifications_div = browser.find_elements_by_id("productDesc")
    if specifications_div:
        specifications = {}
        variant_specs = specifications_div[0].find_elements_by_tag_name('li')
        for v_spec in variant_specs:
            key = v_spec.text.strip().split(':')[0].strip()
            value = v_spec.text.strip().split(':')[1].strip()
            specifications[key] = value
        spec_table = specifications_div[0].find_elements_by_tag_name('tbody')
        if spec_table:
            spec_rows = spec_table[0].find_elements_by_tag_name('tr')
            pricing = {}
            quantities = []
            unit_prices = []
            for spec_row in spec_rows:
                spec_cols = spec_row.find_elements_by_tag_name('td')
                if spec_cols[0].text.strip().lower() == 'part #:':
                    variant['item_code'] = spec_cols[1].text.strip()
                elif spec_cols[0].text.strip().lower() == 'unit price:':
                    quantity = 1
                    unit_price = spec_cols[1].text.strip()
                    quantities.append(quantity)
                    unit_prices.append(unit_price)
                    pricing['quantity'] = quantities
                    pricing['unit_price'] = unit_prices
                    variant['pricing'] = pricing
                elif spec_cols[0].text.strip().lower() == 'pkg quantity:':
                    pack = spec_cols[1].text
                    import re
                    pack = re.split('/| ', pack)
                    # pack = pack.split('/')
                    if pack:
                        pack = pack[0].strip()
                        variant['standard_pack'] = int(pack)
                else:
                    specifications[spec_cols[0].text.strip()] = spec_cols[1].text.strip()
            variant['availability'] = ''
            variant['specifications'] = specifications
    browser.quit()
    return variant


def get_variant_urls(browser):
    variant_urls = []
    select_elements = browser.find_elements_by_tag_name('select')
    if select_elements:
        select_element1 = select_elements[0]
        select_element2 = select_elements[1]
        select1 = Select(select_element1)
        select2 = Select(select_element2)
        select1_option_tags = select_element1.find_elements_by_tag_name('option')

        for select1_option_tag in select1_option_tags[1:-1]:
            select1_option_visible_text = select1_option_tag.text.strip()
            select1.select_by_visible_text(select1_option_visible_text)
            sleep(2)
            print(select1_option_visible_text)

            select2_option_tags = select_element2.find_elements_by_tag_name('option')
            if len(select2_option_tags) >2:
                select2_option_visible_text = select2_option_tags[1].text.strip()
                select2.select_by_visible_text(select2_option_visible_text)
                variant_list_table_divs = browser.find_elements_by_id('plist')
                if variant_list_table_divs:
                    variant_list_table_div = variant_list_table_divs[0]
                    variant_list_table = variant_list_table_div.find_elements_by_tag_name('table')[0]
                    table_rows = variant_list_table.find_elements_by_tag_name('tr')
                    if len(table_rows) > 2:
                        for row in table_rows[1:-1]:
                            columns = row.find_elements_by_tag_name('td')
                            variant_urls.append(columns[-1].find_element_by_tag_name('a').get_attribute('href'))

    return variant_urls


def get_variants(variant_table):
    variants = []
    table_rows = variant_table.find_elements_by_tag_name('tr')
    variant_table_headers = table_rows[0].find_elements_by_tag_name('td')
    for row in table_rows:
        variant = {}
        specifications = {}
        pricing = {}
        quantities = []
        unit_prices = []
        variant['title'] = ''
        variant['descripiton'] = ''
        variant['variant_images'] = []
        pricing['quantity'] = quantities
        pricing['unit_price'] = unit_prices
        variant['pricing'] = pricing
        variant['standard_pack'] = 0
        variant['item_code'] = ''
        spec_cols = row.find_elements_by_tag_name('td')
        i = 0
        for col in spec_cols:
            if variant_table_headers[i].text.strip().lower() == 'part number':
                variant['item_code'] = col.text.strip()
            else:
                specifications[variant_table_headers[i].text.strip()] = col.text.strip()
            i += 1
        variant['availability'] = ''
        variant['specifications'] = specifications
        variants.append(variant)
    return variants