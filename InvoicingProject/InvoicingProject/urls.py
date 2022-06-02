"""InvoicingProject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.contrib.auth import views as auth_views
from django.urls import path
from django.conf.urls import include,url
#add routes to other projects here. Route actual views in their respective projects.

urlpatterns = [
    path('admin/', admin.site.urls),
	url(r'', include('InvoicingWeb.urls')),
	path('accounts/login/',auth_views.LoginView.as_view()),
	path('password-reset/', auth_views.PasswordChangeView.as_view())
]