from django.shortcuts import render
from .models import NodeForm


def get_node_data(node_id):
    class Node:
        def __int__(self):
            self.nodeid = 'xc'
            self.teachers = ['lx', 'yl']
            self.students = ['ygn']
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
