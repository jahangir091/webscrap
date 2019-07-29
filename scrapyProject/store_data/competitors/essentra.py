import pdb
import requests
from bs4 import BeautifulSoup as soup

from store_data.base import create_competitor, create_product_type, create_product, create_variant, get_response

competitor_name = "Essentra"
base_url = 'https://www.essentracomponents.com'

product_type_1_urls = ['https://www.essentracomponents.com/en-us/electronics']


def load_essentra_products():
    competitor = create_competitor(competitor_name, base_url)
    for product_type_1_url in product_type_1_urls:
        response = get_response(product_type_1_url)
        product_type_2_urls, product_type_1_name, product_type_1_image, product_type_1_description = get_product_type_1_name_image_description(response)
        product_type_1 = create_product_type(competitor, product_type_1_name, product_type_1_image, product_type_1_description)

        for product_type_2_url in product_type_2_urls:
            response = get_response(product_type_2_url)
            product_type_3_urls, product_type_2_name, product_type_2_image, product_type_2_description = get_product_type_2_name_image_description(response)
            product_type_2 = create_product_type(competitor, product_type_2_name, product_type_2_image, product_type_2_description, parent=product_type_1)

            for product_type_3_url in product_type_3_urls:
                response = get_response(product_type_3_url)
                product_urls, product_type_3_name, product_type_3_image, product_type_3_description = get_product_type_3_name_image_description(response)
                product_type_3 = create_product_type(competitor, product_type_3_name, product_type_3_image,product_type_3_description, parent=product_type_2)

                for product_url in product_urls:
                    response = get_response(product_url)
                    variant_urls, product_name, product_title, product_description, product_images, product_stock_status = get_pdoduct_info(response)
                    product = create_product(product_name, product_title, product_description, product_images, product_stock_status, product_type=product_type_3)

                    for variant_url in variant_urls:
                        response = get_response(variant_url)
                        variant_info = get_variant_info(response)
                        variant = create_variant(product, **variant_info)


def get_soup(response):
    html_page = response.text
    page_soup = soup(html_page, 'html.parser')
    return page_soup


def get_product_type_1_name_image_description(response):
    soup = get_soup(response)
    type_name = soup.find("div", {"class": "container container-with-padding"}).h1.text
    type_image = ''
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
    type_image = soup.find("div", {"class": "col-lg-4 category-primary-item row align-content-start"}).img['src']
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
    type_image = ''
    type_description = ''
    product_link_divs = soup.find_all("div", {"class": "product-wrapper"})
    product_links = []
    for div in product_link_divs:
        product_link = base_url + div.a['href'] + '?pageSize=All'
        product_links.append(product_link)
    return product_links, type_name, type_image, type_description


def get_pdoduct_info(response):
    soup = get_soup(response)
    product_name = soup.find("div", {"class": "prod-intro"}).h1.text
    product_title = ''
    product_description = soup.find("p", {"class": "prod-desc"}).text
    stock_status = soup.find("div", {"class": "prod-intro"}).strong.text
    product_images = []
    image_divs = soup.find_all("div", {"class": "prod-gallery-item"})
    for image_div in image_divs:
        image_url = base_url + image_div.img['src']
        product_images.append(image_url)
    variant_link_rows = soup.find_all("tr", {"class": "basic-info"})
    variant_links = []
    for row in variant_link_rows:
        variant_link = base_url + row.find("a", {"class": "tealium-skuLinkPgroup"})['href']
        variant_links.append(variant_link)
    return variant_links, product_name, product_title, product_description, product_images, stock_status


def get_variant_info(response):
    soup = get_soup(response)
    pdb.set_trace()
    title = soup.find("div", {"class": "prod-intro"}).h1.text
    descripiton = soup.find("p", {"class": "prod-desc"}).text
    variant_images = []
    image_divs = soup.find_all("div", {"class": "prod-gallery-item"})
    for image_div in image_divs:
        image_url = base_url + image_div.img['src']
        variant_images.append(image_url)
    item_code = soup.find("p", {"class": "prod-meta"}).find_all("span", {"class":""})[1].text
    availability = soup.find("span", {"class": "overrideSkuStock 114A"}).text.strip()

    ##---------------------------------------------------------------------->

    style = ''
    color = ''
    panel_thickness_imperial = ''
    panel_thickness_metric = ''
    series = ''
    maximum_operating_temperature_imperial = ''
    maximum_operating_temperature_metric = ''
    minimum_operating_temperature_imperial = ''
    minimum_operating_temperature_metric = ''
    operating_temperature_range_imperial = ''
    operating_temperature_range_metric = ''
    overall_width_metric = ''
    overall_width_imperial = ''
    full_material = ''
    material_flammability_standard = ''
    package_quantity = ''
    dict = {}
    dict['name'] = 'variant1'
    return dict
