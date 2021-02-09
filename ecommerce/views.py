from django.contrib import messages
from django.http import Http404
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import DeleteView
from django.views.generic import ListView
from django.views.generic.base import TemplateView
from django.views.generic.detail import DetailView

from ecommerce.business_logic import confirm_purchase
from ecommerce.business_logic import reverse_purchase
from ecommerce.exceptions import ConnectionTPaga
from ecommerce.exceptions import ErrorTPaga
from ecommerce.forms import PurchaseProductForm
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

    def get_product(self):
        """Return the product for new purchase"""

        queryset = Product.objects.all()
        # Next, try looking up by primary key.
        pk = self.kwargs.get('product_pk')
        if pk is not None:
            queryset = queryset.filter(pk=pk)

        # If none of those are defined, it's an error.
        if pk is None:
            raise AttributeError(
                "Generic detail view %s must be called with either an object "
                "pk or a slug in the URLconf." % self.__class__.__name__
            )

        try:
            # Get the single item from the filtered queryset
            obj = queryset.get()
        except queryset.model.DoesNotExist:
            raise Http404(_("No %(verbose_name)s found matching the query") %
                          {'verbose_name': queryset.model._meta.verbose_name})
        return obj

    def get_context_data(self, **kwargs):
        kwargs = super(PurchaseView, self).get_context_data(**kwargs)
        kwargs['object'] = self.get_product()
        return kwargs

    def form_invalid(self, form):
        """If the form is invalid, render the invalid form."""
        return self.render_to_response(self.get_context_data(form=form))

    def form_valid(self, form):
        try:
            self.object = form.save()
        except (ErrorTPaga, ConnectionTPaga) as e:
            messages.warning(self.request, e.__str__())
            return HttpResponseRedirect('/')

        return HttpResponseRedirect(self.object.payment_url)

    def post(self, request, *args, **kwargs):
        form = PurchaseProductForm(data=request.POST)
        if not form.is_valid():
            return self.form_invalid(form)
        return self.form_valid(form)


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
        try:
            confirm_purchase(self.object)
        except (ErrorTPaga, ConnectionTPaga) as e:
            messages.warning(self.request, e.__str__())
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
        try:
            reverse_purchase(self.object)
        except (ErrorTPaga, ConnectionTPaga) as e:
            messages.warning(self.request, e.__str__())
        return HttpResponseRedirect(success_url)
