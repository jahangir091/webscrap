from django import forms
from store_data.models import Competitor, ProductType, ProductImage
from django.utils.translation import ugettext_lazy as _

product_types = ProductType.objects.all()
ptypes = []

for pt in product_types:
    toup = []
    toup.append(pt.id)
    toup.append(pt.name)
    ptypes.append(tuple(toup))


class DataUploadForm(forms.Form):

    product_type = forms.ChoiceField(choices=ptypes)
    name = forms.CharField(label='Product name', max_length=1000)
    description = forms.CharField(label='Product description', widget=forms.Textarea, max_length=100000)
    helpful_hints = forms.CharField(label='Helpful hints', widget=forms.Textarea, max_length=100000)
    images = forms.FileField(label='Select images', widget=forms.ClearableFileInput(attrs={'multiple': True}))
    variant_name = forms.CharField(label='Variant name', max_length=500)
    variants = forms.FileField(label='Select variants')