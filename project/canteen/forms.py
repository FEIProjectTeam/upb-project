from django import forms

from users.models import Profile
from canteen.models import Order


class UploadPubKeyForm(forms.ModelForm):
    public_key = forms.CharField(
        label="Public key",
        required=True,
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
            }
        ),
    )

    class Meta:
        model = Profile
        fields = ["public_key"]


class OrderForm(forms.ModelForm):
    quantity = forms.DecimalField(
        label="quantity",
        required=True
    )

    class Meta:
        model = Order
        fields = ["quantity"]
