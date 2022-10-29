from django.contrib import admin

# Register your models here.
from Site_User.models import User,historyUser


class UserModelManager(admin.ModelAdmin):
    list_display = ["username","first_name","last_name","phone_number"]
    class Meta:
        model = User


admin.site.register(User,UserModelManager)
admin.site.register(historyUser)
