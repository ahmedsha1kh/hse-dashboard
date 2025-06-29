# audits/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # --- Authentication URLs ---
    path('login/', views.login_page, name='login'),
    path('', views.home, name='home'),

    # --- Audit Creation URLs (Require login) ---
    path("create_chemical_audit/", views.create_chemical_audit, name="create_chemical_audit"),
    path("create_monthly_audit/", views.create_monthly_audit, name="create_monthly_audit"),
    path("create_biannual_audit/", views.create_biannual_audit, name="create_biannual_audit"),
    path("create_hazardous_audit/", views.create_hazardous_audit, name="create_hazardous_audit"),
    path("create_annual_refresher_audit/", views.create_annual_refresher_audit, name="create_annual_refresher_audit"),
    path("create_hse_induction_audit/", views.create_hse_induction_audit, name="create_hse_induction_audit"),
    path("create_environmental_incident_audit/", views.create_environmental_incident_audit, name="create_environmental_incident_audit"), # NEW URL


    # --- Audit Management URLs (Require login) ---
    path('get-audit/<int:audit_id>/', views.get_audit_data, name='get_audit_data'),
    path('edit-audit/<int:audit_id>/', views.edit_audit, name='edit_audit'),
    path('get-all-audits/', views.get_all_audits, name='get_all_audits'),
    path('delete-audit/<int:audit_id>/', views.delete_audit, name='delete_audit'),

    # --- User Management URLs (Require login and administrator status) ---
    path('users/create/', views.create_user, name='create_user'),
    path('users/all/', views.get_all_users, name='get_all_users_list'),
    path('users/<int:user_id>/', views.get_user_data, name='get_user_data'),
    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/all_groups/', views.get_all_groups, name='get_all_groups'),

    # --- Chart Data Endpoints (Accessible to all, including guests) ---
    path('charts/monthly_inspection_scores/', views.get_monthly_inspection_scores, name='get_monthly_inspection_scores'),
    path('charts/biannual_ncr_data/', views.get_biannual_ncr_chart_data, name='get_biannual_ncr_chart_data'),
    path('charts/hse_induction_completion/', views.get_hse_induction_completion, name='get_hse_induction_completion'),
    path('charts/annual_refresher_completion/', views.get_annual_refresher_completion, name='get_annual_refresher_completion'),
    path('charts/waste_quantity_per_lab/', views.get_waste_quantity_per_lab, name='get_waste_quantity_per_lab'),
    path('charts/environmental_incidents_data/', views.get_environmental_incidents_data, name='get_environmental_incidents_data'), # NEW URL
    path('charts/total_waste_quantity_data/', views.get_total_waste_quantity_data, name='get_total_waste_quantity_data'), # NEW URL

]
