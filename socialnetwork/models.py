import datetime
from django.db import models
from django.utils import timezone

# User class for built-in authentication module
from django.contrib.auth.models import User
class Profile(models.Model):
	user = models.OneToOneField(User)
	age = models.IntegerField(blank=True, max_length = 3, null=True)
	bio = models.CharField(blank=True, max_length =430)
	picture_url   = models.CharField(blank=True, max_length=256)
	followusers = models.ManyToManyField(User,related_name='follow+')

class Posts(models.Model):
	post_content=models.CharField(max_length=160,default="none")
	user = models.ForeignKey(User,default="none")
	date_time=models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
	comment_text =models.CharField(max_length=160,default="none")
	comment_datetime = models.DateTimeField(auto_now_add=True)
	comment_by = models.ForeignKey(Profile)
	comment_post=models.ForeignKey(Posts)
