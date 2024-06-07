from django import forms
from django.db import models
from django.contrib.auth.models import User
class NodeForm(forms.Form):
    node_id = forms.CharField(label='上传 ID序列')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
