from rest_framework import serializers

from app.models import Post, Image, Tag

from lib.constants import FieldConstants

class ImageSerializer(serializers.Serializer):
	name = serializers.CharField()
	image = serializers.ImageField()
	description = serializers.CharField(required=False)
	
	class Meta:
		verbose_name = 'Image'
		verbose_name_plural = 'Images'
		model = Image


	def create(self, validated_data):

		return super().create(validated_data)


class PostSerializer(serializers.Serializer):

	title = serializers.CharField(required=False)
	description = serializers.CharField(required=False)
	no_of_likes = serializers.IntegerField(source='likes', read_only=True)
	no_of_dislikes = serializers.IntegerField(source='dislikes', read_only=True)
	likes = serializers.IntegerField(write_only=True, required=False)
	dislikes = serializers.IntegerField(write_only=True, required=False)
	images = serializers.SerializerMethodField()
	user_choice = serializers.SerializerMethodField()
	post_created = serializers.DateTimeField(
		source='created', format=FieldConstants.DATE_TIME_FORMAT, read_only=True)
	post_images = serializers.ListField(write_only=True, required=False)
	post_tags = serializers.CharField(write_only=True, required=False)


	def get_images(self, instance: Post):
		images = ImageSerializer(instance.images.all(), many=True)
		return images.data
	
	def get_user_choice(self, instance: Post) -> str:
		user = self.context.get('user')
		choice = 'None'
		if user in instance.liked_by.all():
			choice = 'Liked'
		elif user in instance.disliked_by.all():
			choice = 'Disliked'
		return choice


	def validate_likes(self, likes):
		if not self.instance:
			return 0
		user = self.context.get('user')
		if user in self.instance.liked_by.all():
			raise serializers.ValidationError("You cannot like a post more than once")
		return likes
	
	def validate_dislikes(self, dislikes):
		if not self.instance:
			return 0
		user = self.context.get('user')
		if user in self.instance.disliked_by.all():
			raise serializers.ValidationError("You cannot dislike a post more than once")
		return dislikes

	def validate(self, attrs: dict):
		instance = self.instance
		if not instance:
			return super().validate(attrs)
		
		liked = attrs.get('likes', None)
		disliked = attrs.get('dislikes', None)

		if liked and disliked:
			raise serializers.ValidationError({
				"You cannot like and dislike post at the same time"
			})
		return attrs


	class Meta:
		verbose_name = 'Post'
		verbose_name_plural = 'Posts'
		model = Post


	def create(self, validated_data):
		post_images = validated_data.pop('post_images', None)
		post_tags = validated_data.pop('post_tags', None)

		instance = Post.objects.create(**validated_data)

		if post_images:
			images = [
				Image(
					name=image.name,
					image=image,
					post=instance
				)
				for image in post_images
			]

			Image.objects.bulk_create(images)
		
		if post_tags:
			tags = post_tags.split(",")
			for tag in tags:
				name, weight = tag.split(":")
				Tag.objects.create(
					name=name,
					weight=weight,
					post=instance
				)

		
		return instance
	
	def update(self, instance: Post, validated_data):
		user = self.context.get('user')
		liked = validated_data.get("likes", None)
		disliked = validated_data.get("dislikes", None)

		if liked:
			instance.likes += 1
			instance.dislikes = instance.dislikes - 1 if instance.dislikes > 1 else 0

		if disliked:
			instance.dislikes += 1
			instance.likes = instance.likes - 1 if instance.likes > 1 else 0
		
		instance.save()

		if liked:
			instance.liked_by.add(user)
			instance.disliked_by.remove(user)
		if disliked:
			instance.disliked_by.add(user)
			instance.liked_by.remove(user)
		
		return instance
