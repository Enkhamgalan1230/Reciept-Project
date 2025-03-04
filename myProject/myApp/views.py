from django.shortcuts import render

def home(request):
    context ={}
    return render(request, "myApp/home.html", context)
