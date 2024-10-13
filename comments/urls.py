from django.urls import path
from .views import CommentView

urlpatterns = [
    path("select_related/", CommentView.as_view(), name="comments"),
    path("<int:id>/delete/", CommentView.as_view(), name="comments"),
]
