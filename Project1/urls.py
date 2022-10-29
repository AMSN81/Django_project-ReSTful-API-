# from django.contrib import admin
# from django.urls import path, include
from django.conf.urls.static import static
# from djoser.urls.base import router
#
from Project1 import settings
# from Site_User.views import RegisterView
#
# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('',include("Site_User.urls")),
#     # path('api/v1/', include(router.urls)),
#     path('api/auth/', include('djoser.urls')),
#     path('api/auth/', include('djoser.urls.jwt')),
#
#
    # path('api/auth/register', RegisterView.as_view(),name="RegisterAPI"),
# ]

from django.contrib import admin
from django.urls import path
from django.urls.conf import include, re_path

# DRF YASG
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from Site_Project.views import newReportAPI, checkReportAPI, setReportConditionAPI, ReportByID, SearchAllReportAPI, \
    getReportsCheckedByAdmin
from Site_User.views import RegisterAPI, ProfileAPI, EditUserAPI, ProfileUserAPI, SetResumeAPI, \
    LoginAPIWithToken, LogoutAPIWithToken, GetAllAdminAPI

schema_view = get_schema_view(
    openapi.Info(
        title="Djoser API",
        default_version="v1",
        description="REST implementation of Django authentication system. djoser library provides a set of Django Rest Framework views to handle basic actions such as registration, login, logout, password reset and account activation. It works with custom user model.",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path("admin/", admin.site.urls),
    re_path(
        r"^api/v1/docs/$",
        schema_view.with_ui("swagger", cache_timeout=0),
        name="schema-swagger-ui",
    ),
    # path('api/v1/', include('djoser.urls.authtoken')),
    path("", include("Site_Auth.urls")),
    path("api/v1/", include("Site_Project.urls")),
    path("api/v1/auth/", include("djoser.urls")),
    # path("api/v1/", include("djoser.urls.jwt")),
    path('api/v1/', include("Site_User.urls")),
    path('api/v1/auth/register', RegisterAPI.as_view(), name="RegisterAPI"),
    path('api/v1/admin/all', GetAllAdminAPI.as_view(), name="GetAllAdminAPI"),
    # path('api/v1/admin/check/<int:pk>', CheckAdminAPI.as_view(), name="CheckAdminAPI"),
    path('api/v1/user/me', ProfileAPI.as_view(), name="ProfileAPI"),
    path('api/v1/user/<int:pk>', ProfileUserAPI.as_view(), name="ProfileUserAPI"),
    path('api/v1/user/resume/<pk>', SetResumeAPI.as_view(), name="ResumeSetAPI"),
    path('api/v1/user/me/edit/<pk>', EditUserAPI.as_view(), name="UserEditAPI"),


    path('api/v1/report', newReportAPI.as_view(), name="NewReportAPI"),
    path('api/v1/report/<int:id>', ReportByID.as_view(), name="CheckReportAPI"),
    path('api/v1/report/set/<int:pk>', setReportConditionAPI.as_view(), name="SetReportConditionAPI"),
    path('api/v1/reports/<str:type>', checkReportAPI.as_view(), name="CheckReportAPI"),
    path('api/v1/reports/search_all/<str:word>',SearchAllReportAPI.as_view(),name="API_all_report_search"),
    path('api/v1/reports/admin/checked_by', getReportsCheckedByAdmin.as_view(), name="API_reports_checked_by_admin"),
    # path('api/v1/user/me/password/<pk>', EditPasswordAPI.as_view(), name="EditPasswordAPI"),

    path('api/v1/login', LoginAPIWithToken.as_view(), name="TokenLoginAPI"),
    # path('api/v1/admin/login', LoginAdminAPI.as_view(), name="TokenLoginAPI"),
    path('api/v1/logout', LogoutAPIWithToken.as_view(), name="TokenLogoutAPI"),

]

if settings.DEBUG:
    urlpatterns=urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
