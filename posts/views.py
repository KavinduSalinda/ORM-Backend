from django.http import JsonResponse
from django.views import View
from .models import Post
from django.db.models import Sum, Avg
from django.core.exceptions import FieldError
import json


@staticmethod
def convert_to_Data(post):
    data = {
        "title": post.title,
        "author": post.author.username,
    }
    return data


# Create your views here.
class PostView(View):
    def get(self, request):
        title = request.GET.get("title")
        author_id = request.GET.get("author_id")

        if not title and not author_id:
            return JsonResponse({"error": "Missing title and author_id"}, status=400)

        post, created = Post.objects.get_or_create(title=title, author_id=author_id)
        if created:
            return JsonResponse(
                {"message": "Post created", "post": convert_to_Data(post)}, status=201
            )

        return JsonResponse(
            {"message": "Post retrieved", "post": convert_to_Data(post)}, status=200
        )


class PostAggregateView(View):
    def get(self, request):
        field = request.GET.get("field")

        if not field:
            return JsonResponse({"error": "Field parameter is required"}, status=400)

        try:
            result = Post.objects.aggregate(Sum(field))
        except FieldError:
            return JsonResponse({"error": "Invalid field"}, status=400)

        return JsonResponse({"result": json.dumps(result)}, status=200)


def get_first_post(request):
    try:
        post = Post.objects.first()
    except Post.DoesNotExist:
        return JsonResponse({"error": "No posts found"}, status=404)
    return JsonResponse(
        {"message": "Post retrieved", "post": convert_to_Data(post)}, status=200
    )


def get_last_post(request):
    post = Post.objects.last()
    if not post:
        return JsonResponse({"error": "No posts found"}, status=404)
    return JsonResponse({"post": convert_to_Data(post)}, status=200)


def get_reverse_list(request):
    posts = Post.objects.reverse()

    if not posts:
        return JsonResponse({"error": "No posts found"}, status=404)
    return JsonResponse(
        {"posts": [convert_to_Data(post) for post in posts]}, status=200
    )


def get_order_by_field(request):
    field = request.GET.get("field")
    # todo check simple case
    posts = Post.objects.order_by(field) 

    if not posts:
        return JsonResponse({"error": "No posts found"}, status=404)

    return JsonResponse(
        {"posts": [convert_to_Data(post) for post in posts]}, status=200
    )


def get_specific_fields_of_posts(request):
    field = request.GET.get("fields")
    if not field:
        return JsonResponse({"error": "Please provide fields to retrieve"}, status=400)
    
    values= field.split(',')
    posts = Post.objects.all().values(*values)

    if not posts:
        return JsonResponse({"error": "No posts found"}, status=404)
    
    data = [post for post in posts]
    return JsonResponse({"posts": data }, status=200)
