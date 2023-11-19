import json
import base64
import traceback
import io

from reportlab.platypus.tables import Table, TableStyle
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views import View
from django.views.generic import TemplateView
from rest_framework.response import Response
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from django.http import JsonResponse, FileResponse
from rest_framework.parsers import JSONParser
from rest_framework.decorators import parser_classes
from rest_framework import status
from django.shortcuts import render, redirect
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import letter

from canteen.forms import (
    UploadPubKeyForm,
    MealQuantityForm,
    ReviewForm,
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
    get_paid_order_by_id_and_user,
    pay_for_order,
    get_paid_order_data_for_user,
)

from canteen.models import Review
from canteen.services.reviews import submit_review, get_review_for_user_and_meal


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
        query = request.GET.get("q")
        if query:
            meals = Meal.objects.filter(name__icontains=query)
        else:
            meals = get_all_meals()
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


class LeaveReviewView(LoginRequiredMixin, View):
    template_name = "canteen/leave_review.html"

    def get(self, request, meal_id):
        meal = get_meal_by_id(meal_id)
        if meal is None:
            return render(request, "canteen/404.html")
        review = get_review_for_user_and_meal(request.user, meal)
        if review is None:
            form = ReviewForm()
        else:
            form = ReviewForm(instance=review)
        context = {"meal": meal, "form": form}
        return render(request, self.template_name, context)

    def post(self, request, meal_id):
        meal = get_meal_by_id(meal_id)
        form = ReviewForm(request.POST)

        if form.is_valid():
            stars = form.cleaned_data["stars"]
            comment = form.cleaned_data["comment"]

            submit_review(request.user, meal, stars, comment)
            return redirect("menu")

        context = {"meal": meal, "form": form}
        return render(request, self.template_name, context)


class ReviewListView(LoginRequiredMixin, View):
    template_name = "canteen/review_list.html"

    def get(self, request, meal_id):
        meal = get_meal_by_id(meal_id)
        reviews = Review.objects.filter(meal=meal)
        context = {"meal": meal, "reviews": reviews}
        return render(request, self.template_name, context)


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


class InvoiceView(LoginRequiredMixin, View):
    def get(self, request, item):
        order = get_paid_order_by_id_and_user(item, request.user)
        if order is None:
            messages.error(request, "Failed to create invoice for order.")
            return redirect(reverse("orders-list"))

        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=letter)
        textob = c.beginText()
        textob.setTextOrigin(inch, inch)
        textob.setFont("Helvetica", 14)

        meals = order.ordermeal_set.all()
        meal_data = [["Canteen"], ["Your order:"], ["Item", "Quantity", "Price"]]

        total_price = 0
        total_quantity = 0
        for order_meal in meals:
            name = order_meal.meal.name
            quantity = order_meal.quantity
            price = (
                order_meal.meal.price * quantity
            )  # Calculate total price for the quantity
            formatted_price = "{:.2f} €".format(price)
            data = [name, quantity, formatted_price]
            total_price += price
            total_quantity += quantity
            meal_data.append(data)

        formatted_total_price = "{:.2f} €".format(total_price)
        meal_data.append(["Total", total_quantity, formatted_total_price])
        data = meal_data
        table_width = letter[0] - 2 * inch
        table_height = letter[1] - 2 * inch
        top_margin = inch

        t = Table(
            data, colWidths=[table_width * 0.7, table_width * 0.1, table_width * 0.2]
        )

        x_position = inch
        y_position = letter[1] - 2 * inch - top_margin

        style = TableStyle(
            [
                ("SPAN", (0, 0), (-1, 0)),
                ("SPAN", (0, 1), (-1, 1)),
                ("ALIGN", (0, 0), (0, 0), "CENTER"),
                ("ALIGN", (1, 0), (1, -1), "CENTER"),
                ("ALIGN", (-1, 0), (-1, -1), "RIGHT"),
                ("LINEBELOW", (0, 0), (-1, 0), 1, (0, 0, 0)),
                ("LINEBELOW", (0, 1), (-1, 1), 1, (0, 0, 0)),
                ("LINEBELOW", (0, 2), (-1, 2), 1, (0, 0, 0)),
                ("LINEABOVE", (0, -1), (-1, -1), 1, (0, 0, 0)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("FONT", (0, -1), (-1, -1), "Helvetica-Bold"),
            ]
        )

        t.setStyle(style)

        t.wrapOn(c, table_width, table_height)
        t.drawOn(c, x_position, y_position)

        c.showPage()
        c.save()
        buf.seek(0)

        return FileResponse(buf, as_attachment=True, filename="faktura.pdf")
