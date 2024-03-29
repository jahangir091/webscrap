import json

from store_data.base import create_competitor, create_product_type, create_product, create_variant, get_response
from store_data.base import get_soup

competitor_name = "Essentra"
base_url = 'https://www.essentracomponents.com'

product_type_1_urls = ['https://www.essentracomponents.com/en-us/protection',
                       'https://www.essentracomponents.com/en-us/electronics',
                       'https://www.essentracomponents.com/en-us/fasteners',
                       'https://www.essentracomponents.com/en-us/hardware']


def load_essentra_products():
    name  = 'essentra'
    competitor = create_competitor(competitor_name, base_url, name)
    url_no = 0
    for product_type_1_url in product_type_1_urls:
        url_no += 1
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
                        print("{4} Loading product {0}-->{1}-->{2}-->{3}".format(product_type_1, product_type_2, product_type_3, product, url_no) )
                        variant = create_variant(product, v_title, v_descripiton, v_variant_images, v_item_code, v_availability, v_standard_pack, v_pricing, v_specifications)
                        variant_count += 1
                    print("loaded {0} variants of product {1}".format(variant_count, product.name))


def get_product_type_1_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding"}).h1.text.strip() if soup.find("div", {"class": "container container-with-padding"}) else ''
    type_image = None
    type_description = ''
    sub_type_link_divs = soup.find_all("div", {"class": "row category-wrapper has-margin-top"})
    sub_type_links = []
    for link_div in sub_type_link_divs:
        sub_type_links.append(base_url + link_div.find("h2", {"class": "is-bold category-primary-title d-none d-lg-block"}).a['href']) if link_div.find("h2", {"class": "is-bold category-primary-title d-none d-lg-block"}) else ''

    return sub_type_links, type_name, type_image, type_description


def get_product_type_2_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding"}).h1.text.strip() if soup.find("div", {"class": "container container-with-padding"}) else ''
    type_image = base_url + soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}).img['src'] if soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}) else ''
    type_description = soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}).span.text.strip() if soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}) else ''
    sub_type_link_divs = soup.find("div", {"class": "col-lg-8 category-items"}).find_all("li", {"class": "col-6 category-item"}) if soup.find("div", {"class": "col-lg-8 category-items"}) else []
    sub_type_links = []
    for li in sub_type_link_divs:
        sub_type_links.append(base_url + li.a['href'] + '?pageSize=All') if li else ''
    return sub_type_links, type_name, type_image, type_description


def get_product_type_3_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding shop-page"}).h1.text.strip()
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
    product_name = soup.find("div", {"class": "prod-intro"}).h1.text.strip() if soup.find("div", {"class": "prod-intro"}) else ''
    product_title = ''
    meta = soup.head.find("meta", {"name":"description"}).attrs['content'] if soup.head.find("meta", {"name":"description"}) else ''
    product_description = soup.find("p", {"class": "prod-desc"}).text.strip() if soup.find("p", {"class": "prod-desc"}) else ''
    stock_status = soup.find("div", {"class": "prod-intro"}).strong.text.strip() if soup.find("div", {"class": "prod-intro"}) else ''
    product_images = []
    image_divs = soup.find_all("div", {"class": "prod-gallery-item"})
    for image_div in image_divs:
        product_images.append(base_url + image_div.img['src']) if image_div.find('img') else ''

    variant_link_rows = soup.find_all("tr", {"class": "basic-info"})
    variant_links = []
    for row in variant_link_rows:
        variant_links.append(base_url + row.find("a", {"class": "tealium-skuLinkPgroup"})['href']) if row.find("a", {"class": "tealium-skuLinkPgroup"}) else ''
    return variant_links, product_name, product_title, product_description, product_images, stock_status, meta


def get_variant_info(response):
    soup = get_soup(response)
    title = soup.find("div", {"class": "prod-intro"}).h1.text.strip() if soup.find("div", {"class": "prod-intro"}) else ''
    descripiton = soup.find("p", {"class": "prod-desc"}).text.strip() if soup.find("p", {"class": "prod-desc"}) else ''
    variant_images = []
    image_divs = soup.find_all("div", {"class": "prod-gallery-item"})
    for image_div in image_divs:
        variant_images.append(base_url + image_div.img['src']) if image_div.find('img') else ''

    # item_code = soup.find("p", {"class": "prod-meta"}).find_all("span")[1].text
    item_code_spans = soup.find("p", {"class": "prod-meta"}).find_all("span") if soup.find("p", {"class": "prod-meta"}) else []
    item_code = item_code_spans[1].text.strip() if item_code_spans else ''

    # availability = soup.find("p", {"class": "prod-meta"}).find_all("span")[2].text
    availability_spans = soup.find("p", {"class": "prod-meta"}).find_all("span") if soup.find("p", {"class": "prod-meta"}) else []
    availability = availability_spans[2].text.strip() if availability_spans else ''

    #standard_pack = soup.find("div", {"id": "broadleaf-sku-details"}).find_all("span")[1].text
    standard_pack_spans = soup.find("div", {"id": "broadleaf-sku-details"}).find_all("span") if soup.find("div", {"id": "broadleaf-sku-details"}) else []
    standard_pack = standard_pack_spans[1].text.strip() if standard_pack_spans else 0
    try:
        standard_pack = int(standard_pack)
    except Exception as e:
        standard_pack = 0
        pass

    pricing = {}
    pricing_table = soup.find("table", {"class": "table sku-price-table"})
    pricing_table_items = pricing_table.tbody.find_all("tr") if pricing_table else []

    quantities = []
    unit_prices = []
    for tr in pricing_table_items:
        quantities.append(tr.find_all("td")[0].find_all("b")[0].text.strip() + tr.find_all("td")[0].find_all("b")[1].text.strip())
        unit_prices.append(tr.find_all("td")[1].text.strip())
    pricing['quantity'] = quantities
    pricing['unit_price'] = unit_prices

    specifications = {}
    specifications_div = soup.find("div", {"class":"section has-essentra-row"})
    specifications_table = specifications_div.table if specifications_div else None
    specifications_table_rows = specifications_table.tbody.find_all("tr") if specifications_table else []

    for row in specifications_table_rows:
        key = row.th.text.replace('\n', '')
        if 'attr-dim-METRIC' in row.attrs['class']:
            key += 'metric'
        if 'attr-dim-IMPERIAL' in row.attrs['class']:
            key += 'imperial'
        value = row.td.text.replace('\n', '')
        specifications[key] = value

    return title, descripiton, variant_images, item_code, availability, standard_pack, pricing, specifications
