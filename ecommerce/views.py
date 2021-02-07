from django.http import HttpResponseRedirect
from django.urls import reverse_lazy
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from ecommerce.business_logic import confirm_purchase, reverse_purchase
from ecommerce.forms import PurchaseProductForm
from purchase.choices import REVERSED
from purchase.models import Product
from purchase.models import PurchaseItem
from purchase.models import Purchase


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


class PurchaseDetailsView(DetailView):
    model = Purchase
    pk_url_kwarg = 'purchase_pk'

    def get_context_data(self, **kwargs):
        context = super(PurchaseDetailsView, self).get_context_data(**kwargs)
        context['items'] = PurchaseItem.objects.filter(purchase=self.object)
        context['title'] = context['object'].get_purchase_description()
        return context


class ConfirmPaymentView(PurchaseDetailsView):

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        confirm_purchase(self.object)
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class PurchaseListView(ListView):
    model = Purchase


class PurchaseReverseView(DeleteView):
    model = Purchase
    success_url = '/purchase-details/{id}/'
    pk_url_kwarg = 'purchase_pk'

    def delete(self, request, *args, **kwargs):
        """
        Call the delete() method on the fetched object and then redirect to the
        success URL.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        reverse_purchase(self.object)
        return HttpResponseRedirect(success_url)
