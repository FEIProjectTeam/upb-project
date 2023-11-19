from django import forms

from users.models import Profile
from canteen.models import OrderMeal


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


class MealQuantityForm(forms.ModelForm):
    quantity = forms.IntegerField(
        min_value=1,
        label="Quantity",
        required=True,
        widget=forms.NumberInput(attrs={"value": "1", "required": "True"}),
    )

    class Meta:
        model = OrderMeal
        fields = ["quantity"]
