from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'Type',  'balance', )

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'Type', )


# class AuthorSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Author
#         fields = ('id', 'name', 'instituition', 'domain', 'citation_num', 'article_num', 'h_index', 'g_index', 'avator')

class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ('Type','name','files','uid')

class UserAvatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('avator',)

class AuthorAvatorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Avator
        fields = ('uid','avator')

# class AuctionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Auction
#         fields = ('id', 'title', 'started_time', 'price', 'period')


        