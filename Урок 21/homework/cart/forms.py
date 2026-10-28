from django import forms

QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 11)]


class CartAddBookForm(forms.Form):
    """Додати в кошик."""

    quantity = forms.TypedChoiceField(
        choices=QUANTITY_CHOICES, coerce=int, label="Кількість"
    )
    override = forms.BooleanField(
        required=False, initial=False, widget=forms.HiddenInput
    )
