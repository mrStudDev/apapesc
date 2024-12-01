from django.shortcuts import render

# Create your views here.

def HomeView(request):
    return render(request, 'app_home/home.html')