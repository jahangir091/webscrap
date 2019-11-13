from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render

from store_data.models import ProductType

# Create your views here.

from store_data.forms import DataUploadForm


def upload(request):

    if request.method == 'GET':
        context_dict = {
            'form' : DataUploadForm,
            'name' : 'jaha',
        }
        return render(request,
            'upload.html', context_dict)

    elif request.method == 'POST':

        import pdb;
        pdb.set_trace()
        product_type_id = request.POST['product_type']
        product_type = ProductType.objects.get(id=product_type_id)
        product_name = request.POST['name']
        product_description = request.POST['description']
        product_helpful_hints = request.POST['helpful_hints']

        product_images = request.FILES.getlist('images')
        variants_csv = request.FILES.getlist('variants')
        variant_name = request.POST['variant_name']
        return HttpResponseRedirect(
                reverse(
                    'index',
                )
            )
