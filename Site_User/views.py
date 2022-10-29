import telegram
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, redirect
from django.urls import reverse
from requests import post
from rest_framework import generics, status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny , IsAuthenticated , IsAdminUser
from rest_framework.authentication import SessionAuthentication , TokenAuthentication
from rest_framework.response import Response
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

from Project1.settings import host_url
from Project1.config import ADMIN_BOT, MAIN_BOT
from Site_User.models import User
from Site_User.serializers import RegisterSerializer, ProfilesSerializer, UserEditSerializer, \
    SetResumeIDSerializer, CreateTokenSerializer, AdminSerializer, messageSerializer
from utils.pagination import Pagination10
from utils.permissions import OnlySuperuser


class ProfileUserAPI(APIView):
    def get(self,request,*args,**kwargs):
        pk = kwargs["pk"]
        Request = User.objects.filter(id=pk)
        if not Request:
            return Response(status=status.HTTP_404_NOT_FOUND)
        data = Request.values()[0]
        new_data = { your_key: data[your_key] for your_key in ('id',"username","first_name","last_name","phone_number",
                                                               "email") }
        return Response(status=status.HTTP_200_OK,data=new_data)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)

# class CheckAdminAPI(APIView):
#     def get(self,request,*args,**kwargs):
#         pk = kwargs["pk"]
#         Request = User.objects.filter(id=pk,is_staff=True)
#         if not Request:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         data = Request.values()[0]
#         new_data = { your_key: data[your_key] for your_key in ('id',"username","first_name","last_name","phone_number",
#                                                                "email") }
#         return Response(status=status.HTTP_200_OK,data=new_data)
#
#     authentication_classes = (SessionAuthentication, TokenAuthentication)
#     permission_classes = (OnlySuperuser,)

class ProfileAPI(generics.ListAPIView):
    def get_queryset(self):
        queryset = User.objects.filter(id=self.request.user.id)
        return queryset
    serializer_class = ProfilesSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (SessionAuthentication , TokenAuthentication)

class EditUserAPI(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        user = self.request.user.id
        return User.objects.filter(id=user)
    authentication_classes = (SessionAuthentication,TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = UserEditSerializer


class LoginAPIWithToken(APIView):
    # def get_queryset(self):
    #     return Token.objects.all()
    serializer_class = CreateTokenSerializer
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    def post(self, request, *args, **kwargs):
        token = self.serializer_class.create(request, *args, **kwargs,validated_data=request.data)
        if token.user.is_banned:
            return Response(status=status.HTTP_403_FORBIDDEN,data={"message":"You are banned"})
        return Response(status=status.HTTP_200_OK, data={"token":token.key,"authorized":token.user.authorized,"is_staff":token.user.is_staff,"is_superuser":token.user.is_superuser})

# class LoginAdminAPI(APIView):
#     serializer_class = CreateTokenAdminSerializer
#     permission_classes = (AllowAny,)
#     authentication_classes = (SessionAuthentication, TokenAuthentication)
#     def post(self, request, *args, **kwargs):
#         token = self.serializer_class.create(request, *args, **kwargs,validated_data=request.data)
#         if token.user.is_banned:
#             return Response(status=status.HTTP_403_FORBIDDEN,data={"message":"You are banned"})
#         return Response(status=status.HTTP_200_OK, data={"token":token.key,"authorized":token.user.authorized})

class LogoutAPIWithToken(APIView):
    def get_queryset(self):
        return Token.objects.filter(user=self.request.user)
    serializer_class = CreateTokenSerializer
    permission_classes = (AllowAny,)
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    def get(self, request, *args, **kwargs):
        self.serializer_class.remove(request, *args, **kwargs,validated_data=request.data)
        return Response(status=status.HTTP_200_OK, data='Logout Successfully')
    # def post(self, request, *args, **kwargs):
    #     serializer = self.get_serializer(data=request.data)
    #     serializer.is_valid(raise_exception=True)
    #     user = serializer.validated_data
    #     login(request, user)
    #     token, created = Token.objects.get_or_create(user=user)
    #     return Response({"token": token.key}, status=status.HTTP_200_OK)

class SetResumeAPI(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        user = self.request.user.id
        return User.objects.filter(id=user)
    authentication_classes = (SessionAuthentication,TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = SetResumeIDSerializer

# class EditPasswordAPI(generics.RetrieveUpdateDestroyAPIView):
#     def get_queryset(self):
#         user = self.request.user.id
#         return User.objects.filter(id=user)
#     authentication_classes = (SessionAuthentication,TokenAuthentication)
#     permission_classes = (IsAuthenticated,)
#     serializer_class = ChangePasswordSerializer

class RegisterAPI(generics.CreateAPIView):
    def get_queryset(self, *args, **kwargs):
        return User.objects.all()

    # queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer

class GetAllAdminAPI(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        return User.objects.filter(Q(is_superuser=True)|Q(is_staff=True)).distinct()
    permission_classes = (OnlySuperuser,)
    serializer_class = AdminSerializer

class bannedList(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        return User.objects.filter(is_banned=True)
    pagination_class = Pagination10
    permission_classes = (OnlySuperuser,)
    serializer_class = ProfilesSerializer

# class LoginAPI(generics.CreateAPIView):
#     def get_queryset(self, *args, **kwargs):
#         return User.objects.all()
#
#     # queryset = User.objects.all()
#     permission_classes = (AllowAny,)
#     serializer_class = LoginSerializer

def adminCheck(request, id_, todo, *args, **kwargs):
    if request.method == "GET":
        try:
            TOKEN = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            # TOKEN = kwargs["Authorization"].split(" ")[1]
            user: User = Token.objects.get(key=TOKEN).user
            if user.is_superuser:
                if u:=User.objects.filter(id=id_).first():
                    if todo == 'superuser':
                        u.is_superuser = True
                        u.is_staff = True
                        u.save()
                    if todo == 'add':
                        if u.is_staff:
                            return HttpResponse(status=304,content='User is already an admin!')
                        u.is_staff = True
                        u.save()
                    elif todo == 'remove':
                        if not u.is_staff:
                            return HttpResponse(status=304, content="User isn't admin!")
                        u.is_staff = False
                        u.save()
                    elif todo == 'ban':
                        u.is_staff = False
                        u.is_banned = True
                        u.save()
                    else:
                        return HttpResponse(status=400, content='Bad request')
                else:
                    return HttpResponse(status=404,content=f'User ({id_}) not found')
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=403, content='Forbidden')
        except:
            return HttpResponse(status=401, content="Unauthorized")
    else:
        return HttpResponse(status=405, content="Method not allowed")

def adminCheckByNumber(request, number, todo, *args, **kwargs):
    if request.method == "GET":
        try:
            TOKEN = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            # TOKEN = kwargs["Authorization"].split(" ")[1]
            user: User = Token.objects.get(key=TOKEN).user
            if user.is_superuser:
                if u:=User.objects.filter(phone_number=number).first():
                    if todo == 'superuser':
                        u.is_superuser = True
                        u.is_staff = True
                        u.save()
                    if todo == 'add':
                        if u.is_staff:
                            return HttpResponse(status=304,content='User is already an admin!')
                        u.is_staff = True
                        u.save()
                    elif todo == 'remove':
                        if not u.is_staff:
                            return HttpResponse(status=304, content="User isn't admin!")
                        u.is_staff = False
                        u.save()
                    else:
                        return HttpResponse(status=400, content='Bad request')
                else:
                    return HttpResponse(status=404,content=f'User ({number}) not found')
                return HttpResponse(status=200)
            else:
                return HttpResponse(status=403, content='Forbidden')
        except:
            return HttpResponse(status=401, content="Unauthorized")
    else:
        return HttpResponse(status=405, content="Method not allowed")

# def msg_all(request,msg):
#     if request.method == "POST":
#         try:
#             TOKEN = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
#             # TOKEN = kwargs["Authorization"].split(" ")[1]
#             user: User = Token.objects.get(key=TOKEN).user
#             if user.is_superuser:
#                 users = User.objects.all()
#                 bot = telegram.Bot(token=ADMIN_BOT)
#                 for user in users:
#                     try:
#                         bot.send_message(chat_id=user.username, text=str(msg))
#                     except:
#                         pass
#                     return HttpResponse(status=200,content='Message sent successfully.')
#             else:
#                 return HttpResponse(status=403, content="Forbidden")
#         except:
#             return HttpResponse(status=401, content="Unauthorized")
#     else:
#         return HttpResponse(status=405, content="Method not allowed")

class msg_all(APIView):
    authentication_classes = (SessionAuthentication,TokenAuthentication)
    permission_classes = (OnlySuperuser,)
    def post(self,request):
        serializer = messageSerializer(data=request.data)
        if serializer.is_valid():
            msg = self.request.data['msg']
            users = User.objects.all().iterator()
            bot = telegram.Bot(token=MAIN_BOT)
            for user in users:
                try:
                    bot.send_message(chat_id=user.username, text=str(msg))
                except:
                    pass
            return Response(status=status.HTTP_200_OK,data='Message sent successfully.')
        return Response(serializer.errors,status=status.HTTP_400_BAD_REQUEST)