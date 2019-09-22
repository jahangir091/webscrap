
from store_data.base import create_competitor, create_product_type, create_product, create_variant, get_response
from store_data.base import get_soup
from time import sleep

product_type_urls = [
    "https://www.epsi.com/caps",
    "https://www.epsi.com/plugs",
    "https://www.epsi.com/tapes-and-discs",
    "https://www.epsi.com/hooks"
]

competitor_name = 'epsi'

base_url = 'https://www.epsi.com'


def load_epsi_products():
    competitor = create_competitor(competitor_name, base_url)
    for url in product_type_urls:
        product_type_name = url.split('/')[3]
        product_type = create_product_type(competitor, product_type_name, None, '')
        response = get_response(url)
        print('wait 10 seconds')
        sleep(10)
        product_urls = get_product_urls(response)
        for product_url in product_urls:
            response = get_response(product_url)
            print('wait 10 seconds')
            sleep(10)
            variants, product_name, product_title, product_description, product_images, product_stock_status, meta = get_product_info(response)
            product = create_product(product_name, product_title, product_description, product_images,
                                     product_stock_status, meta, product_type=product_type)
            variant_count = 0
            for variant in variants:
                print("Loading product {0}-->{1}".format(product_type, product))
                variant = create_variant(product, variant['title'], variant['descripiton'], variant['variant_images'], variant['item_code'], variant['availability'],
                                         variant['standard_pack'], variant['pricing'], variant['specifications'])
                variant_count += 1
            print("loaded {0} variants of product {1}".format(variant_count, product.name))


def get_product_urls(response):
    soup = get_soup(response)
    products = soup.find_all('div', {'class': 'product-details span6'})
    product_urls = []
    for product in products:
        product_url = base_url + product.h5.a['href']
        product_urls.append(product_url)

    return product_urls


def get_product_info(response):

    soup = get_soup(response)
    product_name = soup.find('div', {'id': 'product'}).h1.text.strip() if soup.find('div', {'id': 'product'}) else ''
    product_title = soup.find('div', {'id': 'product'}).h1.text.strip() if soup.find('div', {'id': 'product'}) else ''
    meta = soup.head.find("meta", {"name": "description"}).attrs['content'] if soup.head.find("meta", {"name": "description"}) else ''
    stock_status = ''

    #fetch product images
    product_images = []
    img_url = base_url + soup.find('div', {'id': 'product-page-html'}).img['src'] if soup.find('div', {'id': 'product-page-html'}) else None
    if img_url:
        product_images.append(img_url)
    overview_div = soup.find('div', {'id': 'overview'}) if soup.find('div', {'id': 'overview'}) else None
    overview_paragraphs = overview_div.find_all('p') if overview_div else None

    #fetch product description
    product_description = soup.find('div', {'id':'overview'}).text.strip() if soup.find('div', {'id':'overview'}) else ''

    #fetch product variants
    variants = []
    variants_table = soup.find('table', {'id':'product-items'}) if soup.find('table', {'id':'product-items'}) else None
    trs = variants_table.tbody.find_all('tr', {'class':'product-item'}) if variants_table else []
    for tr in trs:
        variant = {}

        tds = tr.find_all('td')
        variant['title'] = tds[1].find('div', {'class':'product-item-name'}).text.strip() if tds[1].find('div', {'class':'product-item-name'}) else product_title
        variant['descripiton'] = ''
        variant['variant_images'] = []
        variant['item_code'] = tr.find('div', {'itemprop':'sku'}).text.strip() if tr.find('div', {'itemprop':'sku'}) else None
        variant['availability'] = ''
        variant['standard_pack'] = 0

        pricing = {}
        quantities = []
        unit_prices = []
        variant_unit_price = tr.find('div', {'itemprop':'price'}).text.strip() if tr.find('div', {'itemprop':'price'}) else None
        quantities.append(variant_unit_price.split('/')[1] if variant_unit_price else '0')
        unit_prices.append(variant_unit_price.split('/')[0] if variant_unit_price else '0')
        pricing['quantity'] = quantities
        pricing['unit_price'] = unit_prices
        variant['pricing'] = pricing

        specifications = {}
        spec_keys = []
        ths = variants_table.thead.find_all('th')
        for th in ths[2:-2]:
            spec_keys.append(th.text.strip())

        i = 2
        for spec_key in spec_keys:
            key = spec_key
            value = tds[i].text.strip()
            i += 1
            specifications[key] = value
        variant['specifications'] = specifications

        variants.append(variant)

    #test
    #https: // www.epsi.com / hksc - series - sheet - and -pipe - suspender - hook

    return variants, product_name, product_title, product_description, product_images, stock_status, meta

