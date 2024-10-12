from django.urls import path
from .views import (
    PostView,
    PostAggregateView,
    get_first_post,
    get_last_post,
    get_reverse_list,
    get_order_by_field,
    get_specific_fields_of_posts,
)

urlpatterns = [
    path("get_or_create/", PostView.as_view(), name="posts"),
    path("aggregate/", PostAggregateView.as_view(), name="posts"),
    path("first/", get_first_post, name="posts"),
    path("last/", get_last_post, name="posts"),
    path("reverse/", get_reverse_list, name="posts"),
    path("order_by/", get_order_by_field, name="posts"),
    path("values/", get_specific_fields_of_posts, name="posts"),
]
