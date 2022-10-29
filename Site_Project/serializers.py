from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from Site_Project.models import Projects, Categories, ReqProject, Report
from Site_User.models import User

# class requestApplySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = ReqProject
#         fields = "__all__"
#         read_only_fields = ("applicant","details","project")

class ProjectEditSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(), many=True)
    class Meta:
        model = Projects
        fields = ("id","name","description","price","category","slug","employer","freelancer","condition",'fileID','categories')
        read_only_fields = ("slug","employer","freelancer","condition","created_at","updated_at","fileID")

class RequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReqProject
        fields = ('id',)

class newRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReqProject
        fields = ('id','applicantFullName','applicant','details','project','applied','projectName','resumeID')

class ProjectsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Projects
        fields=("id","slug","name","price","description","employerName","employer","__str__","category","categories","condition")

class CategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields ="__all__"

class ProjectCreateSerializer(serializers.ModelSerializer):
    category = serializers.PrimaryKeyRelatedField(queryset=Categories.objects.all(),many=True)
    class Meta:
        model = Projects
        fields = ('name', 'description', 'price', 'category' , 'id')
        read_only_fields = ('id',)

    # def create(self,validated_data):
    #     new_project = Projects.objects.create(
    #         name=validated_data['name'],
    #         employer=self.context['request'].user,
    #         description=validated_data['description'],
    #         price=validated_data['price'])
    #     new_project.category.set(validated_data['category'])
    #     new_project.save()
    #     return new_project


    # def validate(self, attrs):
    #     if attrs['password'] != attrs['password2']:
    #         raise serializers.ValidationError({"password": "Password fields didn't match."})
    #     if User.objects.filter(username=attrs["username"]).first():
    #         raise serializers.ValidationError({"username": "an account with this username already exists."})
    #     return attrs
    # def validate(self, attrs):
    #     return attrs

    def create(self, validated_data):
        new_project = Projects.objects.create(
            name=validated_data['name'],
            employer=self.context['request'].user,
            description=validated_data['description'],
            price=validated_data['price'],
        )
        # if not Token.objects.filter(user=user).first():
        #     Token.objects.create(user=user)
        new_project.category.set(validated_data['category'])
        new_project.save()

        return new_project

class CheckRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReqProject
        fields = ('id','applicant','details','project','applied','projectName','seen','projectSlug')

class setReportConditionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id','condition','checked_by')
        read_only_fields = ('id','checked_by')

class RequestProjectSerializer(serializers.ModelSerializer):
    def user(self):
        return self.context['request'].user
    project = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.filter(condition="v"))
    class Meta:
        model = ReqProject
        fields = ('project','details')

    def create(self, validated_data):
        if ReqProject.objects.filter(applicant=self.user(),project=validated_data['project']).first():
            raise serializers.ValidationError({"project": "You have already requested this project."}, code=401)
        new_request = ReqProject.objects.create(
            applicant=self.user(),
            project=validated_data['project'],
            details=validated_data['details']
        )
        new_request.save()
        return new_request

class CreateReportSerializer(serializers.ModelSerializer):
    def user(self):
        return self.context['request'].user
    # project = serializers.PrimaryKeyRelatedField(queryset=Projects.objects.filter(condition="v"))
    class Meta:
        model = Report
        fields = ('type','title','details','reported_user')

    def create(self, validated_data):
        new_report = Report.objects.create(
            reporter=self.user(),
            type=validated_data['type'],
            title=validated_data['title'],
            details=validated_data['details'],
            reported_user=validated_data['reported_user']
        )
        new_report.save()
        return new_report

class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ('id','type','title','details','condition','reported_user','reporter','created_at','get_time_diff','slug')
        read_only_fields = ('reporter','created_at')