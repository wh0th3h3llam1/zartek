from rest_framework import status

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from app.models import Post
from app.serializers import PostSerializer

# Create your views here.

class PostViewSet(
	GenericViewSet,
	ListModelMixin,
	RetrieveModelMixin,
	UpdateModelMixin
):
	serializer_class = PostSerializer

	permission_classes = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,)

	def get_queryset(self):
		queryset = Post.objects.all().order_by('id')
		return queryset
	
	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['user'] = self.request.user
	
	@action(methods=['GET',], detail=True, permission_classes=(IsAuthenticated,))
	def liked(self, request, *args, **kwargs):
		
		post = self.get_object()
		users = post.liked_by.values_list('username', flat=True)
		return Response(
			data={
				"users": users
			}, status=status.HTTP_200_OK
		)
	
	@action(methods=['PATCH',], detail=True, permission_classes=(IsAuthenticated,))
	def like(self, request, *args, **kwargs):
		post = self.get_object()
		context = super().get_serializer_context()
		context['user'] = self.request.user
		serializer = self.serializer_class(
			instance=post,
			data=request.data,
			context=context
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(
			data={
				"message": "Data Updated"
			},
			status=status.HTTP_200_OK
		)

	@action(methods=['patch'], detail=True)
	def dislike(self, request, *args, **kwargs):
		post = self.get_object()
		context = super().get_serializer_context()
		context['user'] = self.request.user
		serializer = self.serializer_class(
			instance=post,
			data=request.data,
			context=context
		)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(
			data={
				"message": "Data Updated"
			},
			status=status.HTTP_200_OK
		)

class PostLikeView(APIView):
	pass