"""wiley_calculator URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from . import views
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from calc import analysis


urlpatterns=[
  path('',views.index),
  path('home/', views.get_profile, name = 'home'),
  path('calculator/', views.calculator_view, name = 'calculator'),
  path('financial-analysis/', views.financial_analysis_view, name = 'financial_analysis'),
  path('financial-analysis/<str:key>/', views.financial_analysis_view, name = 'financial_analysis'),
  path('financial-analysis-report/', views.financial_analysis_report, name = 'financial_analysis_report'),
  path('financial-analysis-view-form/<str:key>/', views.financial_analysis_view_form, name = 'financial-analysis-view-form'),
  path('ajax/load-data/<str:key>/', views.load_data, name = 'ajax_load_data'),
  path('logout/',views.logout_view,name='logout'),
  path('profile/',views.get_profile,name='profile'),
  path('get_calculator_data/', views.get_calculator_data, name = 'get_calculator_data'),
  path('update_scenario_status/', views.update_scenario_status, name = 'update_scenario_status'),
]