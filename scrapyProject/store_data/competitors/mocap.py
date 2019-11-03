from selenium import webdriver
import unicodedata
from selenium.webdriver.chrome.options import Options
from django.conf import settings
from time import sleep
from store_data.base import create_competitor, create_product_type, create_product, create_variant
from store_data.base import  get_soup, get_response, get_browser, save_svg_diagram


ALL_MOCAP_PRODUCTS_URL = 'https://www.mocap.com/mocap-all-products.html'
variant_base_url = 'https://store.mocap.com/mocap_en/'
MOCAP_BASE_URL = 'https://www.mocap.com/'
competitor_name = 'mocap'
base_url = 'https://www.mocap.com'





def load_mocap_products():
    competitor = create_competitor(competitor_name, base_url)
    product_urls = get_products_urls_list(ALL_MOCAP_PRODUCTS_URL)
    product_counter = 0
    for product_url in product_urls:
        product_counter += 1
        if product_counter <= 58:
            continue
        print('>>>Product No-{0}: {1}'.format(product_counter, product_url))
        product_type_urls, variant_urls, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(product_url)
        flag = True
        product_type = None
        for product_type_url in product_type_urls:
            product_type_name, description_type = get_product_type_info(product_type_url)
            if flag:
                product_type = create_product_type(competitor, product_type_name, None, description_type)
                flag = False
            else:
                product_type = create_product_type(competitor, product_type_name, None, description_type, product_type)

        product = create_product(product_name, product_title, product_description, product_images,
                       product_stock_status, meta, product_type=product_type)

        for variant_url in variant_urls:
            variant_title, variant_descripiton, variant_images, variant_item_code, variant_availability, \
            variant_standard_pack, variant_pricing, variant_specifications, svg_diagram_url = get_variant_info(variant_url)

            variant = create_variant(product, variant_title, variant_descripiton, variant_images, variant_item_code, variant_availability,
                                     variant_standard_pack, variant_pricing, variant_specifications)
            #svg_code = get_svg_code(svg_diagram_url)
            #save_svg_diagram(variant, svg_code)


def get_product_type_info(url):
    browser = get_browser(url)
    name = ''
    description = ''
    name_tags = browser.find_elements_by_tag_name('h2')
    if name_tags:
        name = name_tags[0].text
    description_tags = browser.find_elements_by_class_name('scrollContent')
    if description_tags:
        description = description_tags[0].text
    browser.quit()
    return name, description


def get_products_urls_list(url):
    response = get_response(url)
    soup = get_soup(response)
    products = soup.find_all("div", {"class": "allproductsdiv"})
    product_urls = []
    for product in products:
        product_urls.append(MOCAP_BASE_URL + product.a['href'])
    return product_urls


def get_product_info(url):
    browser = get_browser(url)
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
    try:
        variants_table = browser.find_element_by_id('SZCHARTID') if browser.find_element_by_id('SZCHARTID') else None
    except Exception as e:
        pass
    else:
        table_row_elements = variants_table.find_elements_by_tag_name('tr') if variants_table else None
        if table_row_elements:
            for tr in table_row_elements[1:-1]:
                variant_link_tags = tr.find_elements_by_class_name('crtlnk')
                if variant_link_tags:
                    variant_link = variant_link_tags[0].get_attribute('href')
                    variant_links.append(variant_link)

    browser.quit()
    return product_type_urls, variant_links, product_name, product_title, product_description, product_images, stock_status, meta


def get_variant_info(url):
    browser = get_browser(url)
    title = ''
    item_code = ''
    title_divs = browser.find_elements_by_class_name('product-name')
    if title_divs:
        title_div = title_divs[0]
        title_tag = title_div.find_element_by_tag_name('h1')
        title = title_tag.text if title_tag else ''
        item_code = title_div.find_element_by_tag_name('span').text
    descripiton = ''
    descripiton_divs = browser.find_elements_by_class_name('box-description')
    if descripiton_divs:
        descripiton_div = descripiton_divs[0]
        descripiton = descripiton_div.text
    availability = 'in stock'
    standard_pack = 0

    specifications = {}
    specifications_divs = browser.find_elements_by_class_name('szinfobox')
    if specifications_divs:
        specifications_div = specifications_divs[0]
        bulk_specification_text = specifications_div.text.split('\n')
        for bulk_spec in bulk_specification_text:
            spec_key,spec_value = bulk_spec.split('...')
            specifications[spec_key.strip()] = spec_value.strip()

    variant_images = []
    image_urls = browser.find_elements_by_id('zoom1')
    if image_urls:
        image_url = image_urls[0].get_attribute('href')
        variant_images.append(image_url)

    diagram_div = browser.find_element_by_id('szimagbox')
    svg_diagram_url = diagram_div.find_element_by_tag_name('object').get_attribute('data')

    pricing = {}
    quantities = []
    unit_prices = []
    pricing_options = browser.find_element_by_id('qty').find_elements_by_tag_name('option')
    flag = True
    for option in pricing_options:
        if flag:
            flag = False
            continue
        option.click()
        #sleep(1)
        quantity = option.text
        price = browser.find_element_by_id('additmtot0').text
        quantities.append(quantity)
        unit_prices.append(price)
    pricing['quantity'] = quantities
    pricing['unit_price'] = unit_prices
    browser.quit()
    return title, descripiton, variant_images, item_code, availability, standard_pack, pricing, specifications, svg_diagram_url


def get_svg_code(url):
    browser = get_browser(url)
    svg_source_code = browser.page_source
    browser.quit()
    return svg_source_code