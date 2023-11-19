from django import forms

from users.models import Profile
from canteen.models import OrderMeal, Order, Review


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
        widget=forms.NumberInput(attrs={"value": "1"}),
    )

    class Meta:
        model = OrderMeal
        fields = ["quantity"]


class ReviewForm(forms.ModelForm):
    stars = forms.IntegerField(
        label="Stars (between 0 and 5)",
        min_value=0,
        max_value=5,
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )
    comment = forms.CharField(
        label="Comment",
        widget=forms.Textarea(attrs={"class": "form-control"}),
        required=False,
    )

    class Meta:
        model = Review
        fields = ["stars", "comment"]


class HiddenOrderIDForm(forms.ModelForm):
    id = forms.IntegerField(
        min_value=1,
        required=True,
        widget=forms.HiddenInput(),
    )

    class Meta:
        model = Order
        fields = ["id"]
