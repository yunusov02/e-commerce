from .cart import Cart
from django.http.request import HttpRequest


def cart(request: HttpRequest):

    return {"cart": Cart(request)}