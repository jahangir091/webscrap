import json
from bs4 import BeautifulSoup as soup

from store_data.base import create_competitor, create_product_type, create_product, create_variant, get_response

competitor_name = "Essentra"
base_url = 'https://www.essentracomponents.com'

product_type_1_urls = ['https://www.essentracomponents.com/en-us/protection',
                       'https://www.essentracomponents.com/en-us/electronics',
                       'https://www.essentracomponents.com/en-us/fasteners',
                       'https://www.essentracomponents.com/en-us/hardware']


def load_essentra_products():
    competitor = create_competitor(competitor_name, base_url)
    for product_type_1_url in product_type_1_urls:
        response = get_response(product_type_1_url)
        if response:
            product_type_2_urls, product_type_1_name, product_type_1_image, product_type_1_description = get_product_type_1_name_image_description(response)
        else:
            continue
        product_type_1 = create_product_type(competitor, product_type_1_name, product_type_1_image, product_type_1_description)

        for product_type_2_url in product_type_2_urls:
            response = get_response(product_type_2_url)
            if response:
                product_type_3_urls, product_type_2_name, product_type_2_image, product_type_2_description = get_product_type_2_name_image_description(response)
            else:
                continue
            product_type_2 = create_product_type(competitor, product_type_2_name, product_type_2_image, product_type_2_description, parent=product_type_1)

            for product_type_3_url in product_type_3_urls:
                response = get_response(product_type_3_url)
                if response:
                    product_urls, product_type_3_name, product_type_3_image, product_type_3_description = get_product_type_3_name_image_description(response)
                else:
                    continue
                product_type_3 = create_product_type(competitor, product_type_3_name, product_type_3_image,product_type_3_description, parent=product_type_2)

                for product_url in product_urls:
                    response = get_response(product_url)
                    if response:
                        variant_urls, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(response)
                    else:
                        continue
                    product = create_product(product_name, product_title, product_description, product_images, product_stock_status, meta, product_type=product_type_3)
                    variant_count = 0
                    for variant_url in variant_urls:
                        response = get_response(variant_url)
                        if response:
                            v_title, v_descripiton, v_variant_images, v_item_code, v_availability, v_standard_pack, v_pricing, v_specifications = get_variant_info(response)
                        else:
                            continue
                        print("Loading product {0}-->{1}-->{2}-->{3}".format(product_type_1, product_type_2, product_type_3, product) )
                        variant = create_variant(product, v_title, v_descripiton, v_variant_images, v_item_code, v_availability, v_standard_pack, v_pricing, v_specifications)
                        variant_count += 1
                    print("loaded {0} variants of product {1}".format(variant_count, product.name))


def get_soup(response):
    html_page = response.text
    page_soup = soup(html_page, 'html.parser')
    return page_soup


def get_product_type_1_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding"}).h1.text
    type_image = None
    type_description = ''
    sub_type_link_divs = soup.find_all("div", {"class": "row category-wrapper has-margin-top"})
    sub_type_links = []
    for link_div in sub_type_link_divs:
        link = base_url + link_div.find("h2", {"class": "is-bold category-primary-title d-none d-lg-block"}).a['href']
        sub_type_links.append(link)

    return sub_type_links, type_name, type_image, type_description


def get_product_type_2_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding"}).h1.text
    type_image = base_url + soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}).img['src']
    type_description = soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}).span.text
    sub_type_link_divs = soup.find("div", {"class": "col-lg-8 category-items"}).find_all("li", {"class": "col-6 category-item"})
    sub_type_links = []
    for li in sub_type_link_divs:
        link = base_url + li.a['href'] + '?pageSize=All'
        sub_type_links.append(link)
    return sub_type_links, type_name, type_image, type_description


def get_product_type_3_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding shop-page"}).h1.text
    type_image = None
    type_description = ''
    product_link_divs = soup.find_all("div", {"class": "product-wrapper"})
    product_links = []
    for div in product_link_divs:
        product_link = base_url + div.a['href'] + '?pageSize=All'
        product_links.append(product_link)
    return product_links, type_name, type_image, type_description


def get_product_info(response):
    soup = get_soup(response)
    product_name = soup.find("div", {"class": "prod-intro"}).h1.text
    product_title = ''
    product_description = soup.find("p", {"class": "prod-desc"}).text
    stock_status = soup.find("div", {"class": "prod-intro"}).strong.text
    product_images = []
    image_divs = soup.find_all("div", {"class": "prod-gallery-item"})
    meta = soup.head.find("meta", {"name":"description"}).attrs['content']

    for image_div in image_divs:
        image_url = base_url + image_div.img['src']
        product_images.append(image_url)
    variant_link_rows = soup.find_all("tr", {"class": "basic-info"})
    variant_links = []
    for row in variant_link_rows:
        variant_link = base_url + row.find("a", {"class": "tealium-skuLinkPgroup"})['href']
        variant_links.append(variant_link)
    return variant_links, product_name, product_title, product_description, product_images, stock_status, meta


def get_variant_info(response):
    soup = get_soup(response)
    title = soup.find("div", {"class": "prod-intro"}).h1.text
    descripiton = soup.find("p", {"class": "prod-desc"}).text
    variant_images = []
    image_divs = soup.find_all("div", {"class": "prod-gallery-item"})
    for image_div in image_divs:
        image_url = base_url + image_div.img['src']
        variant_images.append(image_url)
    item_code = soup.find("p", {"class": "prod-meta"}).find_all("span")[1].text
    availability = soup.find("p", {"class": "prod-meta"}).find_all("span")[2].text
    standard_pack = soup.find("div", {"id": "broadleaf-sku-details"}).find_all("span")[1].text
    pricing = {}
    pricing_table = soup.find("table", {"class": "table sku-price-table"})
    if pricing_table:
        pricing_table_items = pricing_table.tbody.find_all("tr")
    else:
        pricing_table_items = []
    quantities = []
    unit_prices = []
    for tr in pricing_table_items:
        quantities.append(tr.find_all("td")[0].find_all("b")[0].text + tr.find_all("td")[0].find_all("b")[1].text)
        unit_prices.append(tr.find_all("td")[1].text)
    pricing['quantity'] = quantities
    pricing['unit_price'] = unit_prices

    specifications = {}
    specifications_div = soup.find("div", {"class":"section has-essentra-row"})
    specifications_table = specifications_div.table
    specifications_table_rows = specifications_table.tbody.find_all("tr")
    for row in specifications_table_rows:
        key = row.th.text.replace('\n', '')
        if 'attr-dim-METRIC' in row.attrs['class']:
            key += 'metric'
        if 'attr-dim-IMPERIAL' in row.attrs['class']:
            key += 'imperial'
        value = row.td.text.replace('\n', '')
        specifications[key] = value

    return title, descripiton, variant_images, item_code, availability, standard_pack, pricing, specifications
