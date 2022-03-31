from djoser.conf import settings
from rest_framework import serializers


class TokenSerializer(serializers.ModelSerializer):
    token = serializers.CharField(source="key")

    class Meta:
        model = settings.TOKEN_MODEL
        fields = ("token",)
