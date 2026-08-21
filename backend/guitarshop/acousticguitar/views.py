from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_deny

@xframe_options_deny
def acoustic(request):
    return render(request, "acoustic.html")