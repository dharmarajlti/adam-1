from django.urls import path
from .views import AddressViewSet, AddressDetailsView
from . import views
from  django.views.generic import TemplateView

urlpatterns = [
    path('address-add/', AddressViewSet.as_view()),
    path('address-list/', AddressDetailsView.as_view()),
    # path('create_address/', TemplateView.as_view(template_name="adam/create_address.html")),
    # path('view_address/', TemplateView.as_view(template_name="adam/view_address.html"))
    path('create_address/', views.create_address_view),
    path('view_address/', views.view_address),
    path('find_address/', views.find_address),
    path('add_address/', views.create_address),
    path('check_area/', views.check_area),
    path('view_data/', views.view_data)
]
