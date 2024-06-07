from django.shortcuts import render
from .models import NodeForm
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
def get_node_data(node_id):
    class Node:
        def __int__(self):
            self.nodeid = node_id
            self.teachers = ['lx']
            self.students = ['yl']
    node = Node()
    return node


def node_detail(request):
    if request.method == 'POST':
        form = NodeForm(request.POST)
        if form.is_valid():
            node_id = form.cleaned_data['node_id']
            node_data = get_node_data(node_id)
            return render(request, 'node_detail.html', {'node_data': node_data})
    else:
        form = NodeForm()
    return render(request, 'node_form.html', {'form': form})
def index(request):
    return render(request, 'index.html')
def append(request):
    if request.method == 'POST':
        # 获取当前用户
        user = request.user
        phone_number = user.userprofile.phone_number

        # 获取POST请求中的导师和学生参数
        teacher = request.POST.get('teacher')
        student = request.POST.get('student')
        # 处理业务逻辑，例如保存到数据库
        t = request.POST.get('is_teacher', 'false') == 'true'  # 根据需要确定导师/学生的布尔值
    return render(request,'append.html')



