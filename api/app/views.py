from django.contrib.auth.models import User
from django.db.models import Sum, Q

from rest_framework import mixins, status

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from app.models import Post
from app.permissions import UserPermissions
from app.serializers import PostSerializer

# Create your views here.

class PostViewSet(
	mixins.ListModelMixin,
	mixins.RetrieveModelMixin,
	mixins.UpdateModelMixin,
	mixins.CreateModelMixin,
	GenericViewSet
):
	"""
	A Viewset which provides list, retrieve & update methods for Post
	"""
	serializer_class = PostSerializer

	permission_classes = (UserPermissions,)
	authentication_classes = (TokenAuthentication,)

	def get_queryset(self):
		queryset = Post.objects.prefetch_related('tags').all()
		return queryset
	
	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['user'] = self.request.user
		return context
	
	def create(self, request, *args, **kwargs):
		
		serializer = self.serializer_class(data=request.data)
		serializer.is_valid(raise_exception=True)
		serializer.save()
		return Response(
			data={
				"message": "Created Successfully"	
			}, status=status.HTTP_201_CREATED
		)

	
	@action(methods=['GET',], detail=True, permission_classes=(IsAuthenticated,))
	def liked(self, request, *args, **kwargs):
		"""
		Returns the list of users that liked a particular post
		"""
		
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
		user = self.request.user
		context['user'] = user
		serializer = self.serializer_class(
			instance=post,
			data=request.data,
			context=context
		)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer=serializer)

		post_tags = post.tags.values_list('name', flat=True)
		
		similar_posts = self.get_queryset().annotate(
							post_weight=Sum('tags__weight')
						).filter(
							Q(
								tags__name__in=post_tags
							) | Q(
								tags__name__icontains=post_tags
							)
						).exclude(id=post.id).order_by('-post_weight')
		similar_serializer = self.serializer_class(similar_posts, many=True)
		return Response(
			data={
				"similar_posts": similar_serializer.data
			},
			status=status.HTTP_200_OK
		)

	@action(methods=['PATCH'], detail=True, permission_classes=(IsAuthenticated,))
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
		
		post_tags = post.tags.values_list('name', flat=True)
		
		similar_posts = self.get_queryset().annotate(
							post_weight=Sum('tags__weight')
						).exclude(
							id=post.id
						).exclude(
							Q(
								tags__name__in=post_tags
							) | Q(
								tags__name__icontains=post_tags
							)
						).order_by('-post_weight')
		
		similar_serializer = self.serializer_class(similar_posts, many=True)
		return Response(
			data={
				"similar_posts": similar_serializer.data
			},
			status=status.HTTP_200_OK
		)
