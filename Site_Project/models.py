import os

from django.core.exceptions import ValidationError
from django.db.models import Q
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.text import slugify
from django.http.response import BadHeaderError

from Site_User.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator ,MinLengthValidator
# Create your models here.

class Categories(models.Model):
    category=models.CharField(unique=True,max_length=16)

    def __str__(self):
        return self.category

    class Meta:
        verbose_name="Category"
        verbose_name_plural="Categories"

class projectManager(models.Manager):
    def get_active(self):
        return self.get_queryset().filter(condition="a")
    def get_verified(self):
        return self.get_queryset().filter(condition="v")
    def search(self,search):
        lookup=(
                Q(name__icontains=search) |
                Q(employer__first_name__icontains=search) |
                Q(employer__last_name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__category__icontains=search)
        )
        return self.get_verified().filter(lookup).distinct()
    def search_all(self,search):
        lookup=(
                Q(name__icontains=search) |
                Q(employer__first_name__icontains=search) |
                Q(employer__last_name__icontains=search) |
                Q(description__icontains=search) |
                Q(category__category__icontains=search)
        )
        return self.all().filter(lookup).distinct()

def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name , ext = os.path.splitext(base_name)
    return name , ext

def upload_file_project(instance,filename):
    name , ext = get_filename_ext(filename)
    final_name= f"{instance.name}-{Projects.objects.filter(name=instance.name).count()}"
    return f"projects/{final_name}{ext}"

class projectCondition(models.TextChoices):
    active="a","active"
    verified="v","verified"
    pending="p","pending"
    refused="r","refused"
    cancelled="c","cancelled"
    done="d","done"

class Projects(models.Model):
    name=models.CharField(validators=[MinLengthValidator(8)],max_length=30)
    description=models.TextField()
    employer=models.ForeignKey(to=User,on_delete=models.CASCADE,related_name="employer")
    slug=models.SlugField(unique=True,null=True,blank=True)
    fileID=models.IntegerField(null=True,blank=True,unique=True)
    freelancer=models.ForeignKey(blank=True,default=None,null=True,to=User,on_delete=models.CASCADE,related_name="freelancer")
    price=models.PositiveIntegerField(default=10000,validators=[MinValueValidator(10000),MaxValueValidator(10000000)])
    category=models.ManyToManyField(to=Categories)
    submit_Date=models.DateTimeField(auto_now_add=True)
    is_done=models.BooleanField(default=False)
    done_Date=models.DateTimeField(null=True,blank=True)
    # active=models.BooleanField(default=True)
    condition=models.CharField(max_length=1,choices=projectCondition.choices,default=projectCondition.active)
    checked_by=models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True)
    objects=projectManager()
    # seen=models.PositiveIntegerField(default=0)
    # verified_seen=models.BooleanField(default=False)
    # verified=models.BooleanField(default=False)

    @property
    def categories(self):
        c=""
        g=self.category.count()
        for n in range(0,g):
            id=self.category.values()[n]['id']
            new=Categories.objects.filter(id=id).first()
            c += f'{new},'
        return c

    def warn(self):
        self.condition = projectCondition.refused
        self.employer.warns += 1
        self.save()
        self.employer.save()

    def ban(self):
        self.condition = projectCondition.refused
        self.employer.is_banned = True
        self.save()
        self.employer.save()

    def invalidate(self):
        self.condition = projectCondition.refused
        self.save()

    def validate(self):
        self.condition = projectCondition.verified
        self.save()

    @property
    def employerName(self):
        return self.employer.fullname()

    class Meta:
        verbose_name="Project"
        verbose_name_plural="Projects"

    def __str__(self):
        return f"{self.name}-{self.employer}-{self.price}-{self.id}"

def pre_save_for_project(sender, instance:Projects, *args, **kwargs):
    if instance.is_done:
        instance.done_Date = timezone.now()
    if not Projects.objects.filter(name=instance.name).first():
        if not instance.slug:
            instance.slug = slugify(instance.name)
    else:
        if not instance.slug:
            x = instance.name + str(Projects.objects.filter(name=instance.name).count())
            instance.slug = slugify(x)
    if instance.freelancer:
        instance.condition = projectCondition.pending
    p = Projects.objects.filter(id=instance.id).first()
    if p:
        if p.name != instance.name or p.description != instance.description:
            instance.condition = projectCondition.active
    if instance.condition == projectCondition.refused or projectCondition.cancelled:
        rep = Report.objects.filter(type=ReportType.project, title=instance.id).first()
        if rep:
            rep.condition = ReportCondition.solved
            rep.save()

class ReqProject(models.Model):
    applicant = models.ForeignKey(to=User, related_name="applicant",on_delete=models.CASCADE)
    project = models.ForeignKey(to=Projects, related_name="project",on_delete=models.CASCADE)
    details = models.TextField()
    has_seen = models.BooleanField(default=False)
    applied = models.BooleanField(null=True,blank=True)

    # @property
    # def did_send(self):
    #     if ReqProject.objects.filter(applicant=self.applicant,project=self.project).first():
    #         return True
    #     return False

    def warn(self):
        self.applied = False
        self.applicant.warns += 1
        self.save()
        self.applicant.save()

    def ban(self):
        self.applied = False
        self.applicant.is_banned = True
        self.save()
        self.applicant.save()

    @property
    def projectSlug(self):
        return self.project.slug

    @property
    def resumeID(self):
        return self.applicant.resumeID

    @property
    def applicantName(self):
        return self.applicant.username
    @property
    def applicantFullName(self):
        return self.applicant.fullname()

    @property
    def seen(self):
        if self.applied is not None:
            if self.has_seen:
                return True
            self.has_seen = True
            self.save()
            return False
        return False

    @property
    def projectName(self):
        return self.project.name

    def __str__(self):
        return f"{self.applicant}--->{self.project}"

    def save(self,*args,**kwargs):
        q = ReqProject.objects.filter(applicant=self.applicant,project=self.project).first()
        # if self.applicant.joined_active_projects >= self.applicant.maximum_projects:
        #     raise ValueError("Please request when you have done your recent projects")
        if q and q != self:
            raise ValueError("You've been requested for this project before")
        elif self.applicant == self.project.employer:
            raise ValueError("You can't request for your own project")
        # elif self.project.condition != "v":
        #     raise ValueError("This project isn't verified")
        elif self.applied == True:
            project = Projects.objects.filter(id=self.project.id).first()
            project.condition = "p"
            project.freelancer = self.applicant
            project.save()
            super(ReqProject, self).save(*args, **kwargs)
        else:
            super(ReqProject, self).save(*args, **kwargs)
            self.applicant.requested_projects.add(self.project)
            self.applicant.save()

    def apply(self,*args,**kwargs):
        self.applied = True
        self.save(*args,**kwargs)

    def refuse(self,*args,**kwargs):
        self.applied = False
        self.save(*args,**kwargs)

    def delete(self, using=None, keep_parents=False):
        if self.project in self.project.employer.requested_projects.all():
            self.applicant.requested_projects.remove(self.project)
            self.applicant.save()
        super(ReqProject, self).delete(using, keep_parents)
            # project = Projects.objects.filter(id=self.project_id).first()
            # project.condition = "v"
            # project.freelancer = None
            # project.save()
            # self.project.employer.requested_projects.remove(self.project)
            # self.project.employer.save()

class ReportCondition(models.TextChoices):
    ban = "b", "Ban"
    warning = 'w', 'Warning'
    false = 'f', 'False'
    pending = 'p', 'Pending'
    solved = 's', 'Solved'
    ignored = 'i', 'Ignored'

class ReportType(models.TextChoices):
    project = "p", "Project"
    request = "r", "Request"
    # freelancer = "f", "Freelancer"
    # employer = "e", "Employer"
    # admin = "a", "Admin"
    # user = "u", "User"
    bug = "b", "Bug"

class ReportManager(models.Manager):
    def search(self,search):
        lookup=(
                Q(reporter__first_name__icontains=search) |
                Q(reporter__last_name__icontains=search)
        )
        return self.all().filter(lookup).distinct()
    def search_by_condition(self,search:None,condition):
        if search:
            lookup=(
                    Q(reporter__first_name__icontains=search) |
                    Q(reporter__last_name__icontains=search) |
                    Q(condition=condition)
            )
        else:
            lookup = (
                    Q(condition=condition)
            )
        return self.all().filter(lookup).distinct()
    # def search_by_day(self,date:None):
    #     if date:
    #         return self.all().filter(create_date=date).distinct()
    #     else:
    #         return self.all().filter(create_date=timezone.now().date()).distinct()

class Report(models.Model):
    reporter = models.ForeignKey(to=User, related_name="reporter",on_delete=models.CASCADE)
    type = models.CharField(max_length=1,choices=ReportType.choices,default=ReportType.bug)
    title = models.CharField(max_length=40)
    details = models.TextField(null=True,blank=True)
    # reported_user = models.ForeignKey(to=User, related_name="reported_user",on_delete=models.CASCADE,null=True,blank=True)
    admin_message = models.TextField(null=True,blank=True)
    condition = models.CharField(max_length=1,choices=ReportCondition.choices,default=ReportCondition.pending)
    created_at = models.DateTimeField(auto_now_add=True)
    # create_date=created_at.date()
    checked_by = models.ForeignKey(User,on_delete=models.PROTECT,null=True,blank=True)
    objects = ReportManager()

    @property
    def reported(self):
        if self.type == ReportType.project:
            p = Projects.objects.filter(id=self.title).first()
            if p:
                return p.employer
        elif self.type == ReportType.request:
            r = ReqProject.objects.filter(id=self.title).first()
            if r:
                return r.applicant

    @property
    def reported_user(self):
        if self.reported.id:
            return self.reported.id
        return None

    @property
    def slug(self):
        if self.type == ReportType.project and self.title.isdigit():
            return Projects.objects.filter(id=self.title).first().slug
        elif self.type == ReportType.request and self.title.isdigit():
            return ReqProject.objects.filter(id=self.title).first().projectSlug
        return None

    @property
    def get_time_diff(self):
        timediff = timezone.now() - self.created_at
        if timediff.days > 0:
            return f"{timediff.days} days ago"
        elif timediff.seconds > 3600:
            return f"{timediff.seconds // 3600} hours ago"
        elif timediff.seconds > 60:
            return f"{timediff.seconds // 60} minutes ago"
        else:
            return f"{timediff.seconds} seconds ago"

    def __str__(self):
        return f"{self.reporter}--->{self.title}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.type == 'p':
            if not Projects.objects.filter(id=self.title).first():
                raise ValidationError('There is no project with this id!')
        elif self.type == 'r':
            if not ReqProject.objects.filter(id=self.title).first():
                raise ValidationError('There is no request with this id!')
        return self

def pre_save_for_report(sender, instance, *args, **kwargs):
    instance.full_clean()
    if instance.type == ReportType.request:
        req = ReqProject.objects.filter(id=int(instance.title)).first()
        req.applied = False
        req.save()
    if instance.condition == "f":
        instance.reporter.warns += 1
        instance.reporter.save()
    if instance.type != ReportType.bug:
        if instance.condition == "w":
            instance.reported.warns += 1
            instance.reported.save()
            if instance.type == ReportType.project:
                project = Projects.objects.filter(id=instance.title).first()
                project.condition = projectCondition.refused
                project.save()
        elif instance.condition == "b":
            instance.reported.is_banned = True
            instance.reported.save()
            if instance.type == ReportType.project:
                project = Projects.objects.filter(id=instance.title).first()
                project.condition = projectCondition.refused
                project.save()


pre_save.connect(pre_save_for_project,sender=Projects)
pre_save.connect(pre_save_for_report,sender=Report)
