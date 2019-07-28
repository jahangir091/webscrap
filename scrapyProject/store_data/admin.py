from django.contrib import admin

from store_data.models import Competitor, ProductType, Product, ProductImage, Variant, VariantImage

# Register your models here.


admin.site.register(Competitor)
admin.site.register(Product)
admin.site.register(ProductType)
admin.site.register(ProductImage)
admin.site.register(Variant)
admin.site.register(VariantImage)
