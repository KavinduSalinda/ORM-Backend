from django.urls import path
from .views import UsersView, UserView, RegisterView, ProfileView, count_users

urlpatterns = [
    path('', UsersView.as_view(), name='users'),
    path('<int:id>/', UserView.as_view(), name='users'),
    path('exclude/', UsersView.as_view(), name='users'),
    path('create/', RegisterView.as_view(), name='users'),
    path('bulk_create/', RegisterView.as_view(), name='users'),
    path('update_or_create/', ProfileView.as_view(), name='users'),
    path('count/', count_users, name='users'),
]