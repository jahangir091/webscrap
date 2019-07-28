from scrapyProject.store_data.models import Competitor, ProductType, Product, Variant, ProductImage, VariantImage


def create_competitor(comperitor_name, url):
    competitor = Competitor()
    competitor.name = comperitor_name
    competitor.url = url
    competitor = competitor.save()
    return competitor


def create_product_type(competitor, name, image, description, parent=None):
    product_type = ProductType()
    product_type.competitor = competitor
    product_type.name = name
    product_type.image = image
    product_type.description = description
    if parent:
        product_type.parent = parent
    product_type.save()
    return product_type


def create_product(product_name, product_title, product_description, product_in_stock, product_type=None):
    pass


def create_variant(product, **kwargs):
    pass
