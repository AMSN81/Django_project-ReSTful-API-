from django.contrib.auth import logout, authenticate, login
from django.shortcuts import render, redirect
from django.http.request import HttpRequest
from rest_framework import status
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import CreateAPIView
from requests import post
from rest_framework.permissions import AllowAny, IsAuthenticated
from Project1.settings import host_url
from Site_Auth.forms import newForm
from Site_User.models import User


def activate_user(request,uid,token):
    post(url=f"{host_url}api/v1/users/activation/",json={
        "uid":uid,
        "token":token,
    })
    return redirect("schema-swagger-ui")

def logout_page(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect("test_login")
    else:
        return redirect("test_login")


def login_page(request,*args,**kwargs):
    if request.user.is_authenticated:
        return redirect("schema-swagger-ui")
    form = newForm(request.POST or None)
    context={
        "form":form
    }
    if form.is_valid():
        username=form.cleaned_data.get("username")
        user=User.objects.get_or_create(username=username)[0]
        login(request,user)
        return redirect("schema-swagger-ui")
        # else:
        #     newUser=User.objects.create(username=username)
        #     login(request,newUser)
        #     return redirect("schema-swagger-ui")
    return render(request,"account/login.html",context)

# class authorize_user(APIView):
#     authentication_classes = (SessionAuthentication,TokenAuthentication)
#     permission_classes = (IsAuthenticated,)
#     def post(self,request):
#         username=request.data.get("username")
#         password=request.data.get("password")
#         user=authenticate(username=username,password=password)
#         if user:
#             login(request,user)
#             return Response({"success":True})
#         else:
#             return Response({"success":False})


