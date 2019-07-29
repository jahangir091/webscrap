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
                    variant_urls, product_name, product_title, product_description, product_in_stock = get_pdoduct_info(response)
                    product = create_product(product_name, product_title, product_description, product_in_stock, product_type=product_type_3)

                    for variant_url in variant_urls:
                        response = get_response(variant_url)
                        variant_info = get_variant_info(response)
                        variant = create_variant(product, **variant_info)

    response = requests.get(base_url)
    html_page = response.text
    page_soup = soup(html_page, 'html.parser')

    categories_level_2 = page_soup.find_all("div", {"class": "row category-wrapper has-margin-top"})

    counter = 1

    for category in categories_level_2:
        # pdb.set_trace()
        product_name = category.find("h2", {"class": "is-bold category-primary-title d-none d-lg-block"}).a.text.strip()
        product_link = category.find("h2", {"class": "is-bold category-primary-title d-none d-lg-block"}).a['href']
        product_link = product_link

        # product_short_description = container.find("div", {"class":"content"}).text.strip()
        # product_image =  container.find("div", {"class":"fullimage"}).img['src']
        # product_stock_staus = container.find("div", {"class":"span2 extro"}).p.text.strip()
        # number_of_sub_products_string = container.find("a", {"class":"itemVarBtn"}).span.text.strip()
        # number_of_sub_products = int(''.join(filter(str.isdigit, str(number_of_sub_products_string))))

        print(counter)
        print(product_name)
        print(product_link)
        # print(product_short_description)
        # print(product_image)
        # print(product_stock_staus)
        # print(number_of_sub_products)
        counter += 1

        # f.write(product_name + ", "+ product_short_description +", "+ product_image +", "+ product_stock_staus +", " + str(number_of_sub_products) +"\n")
    # f.close()

def get_soup(response):
    html_page = response.text
    page_soup = soup(html_page, 'html.parser')
    return page_soup


def get_product_type_1_name_image_description(response):
    soup = get_soup(response)
    name = soup.find("div", {"class": "container container-with-padding"}).h1.text
    image = ''
    description = ''
    link_divs = soup.find_all("div", {"class": "row category-wrapper has-margin-top"})
    links = []
    for div in link_divs:
        link = base_url + div.find("h2", {"class": "is-bold category-primary-title d-none d-lg-block"}).a['href']
        links.append(link)

    return links, name, image, description


def get_product_type_2_name_image_description(response):
    return [], 2, 3, 4


def get_product_type_3_name_image_description(response):
    return [], 2, 3, 4


def get_pdoduct_info(response):
    return [], 2, 3, 4, 5


def get_variant_info(url):
    dict = {}
    dict['name'] = 'variant1'
    return dict
