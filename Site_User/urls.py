from django.urls import path

from Site_User.views import adminCheck, bannedList , adminCheckByNumber , msg_all

urlpatterns = [
    path("admin/<str:todo>/number/<number>", adminCheckByNumber,name="API_admin_check"),
    path("admin/<str:todo>/id/<id_>", adminCheck,name="API_admin_check"),
    path("admin/msg_all", msg_all.as_view(),name="API_message_all"),
    path("admin/banned", bannedList,name="API_banned_list"),
    ]