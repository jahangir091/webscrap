from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from autoslug import AutoSlugField
from jsonfield import JSONField


class Competitor(models.Model):
    """

    """
    name = models.CharField(max_length=250, verbose_name=_('manufacturer name'), help_text=_('name of a competitor'))
    url = models.URLField(max_length=2000, null=True, blank=True, verbose_name=_('competitor url'),
                          help_text=_('base url of a competitor'))
    slug = AutoSlugField(max_length=30, populate_from='name', unique=True)
    image = models.ImageField(upload_to='competitors', blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def product_type_images_directory_path(instance, filename):
    return '{0}/{1}'.format(instance.image_location, filename)


class ProductType(models.Model):
    """

    """
    parent = models.ForeignKey('self', blank=True, null=True, related_name='childrens', on_delete=models.CASCADE)
    competitor = models.ForeignKey(Competitor, related_name='product_types', on_delete=models.CASCADE)
    name = models.CharField(max_length=50, blank=True, null=True)
    slug = AutoSlugField(max_length=30, unique=True,populate_from='name')
    image_location = models.CharField(max_length=1000, blank=True, null=True)
    image = models.ImageField(upload_to='product_types', blank=True, null=True)
    description = models.CharField(max_length=1500, blank=True, null=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        # import pdb; pdb.set_trace()
        if self.parent:
            self.image_location = self.parent.image_location + '/' + self.name
        else:
            self.image_location = 'product_type/' + str(self.name)
        super(ProductType, self).save(*args, **kwargs)


class Product(models.Model):
    """

    """
    name = models.CharField(max_length=50, blank=True, null=True)
    title = models.CharField(max_length=50, blank=True, null=True)
    slug = AutoSlugField(max_length=30, unique=True, populate_from='name')
    product_type = models.ForeignKey(ProductType, related_name='products', on_delete=models.CASCADE)
    short_description = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    url = models.URLField(max_length=2000, null=True, blank=True, verbose_name=_('product url'),
                          help_text=_('base url of a competitor'))
    stock_status = models.CharField(max_length=20, blank=True, null=True, verbose_name=_('stock status'), help_text=_('stock status of this product'))
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


def product_images_directory_path(instance, filename):
    return '{0}/products/{1}'.format(instance.product.product_type.image_location, filename)


class ProductImage(models.Model):
    """

    """
    title = models.CharField(max_length=50, blank=True, null=True)
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products')


class Variant(models.Model):
    """

    """
    title = models.CharField(max_length=300, blank=True, null=True)
    slug = AutoSlugField(max_length=30, unique=True, populate_from='title')
    description = models.CharField(max_length=2000, blank=True, null=True)
    product = models.ForeignKey(Product, verbose_name=_('product'), help_text=_('product name of this variant'), on_delete=models.CASCADE, related_name='variants')
    item_code = models.CharField(max_length=30, blank=True, null=True)
    availability = models.CharField(max_length=50, blank=True, null=True, help_text=_('availability of this product'))
    standard_pack_size = models.IntegerField(blank=True, default=0, help_text =_('number of items in a pack'))
    pricing = JSONField()
    specification = JSONField()


def variant_images_directory_path(instance, filename):
    return 'variants/{0}/{1}'.format(instance.variant.product.name, filename)


class VariantImage(models.Model):
    """

    """
    title = models.CharField(max_length=50, blank=True, null=True)
    variant = models.ForeignKey(Variant, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='variants')