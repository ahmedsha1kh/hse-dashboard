from django import forms
from .models import Audit  # import your model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm 
from django.contrib.auth.models import User, Group # Import User and Group

class AuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['audit_type', 'fire_extinguishers_checked', 'emergency_exits_inspected', ]  # add more fields as needed

class MonthlyAuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['date', 'location', 'fire_extinguishers_checked', 'emergency_exits_inspected', 'first_aid_kits_checked', 
                  'spill_kits_stocked', 'ppe_stocked', 'lab_coats_clean', 'biohazard_waste_reviewed', 'chemical_waste_reviewed', 
                  'glass_sharp_waste_reviewed', 'lab_surfaces_clean', 'balances_calibrated_cleaned', 'microscopes_calibrated_cleaned',
                  'freezers_functional_clean', 'secondary_containment_ok', 'evidence_of_spills_or_expired_stock', 
                  'chemicals_stored_labelled', 'safety_data_sheets_available', 'chemicals_in_inventory', 'chemical_containers_closed_and_disposed',
                  'spill_kit_accessible', 'bio_sample_temp_maintained', 'lab_consumables_stock_ok', 'storage_conditions_ok',
                  'training_up_to_date', 'score']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'score': forms.NumberInput(attrs={'readonly': 'readonly'})
        }

        
class BiannualAuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = ['date', 'location', 'number_of_closeouts', 'number_of_nonconformances']  # Replace as needed

class HazardousWasteForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'date',
            'location', 

            'hazardous_waste_generated',
            'containers_labeled',
            'containers_segregated',
            'containers_free_from_leaks',
            'secondary_containment_in_place',
            'storage_limit_exceeded',
            'remarks_or_corrective_action',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

class ChemicalAuditForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'date',
            'location', 

            'chemical_name',
            'quantity_liters',
            'container_size',
            'stored_in',
            'used_by',
            'used_for',
            'hazard_classification',
            'disposed',
            'disposed_date',
            'disposed_by',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'disposed_date': forms.DateInput(attrs={'type': 'date'}),
        }

class AnnualEnvironmentalRefresherForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'number_of_employees',
            'number_of_employees_trained',
        ]

class HSEInductionForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'number_of_employees',
            'number_of_inductions',
        ]

class EnvironmentalIncidentForm(AuditForm):
    class Meta():
        model = Audit
        fields = ['date', 'location', 'number_of_incidents', 'details']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'details': forms.Textarea(attrs={'rows': 4}),
        }




# CRITICAL: CustomUserCreationForm
class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=150, required=False, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Group(s)"
    )

    class Meta(UserCreationForm.Meta):
        model = User
        # Include username, first_name, last_name, groups, and then the password fields from base
        fields = ('username', 'first_name', 'last_name', 'groups') + UserCreationForm.Meta.fields[2:]

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            # Set groups after user is saved (Many-to-Many relationship)
            if self.cleaned_data['groups']:
                user.groups.set(self.cleaned_data['groups'])
        return user

# UPDATED: CustomUserChangeForm
class CustomUserChangeForm(UserChangeForm):
    first_name = forms.CharField(max_length=150, required=False, label="First Name")
    last_name = forms.CharField(max_length=150, required=False, label="Last Name")
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple,
        label="Group(s)" # Changed label for clarity
    )

    class Meta(UserChangeForm.Meta):
        model = User
        # Exclude password and other fields not needed for this basic edit form
        fields = ('username', 'first_name', 'last_name', 'groups')
        # We explicitly exclude 'password' field that UserChangeForm includes by default
        # because we are not changing password from this form.

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove password-related fields as they are not needed for this edit form
        if 'password' in self.fields:
            del self.fields['password']
        # UserChangeForm also adds a message about password, remove it
        if 'password_set_message' in self.fields:
            del self.fields['password_set_message']

    def save(self, commit=True):
        user = super().save(commit=False)
        # first_name and last_name are handled by super().save() if they are in fields
        
        if commit:
            user.save()
            # Update groups ManyToMany relationship
            if self.cleaned_data['groups']:
                user.groups.set(self.cleaned_data['groups'])
            else:
                user.groups.clear() # Clear groups if none are selected
        return user

# Helper for read-only score field
class ReadOnlyScoreWidget(forms.TextInput):
    def __init__(self, *args, **kwargs):
        kwargs['attrs'] = {'readonly': 'readonly', 'style': 'background: #f3f3f3;'}
        super().__init__(*args, **kwargs)

# 1. Main Labs (6 labs)
class MainLabMonthlyInspectionForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'date', 'score',
            'fire_extinguishers_checked', 'emergency_exits_inspected', 'first_aid_kits_checked',
            'spill_kits_stocked', 'ppe_stocked', 'lab_coats_clean',
            'biohazard_waste_reviewed', 'chemical_waste_reviewed', 'glass_sharp_waste_reviewed',
            'lab_surfaces_clean', 'balances_calibrated_cleaned', 'microscopes_calibrated_cleaned',
            'freezers_functional_clean', 'secondary_containment_ok', 'evidence_of_spills_or_expired_stock',
            'chemicals_stored_labelled', 'safety_data_sheets_available', 'chemicals_in_inventory',
            'chemical_containers_closed_and_disposed', 'spill_kit_accessible',
            'bio_sample_temp_maintained', 'lab_consumables_stock_ok', 'storage_conditions_ok', 'training_up_to_date',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'score': ReadOnlyScoreWidget(),
        }

# 2. Al Raes Sea Cage Farms (unique)
class AlRaesSeaCageFarmsMonthlyInspectionForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'date', 'score',
            'over_accumulation_fish_waste', 'nets_checked_for_damage', 'cages_secured_to_sea_bed',
            'operations_minimal_disturbance', 'visible_impact_on_marine_life',
            'water_parameters_recorded', 'significant_variations_water_quality',
            'waste_materials_properly_disposed', 'adequate_spill_kits_on_boats',
            'unusual_incidents_observations', 'material_storage_well_maintained',
            'spill_kit_available_storage_area', 'chemicals_lubricants_oils_secondary_containment',
            'storage_containers_sealed_free_leaks', 'hazardous_materials_properly_stored',
            'record_environmental_incidents_past_week',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'score': ReadOnlyScoreWidget(),
        }

# 3. Algae Facilities (2 labs)
class AlgaeFacilityMonthlyInspectionForm(forms.ModelForm):
    class Meta:
        model = Audit
        fields = [
            'date', 'score',
            'coshh_register_valid_and_up_to_date', 'chemical_inspection_monthly',
            'coshh_assessment_available_storage_location', 'all_chemicals_have_manufacturer_labels',
            'fuels_oils_hazardous_liquids_secondary_containment', 'chemical_storage_room_proper_signage',
            'secondary_containment_structures_good_condition', 'spill_kits_available_stocked_accessible',
            'employees_trained_spcc_spill_response', 'evaporation_pond_free_algal_growth_contamination',
            'evaporation_pond_clean_and_well_maintained', 'signs_overflow_leakage_evaporation_pond',
            'water_quality_evaporation_pond_acceptable', 'log_maintained_reject_water_recycling',
            'hazardous_waste_collected_stored_separately', 'general_waste_properly_segregated_disposed',
            'hazardous_waste_containers_labeled_designated_areas', 'waste_collection_areas_free_spills_leaks_contamination',
            'record_waste_collection_storage_disposal', 'general_waste_properly_managed_no_waste_lying_around',
            'all_drums_containers_free_stagnant_water', 'visible_mosquito_larvae_presence',
            'other_signs_pests_within_site', 'visible_plume_emissions_spray_dryer', 'odours_from_site_operations',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'score': ReadOnlyScoreWidget(),
        }

# 6 forms for main labs (Fisheries, Algae, Aquaculture, Duba, Jizan, Jubail)
MainLabMonthlyInspectionForms = [MainLabMonthlyInspectionForm for _ in range(6)]
# 2 forms for algae facilities
AlgaeFacilityMonthlyInspectionForms = [AlgaeFacilityMonthlyInspectionForm for _ in range(2)]
# 1 form for Al Raes
AlRaesSeaCageFarmsMonthlyInspectionForms = [AlRaesSeaCageFarmsMonthlyInspectionForm]
