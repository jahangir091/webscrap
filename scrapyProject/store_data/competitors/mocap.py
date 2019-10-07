from selenium import webdriver
import unicodedata
from selenium.webdriver.chrome.options import Options
from django.conf import settings

from store_data.base import create_competitor, create_product_type, create_product, create_variant
from store_data.base import  get_soup, get_response


ALL_MOCAP_PRODUCTS_URL = 'https://www.mocap.com/mocap-all-products.html'
variant_base_url = 'https://store.mocap.com/mocap_en/'


def get_browser(url):
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    browser = webdriver.Chrome( settings.BASE_DIR + '/chromedriver', chrome_options = chrome_options)
    browser.get(url)

    return browser


def load_essentra_products():
    response = get_response(ALL_MOCAP_PRODUCTS_URL)
    product_urls = get_products_urls_list(response)
    for product_url in product_urls:
        response = get_response(product_url)
        product_type_urls, variant_urls, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(response)


def get_products_urls_list(response):
    soup = get_soup(response)
    products = soup.find_all("div", {"class": "allproductsdiv"})
    product_urls = []
    for product in products:
        product_urls.append(product.a['href'])
    return product_urls


def get_product_info(browser):
    product_type_urls = []
    product_type_links = browser.find_elements_by_class_name('breadnav')
    for product_type_link in product_type_links[1:-1]:
        product_type_urls.append(product_type_link.get_attribute('href'))
    product_title = browser.find_element_by_id('prod_h2').text if browser.find_element_by_id('prod_h2') else ''
    product_code = browser.find_element_by_id('prodcodename1').text if browser.find_element_by_id('prodcodename1') else ''
    product_name = browser.find_element_by_id('prod_h2').text if browser.find_element_by_id('prod_h2') else ''
    product_description = browser.find_element_by_id('scrollContent').text if browser.find_element_by_id('scrollContent') else ''
    stock_status = ''
    meta = browser.find_element_by_xpath('/html/head/meta[5]').get_attribute('content')

    product_images = []
    images_div = browser.find_element_by_id('thmpics')
    image_elements = images_div.find_elements_by_tag_name('img')
    for image_element in image_elements:
        image_src = image_element.get_attribute('src')
        resized_image_src = image_src[:-8] + '0300.png'
        product_images.append(resized_image_src)

    variant_links = []
    variants_table = browser.find_element_by_id('SZCHARTID') if browser.find_element_by_id('SZCHARTID') else None
    table_row_elements = variants_table.find_elements_by_tag_name('tr') if variants_table else None
    if table_row_elements:
        for tr in table_row_elements[1:-1]:
            part_no = tr.get_attribute('title')
            variant_link = variant_base_url + product_code.lower() + '.html?item=' + part_no
            variant_links.append(variant_link)

    browser.quit()
    return product_type_urls , variant_links, product_name, product_title, product_description, product_images, stock_status, meta


def get_variant_info(browser):
    import pdb; pdb.set_trace()
    title = browser.find_element_by_class_name('product-name').text if browser.find_element_by_class_name('product-name') else ''
    descripiton_div = browser.find_element_by_class_name('box-collateral') if browser.find_element_by_class_name('box-collateral') else None
    descripiton = descripiton_div.find_element_by_class_name('std').text if descripiton_div.find_element_by_class_name('std') else ''
    item_code_div = browser.find_element_by_class_name('product-name') if browser.find_element_by_class_name('product-name') else None
    item_code = item_code_div.find_element_by_tag_name('span').text
    availability = ''
    standard_pack = ''
    return title, descripiton, variant_images, item_code, availability, standard_pack, pricing, specifications
