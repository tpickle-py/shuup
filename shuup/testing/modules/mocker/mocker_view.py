import datetime
import random

from django import forms
from django.conf import settings
from django.contrib import messages
from django.utils.timezone import now
from django.views.generic import FormView

from shuup.testing.factories import (
    create_random_company,
    create_random_contact_group,
    create_random_order,
    create_random_person,
    create_random_product_attribute,
)
from shuup.utils.django_compat import force_text


class Mockers:
    """
    Namespace object for mocker methods.

    The docstrings for the callables are user-visible.
    """

    def mock_order(self, **kwargs):
        """Create a random order (randomly completed)."""
        shop = kwargs.pop("shop")

        try:
            return create_random_order(completion_probability=0.6, shop=shop)
        except Exception:
            pass

    def mock_order_6h(self, **kwargs):
        """Create a random order for past 6h (20% chance for completion)."""
        shop = kwargs.pop("shop")

        try:
            return create_random_order(completion_probability=0.2, shop=shop)
        except Exception:
            pass

    def mock_fully_paid_order(self, **kwargs):
        """Create a random order (complete and fully paid)."""
        shop = kwargs.pop("shop")

        try:
            return create_random_order(completion_probability=1, shop=shop, create_payment_for_order_total=True)
        except Exception:
            pass

    def mock_fully_paid_order_6h(self, **kwargs):
        """Create a random order for past 6h (complete and fully paid)."""
        shop = kwargs.pop("shop")
        order_date = now() - datetime.timedelta(minutes=random.uniform(0, 360))
        try:
            return create_random_order(
                completion_probability=1,
                shop=shop,
                create_payment_for_order_total=True,
                order_date=order_date,
            )
        except Exception:
            pass

    def mock_fully_paid_order_30d(self, **kwargs):
        """Create a random order for past 30 days (complete and fully paid)."""
        shop = kwargs.pop("shop")
        order_date = now() - datetime.timedelta(hours=random.uniform(0, 720))
        try:
            return create_random_order(
                completion_probability=1,
                shop=shop,
                create_payment_for_order_total=True,
                order_date=order_date,
            )
        except Exception:
            pass

    def mock_person(self, **kwargs):
        """Create a random person."""
        shop = kwargs.pop("shop")
        return create_random_person(shop=shop)

    def mock_company(self, **kwargs):
        """Create a random company."""
        shop = kwargs.pop("shop")
        return create_random_company(shop=shop)

    def mock_customer_group(self, **kwargs):
        """Create a random contact group."""
        return create_random_contact_group()

    def mock_product_attribute(self, **kwargs):
        """Create a random product attribute."""
        return create_random_product_attribute()


class MockerForm(forms.Form):
    type = forms.ChoiceField(widget=forms.RadioSelect())
    count = forms.IntegerField(min_value=1, max_value=100, initial=1)


class MockerView(FormView):
    form_class = MockerForm
    template_name = "shuup_testing/mocker.jinja"
    mockers = Mockers()

    def get_mockers(self):
        return [
            (
                name,
                force_text(getattr(self.mockers, name, None).__doc__ or name).strip(),
            )
            for name in dir(self.mockers)
            if name.startswith("mock_")
        ]

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.fields["type"].choices = self.get_mockers()
        return form

    def form_valid(self, form):
        data = form.cleaned_data
        mocker = getattr(self.mockers, data["type"], None)
        assert callable(mocker)
        for _n in range(data["count"]):
            try:
                value = mocker(shop=self.request.shop)
                if value:
                    messages.success(self.request, f"Created: {value}")
            except Exception as e:
                if settings.DEBUG:
                    raise
                messages.error(self.request, f"Error! {e}")
        return self.get(self.request)
