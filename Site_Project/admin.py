from django.contrib import admin

# Register your models here.
from Site_Project.models import Categories, Projects, ReqProject, Report


class admin_projects(admin.ModelAdmin):
    list_display = ["__str__","condition","categories"]
    list_editable = ["condition"]
    list_filter = ["category","condition"]
    ordering = ["submit_Date"]

    def categories(self, obj):
        return "\n".join([p.category for p in obj.category.all()])

class admin_reqs(admin.ModelAdmin):
    list_display = ["__str__","has_seen","applied"]

class admin_reports(admin.ModelAdmin):
    list_display = ["type","__str__","condition"]
    search_fields = ["type","__str__","condition"]
    list_filter = ["type","condition"]
    list_editable = ["condition"]

admin.site.register(Categories)
admin.site.register(Report,admin_reports)
admin.site.register(ReqProject,admin_reqs)
admin.site.register(Projects,admin_projects)