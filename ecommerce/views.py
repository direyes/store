from django.http import HttpResponseRedirect
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from ecommerce.business_logic import confirm_purchase
from purchase.models import Product
from purchase.models import Purchase
from ecommerce.forms import PurchaseProductForm


class IndexView(TemplateView):
    template_name = 'ecommerce/index.html'

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        context['products'] = Product.objects.all()
        return context


class ProductView(DetailView):
    model = Product
    template_name = 'purchase/purchase_form.html'
    pk_url_kwarg = 'product_pk'


class PurchaseView(TemplateView):
    template_name = 'purchase/purchase_form.html'

    def get_context_data(self, **kwargs):
        kwargs = super(PurchaseView, self).get_context_data(**kwargs)
        kwargs['object'] = kwargs.get('form').cleaned_data['product']
        return kwargs

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())

    def post(self, request, *args, **kwargs):
        form = PurchaseProductForm(data=request.POST)
        if not form.is_valid():
            return self.form_invalid(form)
        self.form_valid(form)


class ConfirmPaymentView(DetailView):
    model = Purchase
    pk_url_kwarg = 'purchase_pk'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        confirm_purchase(self.object)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
