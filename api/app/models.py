from django.contrib.auth.models import User
from django.db import models

from core.models import BaseModel
from lib.constants import FieldConstants
from lib.utils import get_image_path

# Create your models here.


class Post(BaseModel):
	title = models.CharField(max_length=FieldConstants.MAX_LENGTH)
	description = models.TextField()
	likes = models.PositiveIntegerField(default=0, blank=True)
	dislikes = models.PositiveIntegerField(default=0, blank=True)
	liked_by = models.ManyToManyField(
		to=User,
		related_name='liked_posts',
		blank=True,
		null=True
	)
	disliked_by = models.ManyToManyField(
		to=User,
		related_name='disliked_posts',
		blank=True,
		null=True
	)

	def __str__(self) -> str:
		return self.title
	
	def no_of_likes(self):
		return self.likes
	
	def no_of_dislikes(self):
		return self.dislikes
	

class Image(BaseModel):
	name = models.CharField(verbose_name="Image Name", max_length=FieldConstants.MAX_LENGTH)
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
	image = models.ImageField(upload_to=get_image_path)
	description = models.TextField(verbose_name="Description", blank=True, null=True)

	def __str__(self) -> str:
		return f"{self.name} - {self.post.title}"


class Tag(BaseModel):
	name = models.CharField(max_length=FieldConstants.MAX_LENGTH)
	weight = models.PositiveSmallIntegerField()
	post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='tags')