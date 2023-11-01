import json

from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView

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


class EncryptView(TemplateView):
    template_name = "encryption.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Client first generates rsa keys and sends pem to server
        client_private_key, client_public_key, client_pem = generate_rsa_keys()

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
