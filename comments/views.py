from django.http import JsonResponse
from django.views import View
from .models import Comment

# Create your views here.
class CommentView(View):
    def get(self, request):
        post_id = request.GET.get("post_id")
        if post_id is None:
            return JsonResponse({"error": "post_id is required"}, status=400)
        
        comments = Comment.objects.select_related("user", "post").all()
        return JsonResponse({"comments": list(comments.values())})
    
    def delete(self, request, id):
        try:
            comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            return JsonResponse({"error": "Comment not found"}, status=404)
        comment.delete()
        return JsonResponse({"message": "Comment deleted!"})