from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_deny

@xframe_options_deny
def bass(request):
    return render(request, "bass.html")