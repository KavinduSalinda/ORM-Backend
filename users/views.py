from django.contrib.auth.models import User
from users.models import Profile
from django.http import JsonResponse, HttpResponse
from django.views import View
import json

class RegisterView(View):
    def post(self, request):
        data = json.loads(request.body)

        # Check if data is a list for bulk creation (6)
        if isinstance(data, list):
            users_to_create = []
            errors = []

            for user_data in data:
                username = user_data.get("username")
                email = user_data.get("email")
                first_name = user_data.get("first_name")
                last_name = user_data.get("last_name")

                if not username or not email:
                    errors.append({"error": "Please provide a username and email", "data": user_data})
                    continue  # Skip this user data

                try:
                    user = User(
                        username=username,
                        email=email,
                        first_name=first_name,
                        last_name=last_name,
                    )
                    users_to_create.append(user)
                except Exception as e:
                    errors.append({"error": str(e), "data": user_data})

            # Perform bulk creation
            if users_to_create:
                User.objects.bulk_create(users_to_create)

            # Return errors if any
            if errors:
                return JsonResponse({"errors": errors}, status=400)
            
            return JsonResponse({"message": "Users created successfully"}, status=201)

        # Handle single user creation (5)
        username = data.get("username")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if not username or not email:
            return JsonResponse({"error": "Please provide a username and email"}, status=400)
        try:
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
            )
            return JsonResponse(
                {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class ProfileView(View):
    def post(self, request):
        data = json.loads(request.body)
        user_id = data.get("user_id")
        bio = data.get("bio")
        profile_picture = data.get("profile_picture")
        birth_date = data.get("birth_date")

        if not user_id:
            return JsonResponse({"error": "Please provide a user_id"}, status=400)

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)

        try:
            profile, created = Profile.objects.update_or_create(
                user=user,
                defaults={
                    "bio": bio,
                    "profile_picture": profile_picture,
                    "birth_date": birth_date,
                },
            )
            return JsonResponse(
                {
                    "id": profile.id,
                    "user_id": profile.user.id,
                    "bio": profile.bio,
                    "profile_picture": profile.profile_picture,
                    "birth_date": profile.birth_date,
                },
                status=201,
            )
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)


class UsersView(View):
    def get(self, request):
        email = request.GET.get("email")
        username = request.GET.get("username")

        # If an email is provided, return the user with that email (2)
        if email:
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return JsonResponse({"error": "User not found"}, status=404)
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            }
            return JsonResponse({"user": user_data}, status=200)

        # If a username is provided, return all users except the one with that username (3)
        if username:
            try:
                users = User.objects.exclude(username=username).values(
                    "id", "username", "email", "first_name", "last_name"
                )
            except User.DoesNotExist:
                return JsonResponse({"error": "Users not found"}, status=404)
            users_list = list(users)
            return JsonResponse({"users": users_list}, status=200)

        # If no email is provided, return all users in the database (1)
        users = User.objects.all().values(
            "id", "username", "email", "first_name", "last_name"
        )
        users_list = list(users)
        return JsonResponse({"users": users_list}, status=200)
    
    def put(self, request, id):
        data = json.loads(request.body)
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        
        user.username = data.get("username", user.username)
        user.email = data.get("email", user.email)
        user.first_name = data.get("first_name", user.first_name)
        user.last_name = data.get("last_name", user.last_name)
        user.save()

        return JsonResponse(
            {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
            },
            status=200,
        )


class UserView(View):
    def get(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return JsonResponse({"error": "User not found"}, status=404)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return JsonResponse({"user": user_data}, status=200)

# Count the number of users in the database (9)
def count_users(request):
    users_count = User.objects.count()
    return JsonResponse({"users_count": users_count}, status=200)

def get_users_by_database(request, db_alias):
    try:
        # Retrieve all users from the specified database connection
        users = User.objects.using(db_alias).all()
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
    
    users_data = list(users.values('id', 'username', 'email'))
    return JsonResponse(users_data, safe=False)