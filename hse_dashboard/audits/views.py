# audits/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
# Import user_passes_test for role-based access control
# login_required is still used for CRUD operations, but NOT for the home view
from django.contrib.auth.decorators import login_required, user_passes_test
import datetime
import traceback
from django.db.models import Avg, Sum
from django.utils import timezone

from django.contrib.auth.models import User, Group
from .forms import (
    AuditForm, ChemicalAuditForm, BiannualAuditForm, MonthlyAuditForm, HazardousWasteForm,
    AnnualEnvironmentalRefresherForm, HSEInductionForm,
    CustomUserCreationForm, CustomUserChangeForm, EnvironmentalIncidentForm
)
from .models import Audit

AUDIT_TYPE_FORMS = {
    'monthly': MonthlyAuditForm,
    'biannual': BiannualAuditForm,
    'hazardous': HazardousWasteForm,
    'chemical_waste': ChemicalAuditForm,
    'annual_refresher': AnnualEnvironmentalRefresherForm,
    'hse_induction': HSEInductionForm,
    'environmental_incidents': EnvironmentalIncidentForm,

}

LOCATION_CHOICES = (
    ('', 'Select Location'),
    ('KBD Fisheries Lab', 'KBD Fisheries Lab'),
    ('KBD Algae Lab', 'KBD Algae Lab'),
    ('KBD Aquaculture Lab', 'KBD Aquaculture Lab'),
    ('KBD Algae Facility Laboratory', 'KBD Algae Facility Laboratory'),
    ('Duba Lab', 'Duba Lab'),
    ('Jizan Lab', 'Jizan Lab'),
    ('Jubail Lab', 'Jubail Lab'),
    ('Al Raes Sea Cage Farms', 'Al Raes Sea Cage Farms'),
    ('Algae Facility Phase 2', 'Algae Facility Phase 2'),
)


MONTHLY_METRIC_FIELDS = [
    'fire_extinguishers_checked', 'emergency_exits_inspected', 'first_aid_kits_checked',
    'spill_kits_stocked', 'ppe_stocked', 'lab_coats_clean', 'biohazard_waste_reviewed',
    'chemical_waste_reviewed', 'glass_sharp_waste_reviewed', 'lab_surfaces_clean',
    'balances_calibrated_cleaned', 'microscopes_calibrated_cleaned', 'freezers_functional_clean',
    'secondary_containment_ok', 'evidence_of_spills_or_expired_stock', 'chemicals_stored_labelled',
    'safety_data_sheets_available', 'chemicals_in_inventory', 'chemical_containers_closed_and_disposed',
    'spill_kit_accessible', 'bio_sample_temp_maintained', 'lab_consumables_stock_ok'
]
TOTAL_MONTHLY_METRICS = len(MONTHLY_METRIC_FIELDS)

BIANNUAL_CHART_LOCATIONS = [
    'Al Raes Sea Cage Farms',
    'KBD Fisheries Lab',
    'KBD Algae Lab',
    'KBD Aquaculture Lab',
    'KBD Algae Facility Laboratory',
]

def login_page(request):
    """
    Handles user login.
    """
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            # Redirect to the main home page after successful login
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def is_administrator(user):
    """
    Checks if the given user belongs to the 'Administrator' group OR is a superuser.
    """
    # Guests will not be authenticated, so request.user.is_authenticated will be False
    # and is_superuser will be False. Their group check will also fail.
    # This function is used by @user_passes_test decorators to protect backend views.
    return user.is_authenticated and (user.is_superuser or user.groups.filter(name='Administrator').exists())

def home(request):
    """
    Renders the main dashboard page. Accessible to both authenticated and unauthenticated users.
    Passes authentication status and administrator status to the template for UI control.
    """
    user_creation_form_instance = CustomUserCreationForm()
    
    # Check if the user is authenticated
    is_authenticated_user = request.user.is_authenticated

    # Check for administrator status only if authenticated
    is_admin = False
    if is_authenticated_user:
        is_admin = is_administrator(request.user)

    context = {
        "chemical_form": ChemicalAuditForm(),
        "monthly_form": MonthlyAuditForm(),
        "biannual_form": BiannualAuditForm(),
        "hazardous_form": HazardousWasteForm(),
        "annual_refresher_form": AnnualEnvironmentalRefresherForm(),
        "hse_induction_form": HSEInductionForm(),
        "environmental_incident_form": EnvironmentalIncidentForm(),
        "audits": Audit.objects.all() if is_authenticated_user else [], 
        "user_creation_form": user_creation_form_instance,
        "is_administrator": is_admin,
        "is_authenticated": is_authenticated_user, 
    }
    return render(request, "home.html", context)


# --- Create Audit Views (Require login) ---
@login_required # Retain login_required for backend security
def create_chemical_audit(request):
    """
    Handles creation of Chemical Waste audits.
    """
    if request.method == "POST":
        form = ChemicalAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'chemical_waste'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Hazardous Waste Log created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Retain login_required for backend security
def create_monthly_audit(request):
    """
    Handles creation of Monthly Inspection audits and calculates score.
    """
    if request.method == "POST":
        form = MonthlyAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'monthly'

            true_count = 0
            for field_name in MONTHLY_METRIC_FIELDS:
                if form.cleaned_data.get(field_name, False):
                    true_count += 1
            
            if TOTAL_MONTHLY_METRICS > 0:
                audit.score = (true_count / TOTAL_MONTHLY_METRICS) * 100
            else:
                audit.score = 0.0 # Handle case where no metrics are defined

            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Monthly Inspection created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Retain login_required for backend security
def create_biannual_audit(request):
    """
    Handles creation of Biannual Environment audits.
    """
    if request.method == "POST":
        form = BiannualAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'biannual'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Biannual Environment Audit created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Retain login_required for backend security
def create_hazardous_audit(request):
    """
    Handles creation of Hazardous Waste Inspection audits.
    """
    if request.method == "POST":
        form = HazardousWasteForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'hazardous'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Hazardous Waste Inspection created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required # Retain login_required for backend security
def create_annual_refresher_audit(request):
    """
    Handles creation of Annual Environmental Refresher audits.
    Allows only one instance to exist at a time.
    """
    if request.method == "POST":
        # Check if an instance already exists to enforce single entry
        existing_audit = Audit.objects.filter(audit_type='annual_refresher').first()
        if existing_audit:
            return JsonResponse({
                'status': 'error',
                'message': 'To change Annual Environmental Refresher data, please edit the existing audit.'
            }, status=400)

        form = AnnualEnvironmentalRefresherForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'annual_refresher'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Annual Environmental Refresher created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Retain login_required for backend security
def create_hse_induction_audit(request):
    """
    Handles creation of HSE Induction audits.
    Allows only one instance to exist at a time.
    """
    if request.method == "POST":
        # Check if an instance already exists to enforce single entry
        existing_audit = Audit.objects.filter(audit_type='hse_induction').first()
        if existing_audit:
            return JsonResponse({
                'status': 'error',
                'message': 'To change HSE Induction data, please edit the existing audit.'
            }, status=400)

        form = HSEInductionForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'hse_induction'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'HSE Induction created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

def create_environmental_incident_audit(request):
    """
    Handles creation of Environmental Incidents audits.
    """
    if request.method == "POST":
        form = EnvironmentalIncidentForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'environmental_incidents'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Environmental Incidents audit created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# --- Audit Get/Edit/Delete Views (Require login) ---
@login_required # Retain login_required for backend security
def get_audit_data(request, audit_id):
    """
    Retrieves and serializes data for a specific audit.
    Includes type-specific fields.
    """
    try:
        audit = get_object_or_404(Audit, id=audit_id)
        audit_type_str = audit.audit_type
        form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

        if not form_class:
            return JsonResponse({"error": "No specific form found for this audit type", "audit_type": audit_type_str}, status=400)

        form = form_class(instance=audit)
        serialized_data = {}
        for field_name, form_field in form.fields.items():
            value = getattr(audit, field_name, None)
            if isinstance(value, datetime.date):
                serialized_data[field_name] = value.isoformat()
            elif isinstance(value, datetime.datetime):
                serialized_data[field_name] = value.isoformat()
            elif isinstance(value, bool):
                serialized_data[field_name] = value
            elif isinstance(value, (int, float)):
                if field_name == 'score' and value is not None:
                    serialized_data[field_name] = f"{value:.2f}"
                else:
                    serialized_data[field_name] = value
            elif value is None:
                serialized_data[field_name] = None
            else:
                if hasattr(value, 'pk'): # For foreign key fields if any were added to forms
                    serialized_data[field_name] = value.pk
                else:
                    serialized_data[field_name] = str(value)
        
        serialized_data['id'] = audit.id
        serialized_data['audit_type'] = audit_type_str
        serialized_data['display_audit_type'] = audit.get_audit_type_display()
        
        # Ensure AuditID, date, location are always present if they exist
        if hasattr(audit, 'AuditID'):
            serialized_data['AuditID'] = audit.AuditID
        if hasattr(audit, 'date'):
             serialized_data['date'] = audit.date.isoformat() if isinstance(audit.date, datetime.date) else str(audit.date)
        if hasattr(audit, 'location'):
             serialized_data['location'] = audit.location
        
        # Include type-specific fields
        if audit_type_str == 'biannual':
            serialized_data['number_of_nonconformances'] = audit.number_of_nonconformances
            serialized_data['number_of_closeouts'] = audit.number_of_closeouts
        elif audit_type_str == 'annual_refresher':
            serialized_data['number_of_employees'] = audit.number_of_employees
            serialized_data['number_of_employees_trained'] = audit.number_of_employees_trained
        elif audit_type_str == 'hse_induction':
            serialized_data['number_of_inductions'] = audit.number_of_inductions
        elif audit_type_str == 'chemical_waste' or audit_type_str == 'hazardous': # Hazardous also uses these
            serialized_data['quantity_liters'] = audit.quantity_liters
            serialized_data['description'] = audit.description
        elif audit_type_str == 'environmental_incidents': # NEW: Environmental Incidents
            serialized_data['number_of_incidents'] = audit.number_of_incidents
            serialized_data['details'] = audit.details


        return JsonResponse(serialized_data)

    except Audit.DoesNotExist:
        return JsonResponse({"error": "Audit not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@login_required # Retain login_required for backend security
def edit_audit(request, audit_id):
    """
    Handles editing of an existing audit.
    Updates score for monthly audits.
    """
    audit = get_object_or_404(Audit, id=audit_id)
    audit_type_str = audit.audit_type

    form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

    if not form_class:
        return JsonResponse({"status": "error", "message": "No specific form found for this audit type"}, status=400)

    if request.method == 'POST':
        form = form_class(request.POST, instance=audit)
        if form.is_valid():
            audit_instance = form.save(commit=False)

            if audit_type_str == 'monthly':
                true_count = 0
                for field_name in MONTHLY_METRIC_FIELDS:
                    if form.cleaned_data.get(field_name, False):
                        true_count += 1
                
                if TOTAL_MONTHLY_METRICS > 0:
                    audit_instance.score = (true_count / TOTAL_MONTHLY_METRICS) * 100
                else:
                    audit_instance.score = 0.0
            
            audit_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Audit updated successfully'})
        else:
            print(form.errors) # Log errors for debugging
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@login_required # Retain login_required for backend security
def get_all_audits(request):
    """
    Retrieves a list of all audits with key details.
    """
    try:
        all_audits = Audit.objects.all().order_by('-date', '-id')
        serialized_audits = []
        for audit in all_audits:
            audit_data = {
                'id': audit.id,
                'AuditID': audit.AuditID,
                'audit_type': audit.audit_type,
                'display_audit_type': audit.get_audit_type_display(),
                'date': audit.date.isoformat(),
                'score': f"{audit.score:.2f}" if audit.score is not None else None
            }
            # Include specific fields for different audit types for display in list
            if audit.audit_type == 'monthly':
                audit_data['score'] = f"{audit.score:.2f}" if audit.score is not None else None
            elif audit.audit_type == 'biannual':
                audit_data['number_of_nonconformances'] = audit.number_of_nonconformances
                audit_data['number_of_closeouts'] = audit.number_of_closeouts
            elif audit.audit_type == 'annual_refresher':
                audit_data['number_of_employees'] = audit.number_of_employees
                audit_data['number_of_employees_trained'] = audit.number_of_employees_trained
            elif audit.audit_type == 'hse_induction':
                audit_data['number_of_inductions'] = audit.number_of_inductions
            elif audit.audit_type == 'chemical_waste' or audit.audit_type == 'hazardous':
                audit_data['quantity_liters'] = audit.quantity_liters
                audit_data['description'] = audit.description
            elif audit.audit_type == 'environmental_incidents': # NEW: Environmental Incidents
                audit_data['number_of_incidents'] = audit.number_of_incidents
                audit_data['details'] = audit.details
            
            serialized_audits.append(audit_data)
        return JsonResponse(serialized_audits, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve audit list: {str(e)}"}, status=500)

@login_required # Retain login_required for backend security
def delete_audit(request, audit_id):
    """
    Handles deletion of an audit.
    """
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

# --- User Management Views (Restricted to Administrators/Superusers via @user_passes_test) ---
@login_required # Requires login
@user_passes_test(is_administrator, login_url='/accounts/login/') # Requires admin role; uses default login_url
def create_user(request):
    """
    Handles creation of new users. Restricted to Administrators.
    """
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return JsonResponse({'status': 'success', 'message': f'User {user.username} created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid user data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Requires login to get user data (even just for list display)
def get_all_users(request):
    """
    Retrieves a list of all users.
    """
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
                'groups': group_names,
            })
        return JsonResponse(serialized_users, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve user list: {str(e)}"}, status=500)

@login_required # Requires login to get user data
def get_user_data(request, user_id):
    """
    Retrieves and serializes data for a specific user.
    """
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
            'groups': group_names,
            'selected_group_ids': [group.id for group in user.groups.all()]
        }
        return JsonResponse(serialized_data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

@login_required # Requires login
@user_passes_test(is_administrator, login_url='/accounts/login/') # Requires admin role; uses default login_url
def edit_user(request, user_id):
    """
    Handles editing of existing users. Restricted to Administrators.
    """
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': f'User {user.username} updated successfully'})
        else:
            print(form.errors) # Log errors for debugging
            return JsonResponse({'status': 'error', 'message': 'Invalid user data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Requires login
@user_passes_test(is_administrator, login_url='/accounts/login/') # Requires admin role; uses default login_url
def delete_user(request, user_id):
    """
    Handles deletion of users. Restricted to Administrators.
    """
    if request.method == 'POST':
        try:
            user = get_object_or_404(User, id=user_id)
            user.delete()
            return JsonResponse({'status': 'success', 'message': 'User deleted successfully'})
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'User not found'}, status=404)
        except Exception as e:
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': f'An unexpected error occurred: {str(e)}'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required # Can be accessed by any logged-in user to get group options for user editing
def get_all_groups(request):
    """
    Retrieves a list of all user groups.
    """
    try:
        groups = Group.objects.all().order_by('name')
        serialized_groups = [{'id': group.id, 'name': group.name} for group in groups]
        return JsonResponse(serialized_groups, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve groups: {str(e)}"}, status=500)

# --- Chart data endpoints (No login_required, accessible to all, including guests) ---
# Removed @login_required decorators from chart data views to allow guest access
def get_monthly_inspection_scores(request):
    """
    Provides data for the Monthly Inspection Scores chart.
    """
    try:
        departments_data = Audit.LOCATION_CHOICES 
        current_month_scores = []
        last_year_average_scores = []
        
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        one_year_ago = now - datetime.timedelta(days=365) # Calculate one year ago from current date
        
        current_month_name = now.strftime("%B")

        for dept_key, dept_name in departments_data:
            current_month_audit = Audit.objects.filter(
                audit_type='monthly',
                location=dept_key,
                date__year=current_year,
                date__month=current_month
            ).order_by('-date').first()

            if current_month_audit and current_month_audit.score is not None:
                current_month_scores.append(round(current_month_audit.score, 2))
            else:
                current_month_scores.append(None) # No score for current month in this department

            last_year_audits = Audit.objects.filter(
                audit_type='monthly',
                location=dept_key,
                date__gte=one_year_ago,
                date__lte=now
            )
            
            avg_score = last_year_audits.aggregate(Avg('score'))['score__avg']
            if avg_score is not None:
                last_year_average_scores.append(round(avg_score, 2))
            else:
                last_year_average_scores.append(None) # No average for last year in this department

        chart_data = {
            'labels': [choice[1] for choice in departments_data], # Use display names for labels
            'currentMonthScores': current_month_scores,
            'lastYearAverageScores': last_year_average_scores,
            'currentMonthName': current_month_name,
            'target': 100 # Target score for the chart
        }
        return JsonResponse(chart_data)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve monthly inspection scores: {str(e)}"}, status=500)


def get_biannual_ncr_chart_data(request):
    """
    Provides data for the Biannual NCR Chart.
    """
    try:
        chart_locations = [
            'Al Raes Sea Cage Farms',
            'KBD Fisheries Lab',
            'KBD Algae Lab',
            'KBD Aquaculture Lab',
            'KBD Algae Facility Laboratory',
        ]
        
        labels = []
        total_ncrs_data = []
        open_ncrs_data = []

        for location_name in chart_locations:
            location_audits = Audit.objects.filter(
                audit_type='biannual',
                location=location_name
            )
            
            total_ncrs_sum = location_audits.aggregate(Sum('number_of_nonconformances'))['number_of_nonconformances__sum'] or 0
            total_ncr_closeouts_sum = location_audits.aggregate(Sum('number_of_closeouts'))['number_of_closeouts__sum'] or 0
            
            open_ncrs_sum = total_ncrs_sum - total_ncr_closeouts_sum
            
            labels.append(location_name)
            total_ncrs_data.append(total_ncrs_sum)
            open_ncrs_data.append(max(0, open_ncrs_sum)) # Ensure open NCRs is not negative

        chart_data = {
            'labels': labels,
            'totalNCRs': total_ncrs_data,
            'openNCRs': open_ncrs_data,
        }
        return JsonResponse(chart_data)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve biannual NCR chart data: {str(e)}"}, status=500)


def get_hse_induction_completion(request):
    """
    Provides data for the HSE Induction Completion indicator.
    """
    try:
        hse_induction_audit = Audit.objects.filter(audit_type='hse_induction').order_by('-date').first()
        annual_refresher_audit = Audit.objects.filter(audit_type='annual_refresher').order_by('-date').first()

        inductions_completed = hse_induction_audit.number_of_inductions if hse_induction_audit else 0
        
        # Use number_of_employees from annual_refresher if available, otherwise default
        total_employees = annual_refresher_audit.number_of_employees if annual_refresher_audit and annual_refresher_audit.number_of_employees is not None else 220

        completion_percentage = 0
        if total_employees > 0:
            completion_percentage = (inductions_completed / total_employees) * 100
        
        return JsonResponse({
            'percentage': round(completion_percentage, 2),
            'inductions_completed': inductions_completed,
            'total_employees': total_employees
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve HSE Induction completion data: {str(e)}"}, status=500)


def get_annual_refresher_completion(request):
    """
    Provides data for the Annual Environmental Refresher Completion indicator.
    """
    try:
        annual_refresher_audit = Audit.objects.filter(audit_type='annual_refresher').order_by('-date').first()

        employees_trained = annual_refresher_audit.number_of_employees_trained if annual_refresher_audit else 0
        total_employees = annual_refresher_audit.number_of_employees if annual_refresher_audit and annual_refresher_audit.number_of_employees is not None else 220 # Default as per model

        completion_percentage = 0
        if total_employees > 0:
            completion_percentage = (employees_trained / total_employees) * 100
        
        return JsonResponse({
            'percentage': round(completion_percentage, 2),
            'employees_trained': employees_trained,
            'total_employees': total_employees
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve Annual Refresher completion data: {str(e)}"}, status=500)


def get_waste_quantity_per_lab(request):
    """
    Provides data for the Waste Quantity per Lab chart for the current month.
    """
    try:
        now = timezone.now()
        current_month = now.month
        current_year = now.year

        # Aggregate waste quantity by location for the current month
        waste_data = Audit.objects.filter(
            audit_type='chemical_waste',
            date__year=current_year,
            date__month=current_month
        ).values('location').annotate(total_quantity=Sum('quantity_liters')).order_by('location')

        labels = []
        quantities = []
        
        # Get all possible locations from LOCATION_CHOICES to ensure all labs are represented
        all_locations = [choice[0] for choice in Audit.LOCATION_CHOICES]
        location_map = {item['location']: item['total_quantity'] for item in waste_data}

        for location_key in all_locations:
            # Use the display name for the label and fetch quantity, defaulting to 0.0 if not found
            labels.append(dict(Audit.LOCATION_CHOICES).get(location_key, location_key))
            quantities.append(location_map.get(location_key, 0.0))

        chart_data = {
            'labels': labels,
            'quantities': quantities,
            'month': now.strftime("%B %Y")
        }
        return JsonResponse(chart_data)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve waste quantity per lab data: {str(e)}"}, status=500)
    


def get_environmental_incidents_data(request):
    """
    Provides data for the Environmental Incidents indicator,
    including incidents in the past month and total incidents,
    with an optional location filter.
    """
    try:
        location_filter = request.GET.get('location', '')
        
        # Get current date and one month ago
        now = timezone.now()
        one_month_ago = now - datetime.timedelta(days=30)

        # Base query for environmental incidents
        incidents_query = Audit.objects.filter(audit_type='environmental_incidents')

        # Apply location filter if provided
        if location_filter and location_filter != '':
            incidents_query = incidents_query.filter(location=location_filter)

        # Incidents in the past month
        incidents_past_month = incidents_query.filter(
            date__gte=one_month_ago,
            date__lte=now
        ).aggregate(Sum('number_of_incidents'))['number_of_incidents__sum'] or 0

        # Total incidents (sum of all incidents regardless of date or filter)
        # Note: This 'total' is across the filtered set if location_filter is applied
        # If total across ALL locations is needed, a separate unfiltered query would be required.
        # For this requirement, "total number of incidents" implies within the filtered context if a filter is active.
        total_incidents = incidents_query.aggregate(Sum('number_of_incidents'))['number_of_incidents__sum'] or 0
        
        # Prepare location options for the dropdown
        # Include an "All Locations" option at the beginning
        location_options = [{'value': '', 'text': 'All Locations'}] + \
                           [{'value': choice[0], 'text': choice[1]} for choice in LOCATION_CHOICES]

        return JsonResponse({
            'incidents_past_month': incidents_past_month,
            'total_incidents': total_incidents,
            'location_options': location_options,
            'selected_location': location_filter,
        })
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve environmental incidents data: {str(e)}"}, status=500)

