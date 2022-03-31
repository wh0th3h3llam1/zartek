from django.urls import include, path

from rest_framework.routers import DefaultRouter

from app.views import PostViewSet

router = DefaultRouter()


router.register(prefix="posts", viewset=PostViewSet, basename="posts")


urlpatterns = [
	path('', include(router.urls)),
]
