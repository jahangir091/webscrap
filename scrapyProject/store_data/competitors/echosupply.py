from store_data.base import create_competitor, create_product_type, create_product, create_variant, get_response
from store_data.base import get_soup
from time import sleep
from selenium.webdriver.chrome.options import Options as ChromeOPtions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from django.conf import settings
from selenium import webdriver
from selenium.webdriver.support.ui import Select

product_type_urls = [
    "https://www.echosupply.com/products/masking/plugs",
    "https://www.echosupply.com/products/masking/caps",
    "https://www.echosupply.com/products/masking/die-cuts",
    "https://www.echosupply.com/products/masking/tapes",
    "https://www.echosupply.com/products/hanging/hooks",
    "https://www.echosupply.com/products/protection/plugs",
    "https://www.echosupply.com/products/protection/threaded-plugs",
    "https://www.echosupply.com/products/protection/caps",
    "https://www.echosupply.com/products/protection/netting"
]

competitor_name = 'echosupply'

base_url = 'https://www.echosupply.com'

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
    return browser


def load_echosupply_products():
    competitor = create_competitor(competitor_name, base_url)
    for url in product_type_urls:
        product_type1_name = url.split('/')[4]
        product_type1 = create_product_type(competitor, product_type1_name, None, '')
        product_type2_name = url.split('/')[5]
        product_type2 = create_product_type(competitor, product_type2_name, None, '', product_type1)

        products_page = get_browser(url)
        print('wait 15 seconds')
        sleep(10)
        product_urls = get_product_urls(products_page)
        for product_url in product_urls:
            product_page = get_browser(product_url)
            print('wait 15 seconds')
            sleep(10)
            variants, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(product_page)
            product = create_product(product_name, product_title, product_description, product_images,
                                     product_stock_status, meta, product_type=product_type2)
            variant_count = 0
            for variant in variants:
                print("Loading product {0}-->{1}".format(product_type2, product))
                variant = create_variant(product, variant['title'], variant['descripiton'], variant['variant_images'], variant['item_code'], variant['availability'],
                                         variant['standard_pack'], variant['pricing'], variant['specifications'])
                variant_count += 1
            print("loaded {0} variants of product {1}".format(variant_count, product.name))
            product_page.quit()


def get_product_urls(browser):
    # import pdb; pdb.set_trace()
    section = browser.find_element_by_css_selector('body > es-app > div > es-product-category > main > div > section')
    products = section.find_elements_by_tag_name('li')
    product_urls = []
    for product in products:
        product_url = product.find_element_by_tag_name('a').get_attribute('href')
        product_urls.append(product_url)

    return product_urls


def get_product_info(browser):
    # import pdb; pdb.set_trace()
    product_name = browser.find_element_by_tag_name('h1').text if browser.find_element_by_tag_name('h1') else ''
    product_title = product_name
    meta = browser.find_element_by_xpath('/html/head/meta[6]').get_attribute('content') if browser.find_element_by_xpath('/html/head/meta[6]') else ''

    product_features_divs = browser.find_elements_by_class_name('product-features')
    product_features = []
    if product_features_divs:
        product_features = product_features_divs[0].find_elements_by_tag_name('li')
    product_description = ''
    for feature in product_features:
        product_description += feature.text.strip()
    product_description = product_description
    stock_status = ''
    product_images = []
    img1_divs = browser.find_elements_by_class_name('product-image')
    for img_div in img1_divs:
        product_images.append(img_div.find_element_by_tag_name('img').get_attribute('src'))
    img2_divs = browser.find_elements_by_class_name('product-diagram')
    for img_div in img2_divs:
        product_images.append(img_div.find_element_by_tag_name('img').get_attribute('src'))

    # fetch product variants
    variants = []
    variants_tables = browser.find_elements_by_tag_name('table')
    if variants_tables:
        variants_table = variants_tables[0]
        table_headers = variants_table.find_element_by_tag_name('thead').find_elements_by_tag_name('th')
        table_rows = variants_table.find_element_by_tag_name('tbody').find_elements_by_tag_name('tr')
        for table_row in table_rows:
            #----------------------variant details-------------------------------------------------------
            variant = {}
            tds = table_row.find_elements_by_tag_name('td')
            variant['title'] = product_title if product_title else ''
            variant['descripiton'] = ''
            variant['variant_images'] = []
            variant['item_code'] = tds[0].text if tds else None
            variant['availability'] = ''
            variant['standard_pack'] = 0
            #----------------------------------------------------------------------------------------------

            #---------------------------------variant pricing-----------------------------------------------
            pricing = {}
            quantities = []
            unit_prices = []
            # import pdb; pdb.set_trace()
            # variant_unit_price = tds[-3:-2][0].text.strip()
            #
            # quantities.append(variant_unit_price.split('/')[1].strip() if variant_unit_price else '0')
            # unit_prices.append(variant_unit_price.split('/')[0].strip() if variant_unit_price else '0')
            # pricing['quantity'] = quantities
            # pricing['unit_price'] = unit_prices
            # variant['pricing'] = pricing
            #----------------------------------------------------------------------------------------------

            #---------------------------specifications-----------------------------------------------------
            specifications = {}
            for i in range(len(table_headers)):
                if table_headers[i].text.strip().lower() in ['Part Number'.lower(), 'Qty.'.lower()]:
                    continue
                if table_headers[i].text.strip().lower() == 'Unit Price'.lower():
                    variant_unit_price = tds[i].text.strip()
                    quantities.append(variant_unit_price.split('/')[1].strip() if variant_unit_price else '0')
                    unit_prices.append(variant_unit_price.split('/')[0].strip() if variant_unit_price else '0')
                    pricing['quantity'] = quantities
                    pricing['unit_price'] = unit_prices
                    variant['pricing'] = pricing
                    continue
                key = table_headers[i].text.strip()
                value = tds[i].text.strip()
                specifications[key] = value

            option = browser.find_element_by_id('selectedUnits')
            select = Select(option)
            # import pdb; pdb.set_trace()
            select.select_by_visible_text('Metric')
            for i in range(len(table_headers)):
                if table_headers[i].text.strip().lower() in ['Part Number'.lower(), 'Unit Price'.lower(), 'Qty.'.lower()]:
                    continue
                converted_spans = tds[i].find_elements_by_tag_name('span')

                if converted_spans and converted_spans[0].get_attribute('class') == 'converted':
                    key = table_headers[i].text.strip()
                    value = tds[i].text.strip()
                    specifications[key] = value

            variant['specifications'] = specifications
            select.select_by_visible_text('SAE')
            #-----------------------------------------------------------------------------------------------

            variants.append(variant)
    return variants, product_name, product_title, product_description, product_images, stock_status, meta
