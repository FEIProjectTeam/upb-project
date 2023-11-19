import json
import base64
import traceback

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import parser_classes
from rest_framework import status
from django.shortcuts import render, redirect

from canteen.forms import (
    UploadPubKeyForm,
    MealQuantityForm,
    HiddenOrderIDForm,
)
from canteen.models import Meal
from canteen.serializers import MealSerializer
from canteen.services.encryption import (
    encrypt_with_rsa_pub_key,
    pem_to_pub_key,
)
from canteen.services.meals import (
    get_all_meals,
    get_meal_by_id,
)

from canteen.services.orders import (
    add_meal_to_order,
    get_unpaid_order_data_for_user,
    get_unpaid_order_by_id_and_user,
    pay_for_order,
    get_paid_order_data_for_user,
)


def encrypt_page(request):
    return render(request, "communication.html")


class ListMealsApi(APIView):
    def get(self, request):
        try:
            meals = get_all_meals()
            data = MealSerializer(meals, many=True).data
            json_data = json.dumps(data)  # Convert list of dicts to JSON string
            json_data_bytes = json_data.encode("utf-8")  # Convert string to bytes

            public_key_pem = request.user.profile.public_key
            public_key = pem_to_pub_key(public_key_pem.encode())

            cipheredData = encrypt_with_rsa_pub_key(public_key, json_data_bytes)

            encrypted_data = base64.b64encode(cipheredData).decode("utf-8")

            return JsonResponse(
                {"status": "success", "encryptedData": encrypted_data},
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            traceback.print_exc()  # This will print the stack trace to the console
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class DecryptPriKeyView(LoginRequiredMixin, TemplateView):
    template_name = "canteen/decrypt_pri_key.html"


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


class UploadPubKeyView(LoginRequiredMixin, View):
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


class GenRSAKeysView(LoginRequiredMixin, TemplateView):
    template_name = "canteen/gen_rsa_keys.html"


class EncryptView(APIView):
    @parser_classes((JSONParser,))
    def post(self, request, *args, **kwargs):
        try:
            # Access the PEM from the POST data
            public_key_pem = request.data.get("publicKey")

            if public_key_pem:
                # Convert PEM to public key object
                public_key = pem_to_pub_key(public_key_pem.encode())

                # Here you would retrieve the data to be encrypted from your database
                # For this example, let's assume we are encrypting a simple message
                plaintext_data = "Data to encrypt"

                # Encrypt data using the RSA public key
                ciphertext = encrypt_with_rsa_pub_key(
                    public_key, plaintext_data.encode()
                )

                # Encode the ciphertext to base64 to send as JSON
                encrypted_data = base64.b64encode(ciphertext).decode("utf-8")

                return JsonResponse(
                    {"status": "success", "encryptedData": encrypted_data},
                    status=status.HTTP_200_OK,
                )
            else:
                return JsonResponse(
                    {"status": "error", "message": "No public key provided"},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            # Catch any other errors, such as issues with encryption
            return JsonResponse(
                {"status": "error", "message": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MealsMenuView(LoginRequiredMixin, View):
    template_name = "canteen/meals_menu.html"

    def get(self, request):
        query = request.GET.get('q')  # Retrieve the search query
        if query:
            meals = Meal.objects.filter(name__icontains=query)  # Filter meals based on the query
        else:
            meals = get_all_meals()  # Get all meals if no query
        return render(request, self.template_name, {"mealsList": meals})


class MealDetail(LoginRequiredMixin, View):
    template_name = "canteen/meal_detail.html"

    def get(self, request, meal_id):
        form = MealQuantityForm()
        meal = get_meal_by_id(meal_id)
        if meal is None:
            return render(request, "canteen/404.html")
        return render(request, self.template_name, {"meal": meal, "form": form})

    def post(self, request, meal_id):
        form = MealQuantityForm(request.POST)
        meal = get_meal_by_id(meal_id)
        if meal is None:
            return render(request, "canteen/404.html")
        if form.is_valid():
            add_meal_to_order(request.user, meal, form.cleaned_data["quantity"])
            messages.success(request, "Meal was added to your order.")
        else:
            messages.error(request, "Meal failed to be added to your order.")
        return render(request, self.template_name, {"meal": meal, "form": form})


class OrdersListView(LoginRequiredMixin, View):
    template_name = "canteen/orders_list.html"

    def get(self, request):
        unpaid_order = get_unpaid_order_data_for_user(request.user)
        if unpaid_order:
            form = HiddenOrderIDForm()
            form.fields["id"].initial = unpaid_order["data"][0]["order_id"]
            unpaid_order["form"] = form
        paid_orders = get_paid_order_data_for_user(request.user)
        return render(
            request,
            self.template_name,
            {"unpaid_order": unpaid_order, "paid_orders": paid_orders},
        )

    def post(self, request):
        form = HiddenOrderIDForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data["id"]
            order = get_unpaid_order_by_id_and_user(order_id, request.user)
            if order is None:
                messages.error(request, "Failed to pay for order.")
            else:
                pay_for_order(order)
                messages.success(request, "Order was paid.")
        return redirect(reverse("orders-list"))


class OrderDeleteView(LoginRequiredMixin, View):
    def post(self, request):
        form = HiddenOrderIDForm(request.POST)
        if form.is_valid():
            order_id = form.cleaned_data["id"]
            order = get_unpaid_order_by_id_and_user(order_id, request.user)
            if order is None:
                messages.error(request, "Failed to delete order.")
            else:
                order.delete()
                messages.warning(request, "Order was deleted.")
        return redirect(reverse("orders-list"))
