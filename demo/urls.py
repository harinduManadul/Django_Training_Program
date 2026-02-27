"""
URL configuration for demo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from users.api import app
from devices.api import app as device_app
from telemerty.api import app as telemetry_app

urlpatterns = [
    path('admin/', admin.site.urls),
    path('useapi/', app.urls),
    path('deviceapi/', device_app.urls),
    path('telemetryapi/', telemetry_app.urls)
]
