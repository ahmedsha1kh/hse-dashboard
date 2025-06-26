# audits/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import datetime
import traceback
from django.db.models import Avg, Sum
from django.utils import timezone

from django.contrib.auth.models import User, Group
from .forms import (
    AuditForm, ChemicalAuditForm, BiannualAuditForm, MonthlyAuditForm, HazardousWasteForm,
    AnnualEnvironmentalRefresherForm, HSEInductionForm, # NEW IMPORTS
    CustomUserCreationForm, CustomUserChangeForm
)
from .models import Audit

AUDIT_TYPE_FORMS = {
    'monthly': MonthlyAuditForm,
    'biannual': BiannualAuditForm,
    'hazardous': HazardousWasteForm,
    'chemical_waste': ChemicalAuditForm,
    'annual_refresher': AnnualEnvironmentalRefresherForm, # NEW
    'hse_induction': HSEInductionForm,                   # NEW
}

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
    if request.method == "POST":
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

@login_required
def home(request):
    user_creation_form_instance = CustomUserCreationForm()
    print("\n--- DEBUGGING HOME VIEW ---")
    print(f"Fields available in CustomUserCreationForm instance: {list(user_creation_form_instance.fields.keys())}")
    print("--- END DEBUGGING HOME VIEW ---")

    context = {
        "chemical_form": ChemicalAuditForm(),
        "monthly_form": MonthlyAuditForm(),
        "biannual_form": BiannualAuditForm(),
        "hazardous_form": HazardousWasteForm(),
        "annual_refresher_form": AnnualEnvironmentalRefresherForm(), # NEW
        "hse_induction_form": HSEInductionForm(),                   # NEW
        "audits": Audit.objects.all(),
        "user_creation_form": user_creation_form_instance,
    }
    return render(request, "home.html", context)

# --- Existing Create Audit Views ---
@login_required
def create_chemical_audit(request):
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

@login_required
def create_monthly_audit(request):
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
                audit.score = 0.0

            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Monthly Inspection created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def create_biannual_audit(request):
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

@login_required
def create_hazardous_audit(request):
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


# NEW: Create Annual Environmental Refresher Audit
@login_required
def create_annual_refresher_audit(request):
    if request.method == "POST":
        form = AnnualEnvironmentalRefresherForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'annual_refresher'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'Annual Environmental Refresher created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

# NEW: Create HSE Induction Audit
@login_required
def create_hse_induction_audit(request):
    if request.method == "POST":
        form = HSEInductionForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'hse_induction'
            audit.save()
            return JsonResponse({'status': 'success', 'message': 'HSE Induction created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# --- Existing Audit Get/Edit/Delete Views ---
# MODIFIED: get_audit_data to handle new audit types and their fields
@login_required
def get_audit_data(request, audit_id):
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
                if hasattr(value, 'pk'):
                    serialized_data[field_name] = value.pk
                else:
                    serialized_data[field_name] = str(value)
        
        serialized_data['id'] = audit.id
        serialized_data['audit_type'] = audit_type_str
        serialized_data['display_audit_type'] = audit.get_audit_type_display()
        if hasattr(audit, 'AuditID'):
            serialized_data['AuditID'] = audit.AuditID
        if hasattr(audit, 'date'):
             serialized_data['date'] = audit.date.isoformat() if isinstance(audit.date, datetime.date) else str(audit.date)
        if hasattr(audit, 'location'):
             serialized_data['location'] = audit.location
        
        # Include fields specific to Biannual Audits
        if audit_type_str == 'biannual':
            serialized_data['number_of_nonconformances'] = audit.number_of_nonconformances
            serialized_data['number_of_closeouts'] = audit.number_of_closeouts
        # NEW: Include fields specific to Annual Environmental Refresher
        elif audit_type_str == 'annual_refresher':
            serialized_data['number_of_employees'] = audit.number_of_employees
            serialized_data['number_of_employees_trained'] = audit.number_of_employees_trained
        # NEW: Include fields specific to HSE Induction
        elif audit_type_str == 'hse_induction':
            serialized_data['number_of_inductions'] = audit.number_of_inductions

        return JsonResponse(serialized_data)

    except Audit.DoesNotExist:
        return JsonResponse({"error": "Audit not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


# MODIFIED: edit_audit to handle new audit types
@login_required
def edit_audit(request, audit_id):
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
            
            # For 'biannual', 'annual_refresher', and 'hse_induction'
            # the fields are directly handled by form.save() as they are part of the model and forms.

            audit_instance.save()
            return JsonResponse({'status': 'success', 'message': 'Audit updated successfully'})
        else:
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'Invalid form data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


# MODIFIED: get_all_audits to handle new audit types and their fields for display
@login_required
def get_all_audits(request):
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
            # Include specific fields for different audit types
            if audit.audit_type == 'biannual':
                audit_data['number_of_nonconformances'] = audit.number_of_nonconformances
                audit_data['number_of_closeouts'] = audit.number_of_closeouts
            elif audit.audit_type == 'annual_refresher':
                audit_data['number_of_employees'] = audit.number_of_employees
                audit_data['number_of_employees_trained'] = audit.number_of_employees_trained
            elif audit.audit_type == 'hse_induction':
                audit_data['number_of_inductions'] = audit.number_of_inductions
            
            serialized_audits.append(audit_data)
        return JsonResponse(serialized_audits, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve audit list: {str(e)}"}, status=500)

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

# --- User Management Views (no changes) ---
@login_required
def create_user(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            return JsonResponse({'status': 'success', 'message': f'User {user.username} created successfully'})
        else:
            return JsonResponse({'status': 'error', 'message': 'Invalid user data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

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
                'groups': group_names,
            })
        return JsonResponse(serialized_users, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve user list: {str(e)}"}, status=500)

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
            'groups': group_names,
            'selected_group_ids': [group.id for group in user.groups.all()]
        }
        return JsonResponse(serialized_data)
    except User.DoesNotExist:
        return JsonResponse({"error": "User not found"}, status=404)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)

@login_required
def edit_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'success', 'message': f'User {user.username} updated successfully'})
        else:
            print(form.errors)
            return JsonResponse({'status': 'error', 'message': 'Invalid user data', 'errors': form.errors}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)

@login_required
def delete_user(request, user_id):
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

@login_required
def get_all_groups(request):
    try:
        groups = Group.objects.all().order_by('name')
        serialized_groups = [{'id': group.id, 'name': group.name} for group in groups]
        return JsonResponse(serialized_groups, safe=False)
    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve groups: {str(e)}"}, status=500)

@login_required
def get_monthly_inspection_scores(request):
    try:
        departments_data = Audit.LOCATION_CHOICES 
        current_month_scores = []
        last_year_average_scores = []
        
        now = timezone.now()
        current_month = now.month
        current_year = now.year
        
        one_year_ago = now - datetime.timedelta(days=365)
        
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
                current_month_scores.append(None)

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
                last_year_average_scores.append(None)

        chart_data = {
            'labels': [choice[1] for choice in departments_data],
            'currentMonthScores': current_month_scores,
            'lastYearAverageScores': last_year_average_scores,
            'currentMonthName': current_month_name,
            'target': 100
        }
        return JsonResponse(chart_data)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve monthly inspection scores: {str(e)}"}, status=500)


@login_required
def get_biannual_ncr_chart_data(request):
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
            open_ncrs_data.append(max(0, open_ncrs_sum))

        chart_data = {
            'labels': labels,
            'totalNCRs': total_ncrs_data,
            'openNCRs': open_ncrs_data,
        }
        return JsonResponse(chart_data)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"error": f"Failed to retrieve biannual NCR chart data: {str(e)}"}, status=500)

