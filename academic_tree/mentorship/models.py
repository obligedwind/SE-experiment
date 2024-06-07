from django import forms


class NodeForm(forms.Form):
    node_id = forms.CharField(label='Node ID')