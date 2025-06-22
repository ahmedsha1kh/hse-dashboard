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
            form.save()
            return redirect("home")
    return redirect("home")

def create_monthly_audit(request):
    if request.method == "POST":
        form = MonthlyAuditForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    return redirect("home")

def create_biannual_audit(request):
    if request.method == "POST":
        form = BiannualAuditForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    return redirect("home")

def create_hazardous_audit(request):
    if request.method == "POST":
        form = HazardousWasteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("home")
    return redirect("home")

# === NEW/MODIFIED VIEWS FOR EDITING ===

@login_required 
# @csrf_exempt # Only for development, if you're not passing CSRF token with fetch/AJAX posts
def get_audit_data(request, audit_id):
    try:
        audit = get_object_or_404(Audit, id=audit_id)
        audit_type_str = audit.audit_type # This is crucial: get the actual type from the audit instance

        form_class = AUDIT_TYPE_FORMS.get(audit_type_str)

        if not form_class:
            # Handle unknown audit types gracefully
            return JsonResponse({"error": "No specific form found for this audit type", "audit_type": audit_type_str}, status=400)

        # Instantiate the correct form with the audit instance.
        # This form instance now knows which fields are relevant via its Meta.fields
        form = form_class(instance=audit)

        serialized_data = {}
        # Iterate only through the fields defined in the specific ModelForm's Meta.fields
        for field_name, form_field in form.fields.items():
            # Get the value directly from the Audit model instance
            value = getattr(audit, field_name, None)

            # --- Serialization logic for JsonResponse ---
            # This handles different Python types to ensure they are JSON serializable
            if isinstance(value, datetime.date):
                serialized_data[field_name] = value.isoformat() # Format dates as 'YYYY-MM-DD'
            elif isinstance(value, datetime.datetime):
                serialized_data[field_name] = value.isoformat() # Format datetimes as 'YYYY-MM-DDTHH:MM:SS'
            elif isinstance(value, (bool, int, float, str)):
                serialized_data[field_name] = value
            elif value is None:
                serialized_data[field_name] = None
            else:
                # Handle other types if necessary (e.g., ChoiceFields, ForeignKeys)
                # For ChoiceFields, you might send the current chosen value (string/int)
                # For ForeignKeys, you might send the related object's primary key (value.pk) or __str__ representation.
                if hasattr(value, 'pk'): # For related objects (ForeignKeys)
                    serialized_data[field_name] = value.pk
                else:
                    serialized_data[field_name] = str(value) # Fallback to string for complex objects

        # Always include these for frontend logic
        serialized_data['id'] = audit.id
        serialized_data['audit_type'] = audit_type_str
        # Include AuditID if it's a field in your Audit model and you want to display it
        if hasattr(audit, 'AuditID'):
            serialized_data['AuditID'] = audit.AuditID
        # Include date if it's a field in your Audit model and you want to display it
        if hasattr(audit, 'date'):
             serialized_data['date'] = audit.date.isoformat() if isinstance(audit.date, datetime.date) else str(audit.date)


        return JsonResponse(serialized_data)

    except Audit.DoesNotExist:
        return JsonResponse({"error": "Audit not found"}, status=404)
    except Exception as e:
        # It's good practice to print the full traceback during development
        import traceback
        traceback.print_exc()
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
