from django.shortcuts import render,redirect
from .models import NodeForm
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.auth.models import User
import matplotlib.pyplot as plt
import numpy as np
from django.http import HttpResponse
import graphviz
import json
from  . import main
import psycopg2
db = psycopg2.connect(host='localhost',
                      port='5432',
                      user='postgres',
                      dbname='software',
                      password='123')

cursor = db.cursor()
st=None
nodes = None
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
    if not request.user.is_authenticated:
        return redirect('login')  # 'login' 是你在 URL 配置中定义的登录视图的名称
    global st, nodes
    user_phone= request.user.userprofile.phone_number
    user_name = request.user.username
    st = main.login(user_phone, user_phone)
    nodes = st.nodes
    return render(request, 'index.html')
def append(request):
    if request.method == 'POST':
        # 获取当前用户
        user = request.user
        phone_number = user.userprofile.phone_number
        st = main.login(phone_number, phone_number)
        # 获取POST请求中的导师和学生参数
        teacher = request.POST.get('teacher')
        phone1 = request.POST.get('phone1')
        student = request.POST.get('student')
        phone2 = request.POST.get('phone2')
        # 处理业务逻辑，例如保存到数据库

        if phone2 in st.nodes.keys():
            # 表示当前是stu
            node = st.nodes[phone2]
            node.append(name=teacher, phone=int(phone1), t=True)
        else:
            node = st.nodes[phone1]
            node.append(name=student, phone=int(phone2), t=False)
            # 表示当前是tea
    return render(request,'append.html')
def view(request):
    user = request.user
    phone_number = user.userprofile.phone_number
    st = main.login(phone_number, phone_number)
    # 删除所有 Node 记录
    Node.objects.all().delete()
    # 删除所有 Edge 记录
    Edge.objects.all().delete()

    nodes = Node.objects.all()
    edges = Edge.objects.all()

    n_dict = {}
    for n in st.nodes.values():
        # pic_nodes.append(n.id)
        # return HttpResponse(f"{n.id} + {n.page}")
        url = n.page
        if(url is None):
            url = "https://homepage.hit.edu.cn/home-index"
        node = Node.objects.create(name=n.name, info=n.id, url=url)
        # dot.node(n.id, n.name)
        n_dict[n.id] = node
    for n in st.nodes.values():
        for t in n.teacher:
            # dot.edge(t, n.id)
            Edge.objects.create(source=n_dict[t], target=n_dict[n.id])
    # 使用 values() 方法将 QuerySet 转换为字典列表
    nodes_list = list(nodes.values('id', 'name', 'info', 'url'))
    edges_list = list(edges.values('id', 'source_id', 'target_id'))

    return render(request, 'graph.html', {'nodes': json.dumps(nodes_list), 'edges': json.dumps(edges_list)})

    # pic_nodes = []
    # pic_edges = []
    # dot = graphviz.Digraph(comment='有向图')
    # # 只考虑teacher里面的数据
    # for n in st.nodes.values():
    #     # pic_nodes.append(n.id)
    #     dot.node(n.id, n.name)
    # for n in st.nodes.values():
    #     for t in n.teacher:
    #         dot.edge(t, n.id)
    # dot.render('E:\\project\\SE_project\\academic_tree\\static\\view\\tmp', format='jpg', view=True)
    # return render(request,'view.html')

def delete(request):
    if request.method == 'POST':
        phone1 = request.POST.get('phone1')
        phone2 = request.POST.get('phone2')
        user = request.user
        phone_number = user.userprofile.phone_number
        st = main.login(phone_number, phone_number)
        st.nodes[phone1].drop(phone1, phone2, phone_number)
        st.nodes[phone2].drop(phone1, phone2, phone_number)
    return render(request,'delete.html')
def adjust(request):
    if request.method == 'POST':

        selected_option = request.POST.get('options')
        user = request.user
        phone_number = user.userprofile.phone_number
        st = main.login(phone_number, phone_number)
        if selected_option == 'option1':
            return redirect('mentorship:name_a')
        if selected_option == 'option2':
            return redirect('mentorship:url_a')
        if selected_option == 'option3':
            return redirect('mentorship:time_a')
    return render(request, 'adjust.html')
def name_a(request):
    if request.method=='POST':
        name =request.POST.get('name')
        phone = request.POST.get('phone')
        user = request.user
        phone_number = user.userprofile.phone_number
        st = main.login(phone_number, phone_number)
        st.nodes[phone].modify(item='name', value=name)
    return render(request,'name_a.html')
def url_a(request):
    if request.method=='POST':
        phone = request.POST.get('phone')
        url = request.POST.get('url')
        user = request.user
        phone_number = user.userprofile.phone_number
        st = main.login(phone_number, phone_number)
        st.nodes[phone].modify(item='page', value=url)
    return render(request,'url_a.html')
def time_a(request):
    if request.method=='POST':
        phone1 = request.POST.get('phone1')
        phone2 = request.POST.get('phone2')
        time = request.POST.get('time')
        user = request.user
        phone_number = user.userprofile.phone_number
        st = main.login(phone_number, phone_number)
        st.nodes[phone1].modify(item='time', value=time, id_t=phone1, id_s=phone2)
        st.nodes[phone2].modify(item='time', value=time, id_t=phone1, id_s=phone2)

    return render(request,'time_a.html')
def review(request):
    user = request.user
    phone_number = user.userprofile.phone_number
    st = main.login(phone_number, phone_number)
    merge = st.cursor.toMerge

    merge_dict = {i: item for i, item in enumerate(merge)}

    if request.method == 'POST':
        selected_parameters = request.POST.getlist('parameters')
        # 处理选中的参数，可能保存到数据库或执行其他操作
        selected_items = [merge_dict[int(key)] for key in selected_parameters]
        for s in selected_items:
            # 这个1是作为字符串的
            st.cursor.merge_mani(s[0])
    context = {'dict': merge_dict}
    return render(request, 'review.html', context)
def total(request):
    if request.method == 'POST':
        phone=request.POST.get('phone')
        st = main.lookup(phone)
        # 删除所有 Node 记录
        Node.objects.all().delete()
        # 删除所有 Edge 记录
        Edge.objects.all().delete()

        nodes = Node.objects.all()
        edges = Edge.objects.all()

        n_dict = {}
        for n in st.nodes.values():
            # pic_nodes.append(n.id)
            # return HttpResponse(f"{n.id} + {n.page}")
            url = n.page
            if (url is None):
                url = "https://homepage.hit.edu.cn/home-index"
            node = Node.objects.create(name=n.name, info=n.id, url=url)
            # dot.node(n.id, n.name)
            n_dict[n.id] = node
        for n in st.nodes.values():
            for t in n.teacher:
                # dot.edge(t, n.id)
                Edge.objects.create(source=n_dict[t], target=n_dict[n.id])
        # 使用 values() 方法将 QuerySet 转换为字典列表
        nodes_list = list(nodes.values('id', 'name', 'info', 'url'))
        edges_list = list(edges.values('id', 'source_id', 'target_id'))
        # pic_nodes = []
        # pic_edges = []
        # dot = graphviz.Digraph(comment='有向图')
        # # 只考虑teacher里面的数据
        # for n in st.nodes.values():
        #     # pic_nodes.append(n.id)
        #     dot.node(n.id, n.name)
        # for n in st.nodes.values():
        #     for t in n.teacher:
        #         dot.edge(t, n.id)
        # dot.render('E:\\project\\SE_project\\academic_tree\\static\\view\\tmp', format='jpg', view=True)
        return redirect('mentorship:total_view')

    return render(request,'total.html')
def total_view(request):
    # return render(request,'total_view.html')
    nodes = Node.objects.all()
    edges = Edge.objects.all()
    nodes_list = list(nodes.values('id', 'name', 'info', 'url'))
    edges_list = list(edges.values('id', 'source_id', 'target_id'))
    return render(request, 'graph.html', {'nodes': json.dumps(nodes_list), 'edges': json.dumps(edges_list)})


from .models import Node, Edge

# def graph_view(request):
#     # 删除所有 Node 记录
#     Node.objects.all().delete()
#     # 删除所有 Edge 记录
#     Edge.objects.all().delete()
#
#     nodes = Node.objects.all()
#     edges = Edge.objects.all()
#
#
#
#     # 使用 values() 方法将 QuerySet 转换为字典列表
#     nodes_list = list(nodes.values('id', 'name', 'info', 'url'))
#     edges_list = list(edges.values('id', 'source_id', 'target_id'))
#
#     return render(request, 'graph.html', {'nodes': json.dumps(nodes_list), 'edges': json.dumps(edges_list)})


