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
    path('get-all-audits/', views.get_all_audits, name='get_all_audits'), # NEW
    path('delete-audit/<int:audit_id>/', views.delete_audit, name='delete_audit'),

    path('users/create/', views.create_user, name='create_user'),
    path('users/all/', views.get_all_users, name='get_all_users_list'),

    path('users/<int:user_id>/', views.get_user_data, name='get_user_data'),

    path('users/<int:user_id>/edit/', views.edit_user, name='edit_user'),
    path('users/<int:user_id>/delete/', views.delete_user, name='delete_user'),
    path('users/all_groups/', views.get_all_groups, name='get_all_groups'), # <--- Add this line


]