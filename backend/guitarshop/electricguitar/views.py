from django.shortcuts import render
from django.views.decorators.clickjacking import xframe_options_deny

@xframe_options_deny
def electric(request):
    return render(request, "electric.html")
