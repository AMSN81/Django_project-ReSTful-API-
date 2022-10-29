import os

import django.db.models
from django.core.validators import MaxValueValidator, MinValueValidator, MinLengthValidator, RegexValidator,MaxLengthValidator
from .custom_validators import customValidator, validate_phone_number
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import pre_save
from django.utils import timezone
from django.utils.text import slugify


def get_filename_ext(filepath):
    base_name = os.path.basename(filepath)
    name , ext = os.path.splitext(base_name)
    return name , ext

def upload_img(instance,filename):
    name , ext = get_filename_ext(filename)
    final_name= f"{instance.id}"
    return f"users/{final_name}{ext}"

class User(AbstractUser):
    # email = models.EmailField(unique=True)
    email=models.EmailField(null=True,blank=True)
    username = models.CharField(max_length=20,null=True,unique=True)
    resumeID = models.IntegerField(null=True,blank=True,unique=True,default=None)
    password = None
    bio = models.TextField(max_length=120,null=True,blank=True)
    is_banned = models.BooleanField(default=False)
    warns = models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(3)])
    wallet = models.IntegerField(default=0)
    phone_number = models.CharField(validators=[validate_phone_number],max_length=11,null=True
                                  ,blank=True,default=None,unique=True)
    joined_active_projects = models.SmallIntegerField(validators=[MinValueValidator(0)],default=0)
    maximum_projects = models.SmallIntegerField(validators=[MinValueValidator(0)],default=1)
    date_joined = models.DateTimeField(default=timezone.now)
    requested_projects = models.ManyToManyField('Site_Project.Projects',related_name='requested_projects',blank=True)
    REQUIRED_FIELDS = []

    @property
    def authorized(self):
        if self.phone_number and self.first_name and self.last_name and self.email:
            return True
        return False

    def fullname(self):
        return self.first_name+" "+self.last_name
    # def save(self, *args, **kwargs):
    #     if self.warns == 3:
    #         self.is_banned = True
    #     super().save(*args,**kwargs)

def pre_save_for_user(sender,instance,*args,**kwargs):
    if instance.warns == 3:
        instance.is_banned = True
        instance.warns = 0
    if instance.is_banned == True:
        instance.maximum_projects = 0
    if instance.is_superuser:
        instance.is_banned = False
        instance.warns = 0

class genderSelect(models.TextChoices):
    male="m","male"
    female="f","female"

# class socialAbilities(models.TextChoices):

from Site_Project.models import Categories,Projects

# class resumeUser(models.Model):
#     user=models.OneToOneField(to=User,on_delete=models.CASCADE)
#     completedPercent=models.IntegerField(default=0,validators=[MinValueValidator(0),MaxValueValidator(100)])
#     title=models.CharField(max_length=40,null=True,blank=True)
#     state=models.CharField(max_length=40,null=True,blank=True)
#     city=models.CharField(max_length=40,null=True,blank=True)
#     national_code=models.CharField(validators=[MinLengthValidator(10),RegexValidator(r'^d{0,10}$')],max_length=10,null=True,blank=True)
#     birthday=models.DateField(null=True,blank=True)
#     gender=models.CharField(max_length=6,choices=genderSelect.choices,null=True,blank=True)
#     married=models.BooleanField(default=False)
#     about_me=models.TextField(blank=True,null=True)
#     programming_abilities=models.ManyToManyField(to=Categories)
    # social_abilities=models.CharField(choices=)
    # language=models.CharField(choices=)
#
class historyUser(models.Model):
    user=models.OneToOneField(to=User,on_delete=models.CASCADE)
    projects_Done = models.IntegerField(default=0)
    projects_Wanted = models.IntegerField(default=0)
    history_Done = models.ForeignKey(blank=True,null=True,to=Projects,on_delete=models.SET_NULL,related_name="history_Done")
    history_Wanted = models.ForeignKey(blank=True,null=True,to=Projects,on_delete=models.SET_NULL,related_name="history_Wanted")

    def __str__(self):
        return f"{self.user}-{self.user_id}"

    def save(self,*args,**kwargs):
        if self.user.is_banned == False:
            if self.projects_Done > 10:
                self.user.maximum_projects = 3
            elif self.projects_Done > 3:
                self.user.maximum_projects = 2
        self.user.save()
        super(historyUser,self).save(*args,**kwargs)

pre_save.connect(pre_save_for_user,sender=User)