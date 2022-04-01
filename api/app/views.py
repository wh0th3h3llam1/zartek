from django.db.models import Sum, Q

from rest_framework import status

from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.mixins import RetrieveModelMixin, UpdateModelMixin, ListModelMixin
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from app.models import Post
from app.serializers import PostSerializer

# Create your views here.

class PostViewSet(
	ListModelMixin,
	RetrieveModelMixin,
	UpdateModelMixin,
	GenericViewSet
):
	"""
	A Viewset which provides list, retrieve & update methods for Post
	"""
	serializer_class = PostSerializer

	permission_classes = (IsAuthenticated,)
	authentication_classes = (TokenAuthentication,)

	def get_queryset(self):
		queryset = Post.objects.prefetch_related('tags').all()
		return queryset
	
	def get_serializer_context(self):
		context = super().get_serializer_context()
		context['user'] = self.request.user
		return context
	
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
		serializer.save()

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

	@action(methods=['patch'], detail=True, permission_classes=(IsAuthenticated,))
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

class PostLikeView(APIView):
	pass
	
	# similar_posts = Post.published.exclude(pk=post.pk).filter(
	# 	tags__post=post
	# ).annotate(
	# 	same_tags=Count('tags')
	# ).order_by('-same_tags','-publish')[:4]
	# -----------------------

	#     # List of similar posts
    # post_tags_ids = post.tags.values_list('id', flat=True)
    # similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    # similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:6]

    # return render(request, 'post_detail.html',{'post':post,'comments': comments,'comment_form':comment_form,'similar_posts':similar_posts})