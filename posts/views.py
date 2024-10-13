from django.http import JsonResponse
from django.views import View
from .models import Post
from django.db.models import Sum, Avg, Count
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

# 18
def get_flat_list_of_posts(request):
    field = request.GET.get("fields")
    if not field:
        return JsonResponse({"error": "Please provide fields to retrieve"}, status=400)
    
    values= field.split(',')
    flat = request.GET.get("flat")

    if flat is None or len(values) > 1:
        flat = False

    posts = Post.objects.all().values_list(*values, flat=flat)

    if not posts:
        return JsonResponse({"error": "No posts found"}, status=404)
    data = [post for post in posts]
    return JsonResponse({"posts": data}, status=200)

def check_post_title_exists(request):
    title = request.GET.get("title")
    if not title:
        return JsonResponse({"error": "Please provide a title to check"}, status=400)
    
    post = Post.objects.filter(title=title).exists()

    return JsonResponse({"exists": post}, status=200)


def get_annotate_comments_count(request):
    # Annotate each post with the count of its comments
    posts = Post.objects.annotate(comments_count=Count('comment')).values('id', 'title', 'comments_count')

    if not posts:
        return JsonResponse({"error": "No posts found"}, status=404)
    
    data = [post for post in posts]
    return JsonResponse({"posts": data}, status=200)



def get_distinct_authors(request):
    # Get the field parameter from the query string
    field = request.GET.get('field')

    if not field:
        return JsonResponse({"error": "Field parameter is required"}, status=400)

    # Ensure the field is 'author' since there's no Author model
    if field != 'author':
        return JsonResponse({"error": f"Invalid field: {field}. Only 'author' is allowed."}, status=400)

    # Get distinct authors based on the 'author' field
    try:
        authors = Post.objects.values(field).distinct()
    except FieldError:
        return JsonResponse({"error": "Error retrieving distinct authors"}, status=400)

    return JsonResponse(list(authors), safe=False)


def update_user_profile(request):
    # Get the user ID from the query string
    user_id = request.GET.get('user_id')

    if not user_id:
        return JsonResponse({"error": "User ID is required"}, status=400)

    # Get the user object based on the user ID
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)

    # Update the user's profile information
    user.profile.bio = request.GET.get('bio', user.profile.bio)
    user.profile.location = request.GET.get('location', user.profile.location)
    user.profile.save()

    return JsonResponse({"message": "User profile updated successfully"}, status=200)