
"""
URL configuration for stegano_project project.

The urlpatterns list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from stegano_app import views
from stegano_app.views import steganalysis_view



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index,name='index'),
    path('encryption/', views.encryption_view,name='encryption'),
    path('decryption/', views.decryption_view,name='decryption'),
    path('steganalyze/', steganalysis_view, name='steganalysis'),
    path('estimate', views.estimate_capacity_view, name='estimate_capacity'),
    
] 