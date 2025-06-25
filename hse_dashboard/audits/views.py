# audits/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse # HttpResponse is now unused, can be removed
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required

import datetime
import traceback # <--- Ensure this is imported for error logging


from .forms import (
    AuditForm, ChemicalAuditForm, BiannualAuditForm, MonthlyAuditForm, HazardousWasteForm,
    CustomUserCreationForm, CustomUserChangeForm
)
from .models import Audit # Only import the single Audit model
from django.contrib.auth.models import User, Group

AUDIT_TYPE_FORMS = {
    'monthly': MonthlyAuditForm,
    'biannual': BiannualAuditForm,
    'hazardous': HazardousWasteForm,
    'chemical_waste': ChemicalAuditForm,
}


def login_page(request):
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # This is a traditional form submission, so redirect is fine here.
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home(request):
    user_creation_form_instance = CustomUserCreationForm() # Store in a variable to inspect
    print("\n--- DEBUGGING HOME VIEW ---")
    print(f"Fields available in CustomUserCreationForm instance: {list(user_creation_form_instance.fields.keys())}")
    print("--- END DEBUGGING HOME VIEW ---")

    context = {
        "chemical_form": ChemicalAuditForm(),
        "monthly_form": MonthlyAuditForm(),
        "biannual_form": BiannualAuditForm(),
        "hazardous_form": HazardousWasteForm(),
        "audits": Audit.objects.all(), # This is for initial page load of list
        "user_creation_form": CustomUserCreationForm(),
    }
    return render(request, "home.html", context)

@login_required
def create_chemical_audit(request):
    if request.method == "POST":
        form = ChemicalAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False) # Get the instance, don't save to DB yet
            # Make sure audit.user = request.user is uncommented if you have a User ForeignKey
            # audit.user = request.user
            audit.audit_type = 'chemical_waste' # Set the audit_type
            audit.save() # <-- CORRECT: Save the instance now
            return JsonResponse({'status': 'success', 'message': 'Chemical Audit created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def create_monthly_audit(request):
    if request.method == "POST":
        form = MonthlyAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            # audit.user = request.user
            audit.audit_type = 'monthly'
            audit.save() # <-- CORRECT: Save the instance now (was 'form.save()')
            return JsonResponse({'status': 'success', 'message': 'Monthly Audit created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def create_biannual_audit(request):
    if request.method == "POST":
        form = BiannualAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            # audit.user = request.user
            audit.audit_type = 'biannual'
            audit.save() # <-- CORRECT: Save the instance now (was 'form.save()')
            return JsonResponse({'status': 'success', 'message': 'Biannual Audit created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def create_hazardous_audit(request):
    if request.method == "POST":
        form = HazardousWasteForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            # audit.user = request.user
            audit.audit_type = 'hazardous'
            audit.save() # <-- CORRECT: Save the instance now (was 'form.save()')
            return JsonResponse({'status': 'success', 'message': 'Hazardous Waste Audit created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def get_audit_data(request, audit_id):
    try:
        audit = get_object_or_404(Audit, id=audit_id)
        audit_type_str = audit.audit_type

        print(f"\n--- DEBUGGING GET_AUDIT_DATA FOR AUDIT ID: {audit_id} ---")
        print(f"1. Actual Audit Type from DB: '{audit_type_str}'")

        form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

        if not form_class:
            print(f"ERROR: No specific form found for audit type '{audit_type_str}'")
            return JsonResponse({"error": "No specific form found for this audit type", "audit_type": audit_type_str}, status=400)

        print(f"2. Resolved Form Class: {form_class.__name__}")

        form = form_class(instance=audit)

        # --- NEW DEBUGGING CODE HERE ---
        print("3a. Fields available in form.fields (from ModelForm.Meta.fields):")
        if not form.fields:
            print("    -> No fields found in this form instance!")
        for f_name in form.fields.keys():
            print(f"    - Found form field: '{f_name}'")
        # --- END NEW DEBUGGING CODE ---

        serialized_data = {}
        print("3b. Fields being processed for JSON serialization:")
        for field_name, form_field in form.fields.items():
            value = getattr(audit, field_name, None)

            # Your existing serialization logic
            if isinstance(value, datetime.date):
                serialized_data[field_name] = value.isoformat()
            elif isinstance(value, datetime.datetime):
                serialized_data[field_name] = value.isoformat()
            elif isinstance(value, (bool, int, float, str)):
                serialized_data[field_name] = value
            elif value is None:
                serialized_data[field_name] = None
            else:
                if hasattr(value, 'pk'):
                    serialized_data[field_name] = value.pk
                else:
                    serialized_data[field_name] = str(value)
            print(f"   - Field Name: '{field_name}', Value: '{serialized_data.get(field_name)}'")

        serialized_data['id'] = audit.id
        serialized_data['audit_type'] = audit_type_str
        if hasattr(audit, 'AuditID'):
            serialized_data['AuditID'] = audit.AuditID
        if hasattr(audit, 'date'):
             serialized_data['date'] = audit.date.isoformat() if isinstance(audit.date, datetime.date) else str(audit.date)

        print(f"4. Final JSON Data Sent to Frontend: {serialized_data}")
        print("--- END DEBUGGING GET_AUDIT_DATA ---")

        return JsonResponse(serialized_data)

    except Audit.DoesNotExist:
        print(f"ERROR: Audit with ID {audit_id} not found (404).")
        return JsonResponse({"error": "Audit not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        print(f"UNEXPECTED ERROR in get_audit_data for audit ID {audit_id}: {e}")
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


# === CORRECTED EDIT_AUDIT VIEW TO RETURN JSONRESPONSE ===
@login_required
def edit_audit(request, audit_id):
    audit = get_object_or_404(Audit, id=audit_id)
    audit_type_str = audit.audit_type

    form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

    if not form_class:
        # If form class not found, return JSON error
        return JsonResponse({"status": "error", "message": "No specific form found for this audit type"}, status=400)

    if request.method == 'POST':
        form = form_class(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            # On successful save, return JSON success
            return JsonResponse({'status': 'success', 'message': 'Audit updated successfully'})
        else:
            # On invalid form, return JSON errors
            print(form.errors) # For server-side debugging
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    # If not a POST request, return an appropriate JSON error
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# === EXISTING GET_ALL_AUDITS VIEW (Already returns JSON) ===
@login_required
def get_all_audits(request):
    try:
        all_audits = Audit.objects.all().order_by('-date', '-id')
        serialized_audits = []
        for audit in all_audits:
            serialized_audits.append({
                'id': audit.id,
                'AuditID': audit.AuditID,
                'audit_type': audit.audit_type,
                'date': audit.date.isoformat(),
            })
        return JsonResponse(serialized_audits, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve audit list: {str(e)}"}, status=500)

# === EXISTING DELETE_AUDIT VIEW (Already returns JSON) ===
@login_required
def delete_audit(request, audit_id):
    if request.method == 'POST':
        try:
            audit = get_object_or_404(Audit, id=audit_id)
            audit.delete()
            return JsonResponse({'status': 'success', 'message': 'Audit deleted successfully'})
        except Audit.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Audit not found'}, status=404)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# NEW: Create User View
@login_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save() # CustomUserCreationForm save method handles user and groups
            return JsonResponse({'status': 'success', 'message': f'User {user.username} created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid user data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# NEW: Get All Users View (for list display)
@login_required
def get_all_users(request):
    try:
        all_users = User.objects.all().order_by('username').prefetch_related('groups')
        serialized_users = []
        for user in all_users:
            group_names = [group.name for group in user.groups.all()]
            serialized_users.append({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_staff': user.is_staff,
                'is_active': user.is_active,
                'date_joined': user.date_joined.isoformat(),
                'groups': group_names, # List of group names (e.g., ['Administrator', 'Regular'])
            })
        return JsonResponse(serialized_users, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve user list: {str(e)}"}, status=500)

# NEW: Get Single User Data View (for edit/delete confirmation)
@login_required
def get_user_data(request, user_id):
    try:
        user = get_object_or_404(User, id=user_id)
        group_names = [group.name for group in user.groups.all()]
        
        serialized_data = {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_staff': user.is_staff,
            'is_active': user.is_active,
            'date_joined': user.date_joined.isoformat(),
            'groups': group_names, # List of group names
            'selected_group_ids': [group.id for group in user.groups.all()] # For setting initial selection in form
        }
        return JsonResponse(serialized_data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

# NEW: Edit User View
@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        # Pass the User instance to the form
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save() # This form's save method handles user and group updates
            return JsonResponse({'status': 'success', 'message': f'User {user.username} updated successfully'})
        else:
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'Invalid user data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# NEW: Delete User View
@login_required
def delete_user(request, user_id):
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            user.delete() # Deleting the User object will handle group relationships
            return JsonResponse({'status': 'success', 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def get_all_groups(request):
    """
    Returns a JSON list of all available Django Groups.
    """
    try:
        groups = Group.objects.all().order_by('name')
        serialized_groups = [{'id': group.id, 'name': group.name} for group in groups]
        return JsonResponse(serialized_groups, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve groups: {str(e)}"}, status=500)

