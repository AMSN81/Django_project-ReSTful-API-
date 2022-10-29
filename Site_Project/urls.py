# from telegram import bot, InlineKeyboardMarkup, InlineKeyboardButton, update , Update
# from telegram.ext import CallbackQueryHandler , ConversationHandler

from Site_Project.views import ProjectsAPIView, ProjectBySlugAPIView, CreateProjectAPI, SearchProjectAPI, \
    allCategoriesAPI, RequestProjectAPI, sendedProjectsAPI, CheckRequestProjectAPI, ApplyRequestAPI, EditProjectAPI, \
    checkRequestsOfProjectAPI, changeFile, checkRequestAPI, RefuseRequestAPI, invalidateProjectAPI, \
    getUnverifiedProject, verifyProjectAPI, SearchAllProjectAPI, getProjectsCheckedByAdmin, \
    ProjectAllBySlugAPIView, ProjectByPkAPIView
from django.urls import path

urlpatterns = [
    path('projects/categories/<str:category>',ProjectsAPIView.as_view(),name="API_related_projects"),
    path('projects/request', RequestProjectAPI.as_view(), name="API_request_project"),
    path('projects/request/<int:pk>/apply', ApplyRequestAPI.as_view(), name="API_request_apply_project"),
    path('projects/request/<int:pk>/refuse', RefuseRequestAPI.as_view(), name="API_request_refuse_project"),
    path('projects/self/<str:slug>/requests', checkRequestsOfProjectAPI.as_view(), name="API_check_requests_of_project"),
    path('projects/self/request/<int:id>' , checkRequestAPI.as_view() , name="API_check_request"),
    path('projects/self/requests', CheckRequestProjectAPI.as_view(), name="API_check_requests_project"),
    path('projects/self/<int:pk>/edit', EditProjectAPI.as_view(), name="API_edit_project"),
    path('projects/self', sendedProjectsAPI.as_view(), name="API_sended_projects"),
    path('projects/file/<int:fileID>/<int:id>', changeFile, name="API_change_file"),
    path('projects/create', CreateProjectAPI.as_view(), name="API_project_create"),
    path('projects/get/unverified', getUnverifiedProject.as_view(), name="API_get_unverified_project"),
    path('projects/<str:slug>',ProjectBySlugAPIView.as_view(),name="API_project_by_slug"),
    path('projects/all/<str:slug>',ProjectAllBySlugAPIView.as_view(),name="API_project_all_by_slug"),
    path('projects/id/<int:pk>',ProjectByPkAPIView.as_view(),name="API_project_all_by_id"),
    path('projects/<int:id>/invalidate',invalidateProjectAPI.as_view(),name="API_invalidate_project"),
    path('projects/<int:id>/verify',verifyProjectAPI.as_view(),name="API_verify_project"),
    path('projects/search/<str:word>',SearchProjectAPI.as_view(),name="API_project_Search"),
    path('projects/search_all/<str:word>',SearchAllProjectAPI.as_view(),name="API_all_project_search"),
    path('categories',allCategoriesAPI.as_view(),name="API_categories"),
    path('projects/admin/checked_by',getProjectsCheckedByAdmin.as_view(),name="API_projects_checked_by_admin"),
]