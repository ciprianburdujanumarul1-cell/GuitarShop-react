from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .models import Userdetail

from django.views.decorators.clickjacking import xframe_options_deny



# Create your views here.
@xframe_options_deny
def home(request):
    return render(request, "index.html")
@xframe_options_deny
def s(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]
        country = request.POST["country"]
        city = request.POST["city"]
        address = request.POST["address"]
        postal_code = request.POST["postal_code"]

        # Check for existing user
        if User.objects.filter(email=email).exists():
            return render(request, "signin.html", {"error": "Email already registered"})
        if User.objects.filter(username=username).exists():
            return render(request, "signin.html", {"error": "Username already registered"})

        # Create the User
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        # Create the Userdetail linked to the user
        Userdetail.objects.create(
            user=user,  
            country=country,
            city=city,
            address=address,
            postal_code=postal_code
        )

        return redirect("login")

    return render(request, "signin.html")
# view pentru pagina login
@xframe_options_deny
def l(request):
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]

        try:
            # căutăm userul după email
            user_obj = User.objects.filter(email=email).first()
            if user_obj is None:
                # return error, e.g.:
                return render(request, 'login.html', {'error': 'Invalid email or password'})
            username = user_obj.username   # Django autentifică cu username
        except User.DoesNotExist:
            return render(request, "login.html", {"error": "Email or password incorrect"})

        # autentificăm cu username + password
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)  # logăm userul
            return redirect("home")
        else:
            return render(request, "login.html", {"error": "Email or password incorrect"})

    return render(request, "login.html")

def logout_view(request):
    logout(request)  # clears the session and logs out the user
    return redirect("login") 