from django.contrib.auth import login, authenticate
from django.contrib.auth.password_validation import validate_password
from django.http import HttpResponse
from requests import post, Response
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from Project1.settings import host_url
from rest_framework_simplejwt.models import TokenUser
from rest_framework.authtoken.models import Token
from rest_framework import status
from rest_framework.response import Response

from Site_User.custom_validators import customValidator, validate_phone_number
from Site_User.models import User



class RegisterSerializer(serializers.ModelSerializer):
    # email = serializers.EmailField(
    #         required=True,
    #         validators=[UniqueValidator(queryset=User.objects.all())]
    #         )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)
    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        if User.objects.filter(username=attrs["username"]).first():
            raise serializers.ValidationError({"username": "an account with this username already exists."})
        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            # email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )
        # if not Token.objects.filter(user=user).first():
        #     Token.objects.create(user=user)
        user.set_password(validated_data['password'])
        user.save()

        return user

class CreateTokenSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)

    def create(self, validated_data):
        username = validated_data['username']
        user = User.objects.get_or_create(username=username)[0]
        if token := Token.objects.filter(user=user).first():
            token.delete()
        token = Token.objects.create(user=user)
        return token

    def remove(self, validated_data):
        username = validated_data['username']
        user = User.objects.filter(username=username).first()
        if token := Token.objects.filter(user=user).first():
            token.delete()
        return token

# class CreateTokenAdminSerializer(serializers.Serializer):
#     username = serializers.CharField(required=True)
#     password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
#     def create(self, validated_data):
#         username = validated_data['username']
#         password = validated_data['password']
#         user = User.objects.filter(username=username,admin_password=password).first()
#         if not user:
#             raise serializers.ValidationError({"username": "Invalid username or password."})
#         if not user.is_staff:
#             raise serializers.ValidationError({"username": "You are not an admin."})
#         if token := Token.objects.filter(user=user).first():
#             token.delete()
#         token = Token.objects.create(user=user)
#         return token
#
#     def remove(self, validated_data):
#         username = validated_data['username']
#         user = User.objects.filter(username=username).first()
#         if token := Token.objects.filter(user=user).first():
#             token.delete()
#         return token

class ProfilesSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =('id', 'username', 'first_name', 'last_name'
                 , 'email', 'is_staff', 'is_superuser', 'is_active',
                 'date_joined', 'last_login','requested_projects','phone_number','authorized')

class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','fullname')

class UserEditSerializer(serializers.ModelSerializer):
    # password=serializers.CharField(write_only=True)
    phone_number=serializers.CharField(validators=[validate_phone_number])

    # def update(self, instance, validated_data):
    #     if instance.phone_number[0] != 0:
    #         self.returnStatus(-1)
    #         # content = {'username':"None",'Error': "It's not a valid phone number"}
    #         # return Response(status=status.HTTP_400_BAD_REQUEST)
    #     return instance

    class Meta:
        model = User
        fields = ("first_name","last_name","phone_number","email","authorized")
        read_only_fields = ("authorized",)


class SetResumeIDSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("resumeID",)

class messageSerializer(serializers.Serializer):
    msg = serializers.CharField(max_length=200)

# class ChangePasswordSerializer(serializers.ModelSerializer):
#     password=serializers.CharField(write_only=True)
#     # phone_number=serializers.CharField(validators=[validate_phone_number])
#
#     # def update(self, instance, validated_data):
#     #     if instance.phone_number[0] != 0:
#     #         self.returnStatus(-1)
#     #         # content = {'username':"None",'Error': "It's not a valid phone number"}
#     #         # return Response(status=status.HTTP_400_BAD_REQUEST)
#     #     return instance
#
#     class Meta:
#         model = User
#         fields = ("password",)
#         # write_only_fields = ("password",)