import json

from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect

# Create your views here.
from djoser.social import token
from rest_framework import generics, status, authtoken
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from Site_Project.serializers import ProjectsSerializer, ProjectCreateSerializer, CategoriesSerializer, \
    RequestProjectSerializer, RequestSerializer, ProjectEditSerializer, CheckRequestSerializer, CreateReportSerializer, \
    newRequestSerializer, ReportSerializer, setReportConditionSerializer
from Site_User.models import User
from Site_Project.models import Projects, Categories, ReqProject, Report

# class ProjectsAPIView(APIView):
#     def get(self,request,*args,**kwargs):
#         print(kwargs)
#         category = kwargs["category"]
#         related_Projects = Projects.objects.filter(category__category=category,active=True).order_by('submit_Date').values()
#         print(related_Projects)
#         return Response(related_Projects)
#     authentication_classes = (SessionAuthentication,TokenAuthentication)
#     permission_classes = (AllowAny,)
from utils.pagination import Pagination10
from utils.permissions import IsStaffOrReadOnly


class ProjectsAPIView(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        category = self.kwargs["category"]
        return Projects.objects.filter(category__category=category, condition="v").order_by('submit_Date')

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination10


class ReportByID(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        id = self.kwargs['id']
        return Report.objects.filter(id=id)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser,)


class ProjectBySlugAPIView(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs["slug"]
        return Projects.objects.filter(slug=slug, condition='v')

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    permission_classes = (IsAuthenticated,)


class ProjectAllBySlugAPIView(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        slug = self.kwargs["slug"]
        return Projects.objects.filter(slug=slug)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    permission_classes = (IsAuthenticated,)


class ProjectByPkAPIView(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        id_ = self.kwargs["pk"]
        return Projects.objects.filter(id=id_)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    permission_classes = (IsAdminUser,)


# class ProjectSendBySlugAPIView(APIView):
#     def get_queryset(self,*args,**kwargs):
#         slug = self.kwargs["slug"]
#         return Projects.objects.filter(slug=slug,active=True).order_by('submit_Date')
#     authentication_classes = (SessionAuthentication, TokenAuthentication)
#     permission_classes = (IsAuthenticated,)

class allCategoriesAPI(generics.ListAPIView):
    def get_queryset(self):
        return Categories.objects.all()

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = CategoriesSerializer
    permission_classes = (IsAuthenticated,)


class sendedProjectsAPI(generics.ListAPIView):
    def get_queryset(self):
        return Projects.objects.filter(employer=self.request.user)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    pagination_class = Pagination10
    permission_classes = (IsAuthenticated,)


class checkRequestsOfProjectAPI(generics.ListAPIView):
    def get_queryset(self):
        slug = self.kwargs["slug"]
        return ReqProject.objects.filter(project__slug=slug, applied=None)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = RequestSerializer
    pagination_class = Pagination10
    permission_classes = (IsAuthenticated,)


class checkRequestAPI(generics.ListAPIView):
    def get_queryset(self):
        id = self.kwargs["id"]
        return ReqProject.objects.filter(id=id)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = newRequestSerializer
    permission_classes = (IsAuthenticated,)


# def checkseenRequests(request,id,TOKEN):
#     if request.method == "GET":
#         if TOKEN:
#             try:
#                 user = User.objects.get(token=TOKEN)
#             except:
#                 return HttpResponse(status=401,content="Unauthorized1")
#         else:
#             return HttpResponse(status=401,content="Unauthorized2")
#         req = ReqProject.objects.filter(applicant=user,seen=False,id=id)
#         if req:
#             req.update(seen=True)
#             return HttpResponse(status=200,content="seen")
#         else:
#             return HttpResponse(status=400,content="bad request")
#     return HttpResponse(status=401,content="Unauthorized3")
# return ReqProject.objects.filter(project__employer=self.request.user,project__slug=slug,seen=False)

class ApplyRequestAPI(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        Request = ReqProject.objects.filter(project__employer=self.request.user, id=pk, project__condition="v").first()
        if Request:
            Request.apply()
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK,
                        data={'applicant': Request.applicant.username, 'project': Request.project.name})

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    # serializer_class = requestApplySerializer


class RefuseRequestAPI(APIView):
    def get(self, request, *args, **kwargs):
        pk = kwargs["pk"]
        Request = ReqProject.objects.filter(project__employer=self.request.user, id=pk, project__condition="v").first()
        if Request:
            Request.refuse()
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_200_OK,
                        data={'applicant': Request.applicant.username, 'project': Request.project.name})

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    # serializer_class = requestApplySerializer


class invalidateProjectAPI(APIView):
    def get(self, request, *args, **kwargs):
        id = kwargs["id"]
        project = Projects.objects.filter(id=id).first()
        if project:
            project.invalidate()
            project.checked_by = self.request.user
            project.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAdminUser,)


class verifyProjectAPI(APIView):
    def get(self, request, *args, **kwargs):
        id = kwargs["id"]
        project = Projects.objects.filter(id=id).first()
        if project:
            project.validate()
            project.checked_by = self.request.user
            project.save()
            return Response(status=status.HTTP_200_OK)
        return Response(status=status.HTTP_404_NOT_FOUND)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAdminUser,)


class getUnverifiedProject(generics.ListAPIView):
    def get_queryset(self):
        return Projects.objects.filter(condition='a')

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    permission_classes = (IsAdminUser,)


class setReportConditionAPI(generics.RetrieveUpdateAPIView):
    def get_queryset(self):
        rep = Report.objects.filter(id=self.kwargs['pk']).first()
        if (not rep.checked_by) and (rep.condition == 'p'):
            rep.checked_by = self.request.user
            rep.save()
        return rep
    serializer_class = setReportConditionSerializer
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAdminUser,)


class EditProjectAPI(generics.RetrieveUpdateDestroyAPIView):
    def get_queryset(self):
        pk = self.kwargs["pk"]
        return Projects.objects.filter(employer=self.request.user, id=pk).filter(Q(condition='v') | Q(condition='p'))
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectEditSerializer


class newReportAPI(generics.CreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = CreateReportSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(reporter=self.request.user)
        return Response(status=status.HTTP_201_CREATED)


class checkReportAPI(generics.ListAPIView):
    def get_queryset(self):
        type = self.kwargs["type"]
        return Report.objects.filter(condition='p', type=type)
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = Pagination10


class CreateProjectAPI(generics.CreateAPIView):
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = ProjectCreateSerializer


# class RequestProjectAPI(generics.CreateAPIView):
#     def get_queryset(self, *args, **kwargs):
#         return ReqProject.objects.all()
#     authentication_classes = (SessionAuthentication,TokenAuthentication)
#     permission_classes = (IsAuthenticated,)
#     serializer_class = RequestProjectSerializer

class RequestProjectAPI(APIView):
    def get_queryset(self, *args, **kwargs):
        return ReqProject.objects.all()

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = RequestProjectSerializer

    def post(self, request, *args, **kwargs):
        serializer = RequestProjectSerializer(data=request.data)
        if serializer.is_valid():
            # serializer.save(applicant=request.user)
            ReqProject.objects.create(applicant=request.user, **serializer.validated_data)
            x = Projects.objects.filter(id=serializer.data["project"]).first()
            return Response(data={'request': serializer.data,
                                  'employer': x.employer.username, 'project': x.name}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def changeFile(request, fileID, id, *args, **kwargs):
    if request.method == "GET":
        try:
            TOKEN = request.META["HTTP_AUTHORIZATION"].split(" ")[1]
            # TOKEN = kwargs["Authorization"].split(" ")[1]
            user = Token.objects.get(key=TOKEN).user
        except:
            return HttpResponse(status=401, content="Unauthorized")
        try:
            project = Projects.objects.get(id=id)
        except:
            return HttpResponse(status=404, content="Project not found")
        if project.employer == user:
            project.fileID = fileID
            project.save()
            return HttpResponse(status=200, content="File changed")
        else:
            return HttpResponse(status=403, content="Forbidden")
    else:
        return HttpResponse(status=400, content="Method not allowed")


class CheckRequestProjectAPI(generics.ListAPIView):
    def get_queryset(self, *args, **kwargs):
        return ReqProject.objects.filter(applicant=self.request.user)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    permission_classes = (IsAuthenticated,)
    serializer_class = CheckRequestSerializer


class SearchProjectAPI(generics.ListAPIView):
    def get_queryset(self):
        search = self.kwargs["word"]
        return Projects.objects.search(search=search)

    permission_classes = (IsAuthenticated,)
    pagination_class = Pagination10
    serializer_class = ProjectsSerializer


class SearchAllProjectAPI(generics.ListAPIView):
    def get_queryset(self):
        search = self.kwargs["word"]
        return Projects.objects.search_all(search=search)

    permission_classes = (IsAdminUser,)
    pagination_class = Pagination10
    serializer_class = ProjectsSerializer


class SearchAllReportAPI(generics.ListAPIView):
    def get_queryset(self):
        search = self.kwargs["word"]
        return Report.objects.search(search=search)
    permission_classes = (IsAdminUser,)
    pagination_class = Pagination10
    serializer_class = ReportSerializer


class getProjectsCheckedByAdmin(generics.ListAPIView):
    def get_queryset(self):
        return Projects.objects.filter(checked_by=self.request.user)

    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ProjectsSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = Pagination10


class getReportsCheckedByAdmin(generics.ListAPIView):
    def get_queryset(self):
        return Report.objects.filter(checked_by=self.request.user)
    authentication_classes = (SessionAuthentication, TokenAuthentication)
    serializer_class = ReportSerializer
    permission_classes = (IsAdminUser,)
    pagination_class = Pagination10



