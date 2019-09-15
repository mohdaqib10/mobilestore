from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from .models import User, UserMobile, UserToken


class UserTokenSerializer(ModelSerializer):
    class Meta:
        model = UserToken
        fields = '__all__'


class UserBasicSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email')  # or '__all__'


class UserSerializer(ModelSerializer):
    primary_mobile = serializers.SerializerMethodField()
    mobiles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'primary_mobile', 'mobiles')

    def get_primary_mobile(self, instance):
        return UserMobileSerializer(instance.primary_mobile).data

    def get_mobiles(self, instance):
        return UserMobileSerializer(instance.all_mobiles, many=True).data


class UserMobileSerializer(ModelSerializer):
    class Meta:
        model = UserMobile
        fields = ('id', 'user', 'mobile', 'is_spam', 'is_primary', 'count')
