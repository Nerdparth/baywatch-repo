from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from dashboard.models import Student, School
from django.contrib import messages


def signup_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        email = request.POST["email"]
        confirm_password = request.POST["confirm_password"]
        school_id = int(request.POST["school_id"])
        if User.objects.filter(username=username).exists():
            messages.error(request, "username already exists")
            return redirect("register")
        if password != confirm_password:
            messages.error(request, "passwords donot match")
            return redirect("register")
        school = School.objects.get(id=school_id)
        student = User.objects.create(username=username, email=email)
        student.set_password(password)
        student.save()
        Student.objects.create(school=school, student=student)
        login(request, student)
        messages.success(request, "Signed up Successfully")
        return redirect("dashboard")
    schools = list(School.objects.values("id", "name"))
    return render(request, "signup.html", {"schools": schools})


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "logged in successfully")
            return redirect("dashboard")
        else:
            messages.error(request, "invalid credentials")
            return redirect("dashboard")
    return render(request, "login.html")


def logout_view(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        logout(request)
        messages.success(request, "Logged out successfully")
    return redirect("login")
