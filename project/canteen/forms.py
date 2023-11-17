from django import forms

from users.models import Profile


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

class MakeOrder(forms.ModelForm):
    pass
