"""config URL Configuration

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
from django.urls import path, include
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from calc import views
from django_plotly_dash import DjangoDash
from django.views.generic import TemplateView
from calc import analysis

urlpatterns = [
    path('grappelli/', include('grappelli.urls')),  # grappelli URLS
    path('django_plotly_dash/', include('django_plotly_dash.urls')),
    path('admin/', admin.site.urls),
    path('', include('django.contrib.auth.urls')),
    path('', views.index),
    path('accounts/', include('allauth.urls')),
    path('calculator/',include("calc.urls")),
    path('analysis/',include("calc.urls")),
    url(r'^login/$', auth_views.LoginView.as_view(),name='login'),
    path('logout/', include("calc.urls")),
    path('profile/', include("calc.urls")),
    path('get_calculator_data/', include("calc.urls"), name='get_calculator_data'),
    path('', include("adam.urls")),
    path('api/', include("adam.urls"), name="address_api"),
    # path('create_address/', include("adam.urls"), name="create_address"),
    # path('view_address/', include("adam.urls"), name="view_address")
    path('update_scenario_status/', include("calc.urls"), name='update_scenario_status'),
    path('home/', views.page_index, name='home'),
    path('calculator/', views.calculator_view, name='calculator'),
    url(r'^login/$', auth_views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.get_profile, name='profile'),
    path('financial-analysis/', views.financial_analysis_view, name='financial_analysis'),
    path('financial-analysis/<str:key>/', views.financial_analysis_view, name='financial_analysis'),
    path('financial-analysis-report/', views.financial_analysis_report, name='financial_analysis_report'),
    path('financial-analysis-view-form/<str:key>/', views.financial_analysis_view_form,
         name='financial-analysis-view-form'),
    path('ajax/load-data/<str:key>/', views.load_data, name='ajax_load_data'),
    path('get_calculator_data/', views.get_calculator_data, name='get_calculator_data'),
    path('update_scenario_status/', views.update_scenario_status, name='update_scenario_status'),
    path('get_calculator_version/', views.get_calculator_version, name='get_calculator_version')
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
