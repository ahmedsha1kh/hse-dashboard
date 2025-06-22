from django import forms
from .models import Audit  # import your model

class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['audit_type', 'fire_extinguishers_checked', 'emergency_exits_inspected', ]  # add more fields as needed

class MonthlyAuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['date', 'fire_extinguishers_checked', 'emergency_exits_inspected']
        
class BiannualAuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['date', 'lab_coats_clean', 'biohazard_waste_reviewed']  # Replace as needed

class HazardousWasteForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['date', 'hazardous_waste_generated', 'containers_labeled', 'remarks_or_corrective_action']

class ChemicalAuditForm(forms.ModelForm):
    class Meta:
        model = Audit  # or a separate model for ChemicalAudit
        fields = ['date', 'chemical_name', 'quantity_liters', 'container_size', 'stored_in']  # Replace with your fields
