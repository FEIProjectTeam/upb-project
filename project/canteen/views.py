import json

from cryptography.hazmat.primitives import serialization
from django.contrib import messages
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

from canteen.forms import UploadPubKeyForm
from canteen.models import Meal
from canteen.serializers import MealSerializer
from canteen.services.encryption import (
    symmetric_encrypt,
    generate_rsa_keys,
    encrypt_with_rsa_pub_key,
    decrypt_with_rsa_prv_key,
    symmetric_decrypt,
    get_hmac,
    pem_to_pub_key,
)
from canteen.services.meals import get_all_meals


class ListMealsApi(APIView):
    def get(self, request):
        data = MealSerializer(get_all_meals(), many=True).data
        return Response(data, HTTP_200_OK)


class GenerateDummyDatabaseApi(APIView):
    def get(self, request):
        try:
            Meal.objects.create(name="Soup", price=0.8)
            Meal.objects.create(name="Chicken with rice", price=3.6)
            Meal.objects.create(name="Pizza", price=5.5)
        except:
            pass
        finally:
            return Response(status=HTTP_200_OK)


class UploadPubKeyView(View):
    template_name = "canteen/upload_pub_key.html"

    def get(self, request, *args, **kwargs):
        form = UploadPubKeyForm(instance=request.user.profile)
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = UploadPubKeyForm(request.POST, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, f"Public key was successfully updated.")
        else:
            messages.error(request, f"Public key could not be updated.")
        return render(request, self.template_name, {"form": form})


class GenRSAKeysView(View):
    template_name = "canteen/gen_rsa_keys.html"


class EncryptView(TemplateView):
    template_name = "encryption.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Client first generates rsa keys and sends pem to server
        client_private_key, client_public_key, client_pem = generate_rsa_keys()
        context["pub_key"] = client_public_key
        context["pem_key"] = client_pem
        context["prv_key"] = client_private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ).decode("utf-8")
        # Server retrieves public key from client's pem
        public_key = pem_to_pub_key(client_pem)

        orig_data = MealSerializer(get_all_meals(), many=True).data
        orig_data = json.dumps(orig_data)
        context["orig_data"] = orig_data
        password = "password"

        symmetric_key, salt, iv, encrypted_data = symmetric_encrypt(orig_data, password)
        context["encrypted_data"] = encrypted_data.hex()

        orig_hmac = get_hmac(symmetric_key, encrypted_data)

        encrypted_symmetric_key = encrypt_with_rsa_pub_key(public_key, symmetric_key)
        context["encrypted_symmetric_key"] = encrypted_symmetric_key.hex()

        encryption_message = json.dumps(
            {
                "iv": iv.hex(),
                "hmac": orig_hmac.hex(),
                "symmetric_key": encrypted_symmetric_key.hex(),
                "cyphertext": encrypted_data.hex(),
            }
        )

        # Here is encryption message sent to the recipient

        received_message = json.loads(encryption_message)

        rcv_iv = bytes.fromhex(received_message["iv"])
        rcv_hmac = bytes.fromhex(received_message["hmac"])
        rcv_symmetric_key = bytes.fromhex(received_message["symmetric_key"])
        rcv_cyphertext = bytes.fromhex(received_message["cyphertext"])

        decrypted_symmetric_key = decrypt_with_rsa_prv_key(
            client_private_key, rcv_symmetric_key
        )

        if rcv_hmac == get_hmac(decrypted_symmetric_key, rcv_cyphertext):
            context[
                "hmac_result"
            ] = "Data is authentic and intact, proceed with decryption."
        else:
            context[
                "hmac_result"
            ] = "Data integrity check failed, consider the data compromised."

        decrypted_data = symmetric_decrypt(
            decrypted_symmetric_key, rcv_iv, rcv_cyphertext
        )
        context["decrypted_data"] = decrypted_data.decode("utf-8")

        return context
