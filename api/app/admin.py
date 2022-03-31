from django.contrib import admin

from app.models import Post, Image, Tag
# Register your models here.


class TagInLine(admin.TabularInline):
	model = Tag

class ImageInLine(admin.TabularInline):
	model = Image

class PostAdmin(admin.ModelAdmin):
	list_display = ("title", "description", "no_of_likes", "no_of_dislikes")
	inlines = (ImageInLine, TagInLine)
	readonly_fields = ("likes", "dislikes")

admin.site.register(Post, PostAdmin)
admin.site.register(Image)
admin.site.register(Tag)