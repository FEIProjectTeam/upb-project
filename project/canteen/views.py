import json

from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from canteen.serializers import MealSerializer
from canteen.services.encryption import (symmetric_encrypt, generate_rsa_keys, encrypt_with_rsa_pub_key,
                                         decrypt_with_rsa_prv_key, symmetric_decrypt, get_hmac)
from canteen.services.meals import get_all_meals


class ListMealsApi(APIView):
    def get(self, request):
        data = MealSerializer(get_all_meals(), many=True).data
        return Response(data, HTTP_200_OK)


class EncryptView(TemplateView):
    template_name = "encryption.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        orig_data = MealSerializer(get_all_meals(), many=True).data
        orig_data = json.dumps(orig_data)
        context["orig_data"] = orig_data
        password = 'password'

        symmetric_key, salt, iv, encrypted_data = symmetric_encrypt(orig_data, password)
        context["encrypted_data"] = encrypted_data.hex()

        orig_hmac = get_hmac(symmetric_key, encrypted_data)

        private_key, public_key, pem = generate_rsa_keys()

        encrypted_symmetric_key = encrypt_with_rsa_pub_key(public_key, symmetric_key)
        context["encrypted_symmetric_key"] = encrypted_symmetric_key.hex()

        decrypted_symmetric_key = decrypt_with_rsa_prv_key(private_key, encrypted_symmetric_key)

        if orig_hmac == get_hmac(decrypted_symmetric_key, encrypted_data):
            context["hmac_result"] = "Data is authentic and intact, proceed with decryption."
        else:
            context["hmac_result"] = "Data integrity check failed, consider the data compromised."

        decrypted_data = symmetric_decrypt(decrypted_symmetric_key, iv, encrypted_data)
        context["decrypted_data"] = decrypted_data.decode('utf-8')

        return context
