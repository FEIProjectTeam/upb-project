import json
import base64
import traceback

from cryptography.hazmat.primitives import serialization
from django.contrib import messages
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import api_view, parser_classes
from rest_framework import status
from django.shortcuts import render



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

def encrypt_page(request):
    return render(request, 'communication.html')

class ListMealsApi(APIView):
    
    def get(self, request):
        try:
            meals = get_all_meals()
            data = MealSerializer(meals, many=True).data
            json_data = json.dumps(data)  # Convert list of dicts to JSON string
            json_data_bytes = json_data.encode('utf-8')  # Convert string to bytes

            public_key_pem = request.user.profile.public_key
            public_key = pem_to_pub_key(public_key_pem.encode())

            cipheredData = encrypt_with_rsa_pub_key(public_key, json_data_bytes)

            encrypted_data = base64.b64encode(cipheredData).decode('utf-8')

            return JsonResponse({
                "status": "success",
                "encryptedData": encrypted_data
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            traceback.print_exc()  # This will print the stack trace to the console
            return JsonResponse({"status": "error", "message": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class DecryptPriKeyView(View):
    template_name = "canteen/decrypt_pri_key.html"

    def get(self, request, *args, **kwargs):
        
        return render(request, self.template_name)

    

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


def genRSAKeysView(request):
    return render(request, "canteen/gen_rsa_keys.html")



""" class EncryptView(TemplateView):
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

        return context """

class EncryptView(APIView):
    
    @parser_classes((JSONParser,))
    def post(self, request, *args, **kwargs):
        try:
            # Access the PEM from the POST data
            public_key_pem = request.data.get('publicKey')
            
            if public_key_pem:
                # Convert PEM to public key object
                public_key = pem_to_pub_key(public_key_pem.encode())



                # Here you would retrieve the data to be encrypted from your database
                # For this example, let's assume we are encrypting a simple message
                plaintext_data = "Data to encrypt"

                # Encrypt data using the RSA public key
                ciphertext = encrypt_with_rsa_pub_key(public_key, plaintext_data.encode())

                # Encode the ciphertext to base64 to send as JSON
                encrypted_data = base64.b64encode(ciphertext).decode('utf-8')
                
                return JsonResponse({
                    "status": "success",
                    "encryptedData": encrypted_data
                }, status=status.HTTP_200_OK)
            else:
                return JsonResponse({
                    "status": "error", 
                    "message": "No public key provided"
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            # Catch any other errors, such as issues with encryption
            return JsonResponse({
                "status": "error", 
                "message": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
