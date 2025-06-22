from django.urls import path, include
from . import views

#THIS IS A URL CONFIGURATION
urlpatterns = [
    path('login/', views.login_page, name='login'),  # Your custom view
    path('', views.home, name='home'),
    path("create_chemical_audit/", views.create_chemical_audit, name="create_chemical_audit"),
    path("create_monthly_audit/", views.create_monthly_audit, name="create_monthly_audit"),
    path("create_biannual_audit/", views.create_biannual_audit, name="create_biannual_audit"),
    path("create_hazardous_audit/", views.create_hazardous_audit, name="create_hazardous_audit"),

        # New for editing audits
    path('get-audit/<int:audit_id>/', views.get_audit_data, name='get_audit_data'),
    path('edit-audit/<int:audit_id>/', views.edit_audit, name='edit_audit'),

]