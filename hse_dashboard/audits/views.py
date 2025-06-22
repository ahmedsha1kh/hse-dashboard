from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import AuditForm, ChemicalAuditForm, BiannualAuditForm, MonthlyAuditForm, HazardousWasteForm
from .models import Audit
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
import datetime

# Create your views here.

AUDIT_TYPE_FORMS = {
    'monthly': MonthlyAuditForm,
    'biannual': BiannualAuditForm,
    'hazardous': HazardousWasteForm, # Ensure this matches the 'audit_type' string in your model for hazardous waste
    'chemical_waste': ChemicalAuditForm, # Ensure this matches the 'audit_type' string in your model for chemical audits
    # Add other audit types as they appear in your Audit model
    # If 'AuditForm' covers common fields for types not explicitly listed, you might use it as a default.
    # For now, let's assume 'audit_type' in your Audit model directly maps to these keys.
}


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
    # Pass all specific forms for creation modals
    context = {
        "chemical_form": ChemicalAuditForm(),
        "monthly_form": MonthlyAuditForm(),
        "biannual_form": BiannualAuditForm(),
        "hazardous_form": HazardousWasteForm(),
        "audits": Audit.objects.all(), # Pass all audits for the selection list
    }
    return render(request, "home.html", context)

# Your create audit views remain the same
def create_chemical_audit(request):
    if request.method == "POST":
        form = ChemicalAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'chemical_waste' 
            audit.save()
            return redirect("home")
    return redirect("home")

def create_monthly_audit(request):
    if request.method == "POST":
        form = MonthlyAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'monthly' 
            form.save()
            return redirect("home")
    return redirect("home")

def create_biannual_audit(request):
    if request.method == "POST":
        form = BiannualAuditForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'biannual' 
            form.save()
            return redirect("home")
    return redirect("home")

def create_hazardous_audit(request):
    if request.method == "POST":
        form = HazardousWasteForm(request.POST)
        if form.is_valid():
            audit = form.save(commit=False)
            audit.audit_type = 'hazardous' 
            form.save()
            return redirect("home")
    return redirect("home")

# === NEW/MODIFIED VIEWS FOR EDITING ===

@login_required
def get_audit_data(request, audit_id):
    try:
        audit = get_object_or_404(Audit, id=audit_id)
        audit_type_str = audit.audit_type

        # --- IMPORTANT DEBUG PRINTS ---
        print(f"\n--- DEBUGGING GET_AUDIT_DATA FOR AUDIT ID: {audit_id} ---")
        print(f"1. Actual Audit Type from DB: '{audit_type_str}'")

        form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

        if not form_class:
            print(f"ERROR: No specific form found for audit type '{audit_type_str}'")
            return JsonResponse({"error": "No specific form found for this audit type", "audit_type": audit_type_str}, status=400)

        print(f"2. Resolved Form Class: {form_class.__name__}")

        form = form_class(instance=audit)

        serialized_data = {}
        print("3. Fields being processed by the selected form:")
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
                    serialized_data[field_name] = str(value) # Fallback to string for complex objects
            print(f"   - Field Name: '{field_name}', Value: '{serialized_data.get(field_name)}'")

        serialized_data['id'] = audit.id
        serialized_data['audit_type'] = audit_type_str # Ensure audit_type is in the final data
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
        import traceback
        traceback.print_exc()
        print(f"UNEXPECTED ERROR in get_audit_data for audit ID {audit_id}: {e}")
        return JsonResponse({"error": f"An unexpected error occurred: {str(e)}"}, status=500)


@login_required
def edit_audit(request, audit_id):
    audit = get_object_or_404(Audit, id=audit_id)
    audit_type_str = audit.audit_type

    form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

    if not form_class:
        return redirect('home') # Or render an error page

    if request.method == 'POST':
        form = form_class(request.POST, instance=audit)
        if form.is_valid():
            form.save()
            return redirect('home')
        else:
            print(form.errors) # For debugging form validation errors
    return redirect('home') # Redirect back to home on GET or if form is invalid on POST
