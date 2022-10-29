from django.urls import path

from Site_Auth.views import activate_user, logout_page, login_page

urlpatterns = [
    path('#/activate/<uid>/<token>',activate_user,name="Activate_Channel"),
    path('test/login',login_page,name="test_login"),
    path('test/logout',logout_page,name="test_logout"),
]