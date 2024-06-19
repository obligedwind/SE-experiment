from django import forms
from django.db import models
from django.contrib.auth.models import User
class NodeForm(forms.Form):
    node_id = forms.CharField(label='上传 ID序列')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)



class Node(models.Model):
    name = models.CharField(max_length=100)
    info = models.TextField()
    url = models.CharField(max_length=100)

class Edge(models.Model):
    source = models.ForeignKey(Node, related_name='source_node', on_delete=models.CASCADE)
    target = models.ForeignKey(Node, related_name='target_node', on_delete=models.CASCADE)