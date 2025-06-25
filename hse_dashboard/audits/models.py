from django.db import models
from django.utils import timezone # Import timezone for current date
import datetime

# Create your models here.

class Audit(models.Model):

    ######################### GENERAL #########################

    AUDIT_TYPE_CHOICES = [
        ('monthly', 'Monthly Inspection'),
        ('biannual', 'Biannual Inspection'),
        ('hazardous', 'Hazardous Waste Inspection'),
        ('chemical_waste', 'Chemical Waste Inventory')
    ]

    audit_type = models.CharField(
        max_length=20,
        choices=AUDIT_TYPE_CHOICES,
        default='monthly' # Keep default='monthly' but ensure views override it for other types
    )

    date = models.DateField(default=datetime.date.today)

    AuditID = models.CharField(max_length=5, unique=True, editable=False, blank=True)

    LOCATION_CHOICES = [
        ('KBD Fisheries Lab', 'KBD Fisheries Lab'),
        ('KBD Algae Lab', 'KBD Algae Lab'),
        ('KBD Aquaculture Lab', 'KBD Aquaculture Lab'),
        ('KBD Algae Facility Laboratory', 'KBD Algae Facility Laboratory'),
        ('Duba Lab', 'Duba Lab'),
        ('Jizan Lab', 'Jizan Lab'),
        ('Jubail Lab', 'Jubail Lab'),
        ('Al Raes Sea Cage Farms', 'Al Raes Sea Cage Farms'),
        ('Algae Facility Phase 2', 'Algae Facility Phase 2'),
    ]
    location = models.CharField(max_length=30, choices=LOCATION_CHOICES, blank=True, null=True)

    # Consider adding a user field for who created/last modified the audit (good practice)
    # user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    ######################### MONTHLY INSPECTIONS ###############################

    # Safety and Equipment - ADDED null=True, blank=True
    fire_extinguishers_checked = models.BooleanField(default=False, null=True, blank=True)
    emergency_exits_inspected = models.BooleanField(default=False, null=True, blank=True)
    first_aid_kits_checked = models.BooleanField(default=False, null=True, blank=True)
    spill_kits_stocked = models.BooleanField(default=False, null=True, blank=True)
    ppe_stocked = models.BooleanField(default=False, null=True, blank=True)
    lab_coats_clean = models.BooleanField(default=False, null=True, blank=True)

    # Waste Disposal - ADDED null=True, blank=True
    biohazard_waste_reviewed = models.BooleanField(default=False, null=True, blank=True)
    chemical_waste_reviewed = models.BooleanField(default=False, null=True, blank=True)
    glass_sharp_waste_reviewed = models.BooleanField(default=False, null=True, blank=True)

    # Cleanliness and Surfaces - ADDED null=True, blank=True
    lab_surfaces_clean = models.BooleanField(default=False, null=True, blank=True)
    balances_calibrated_cleaned = models.BooleanField(default=False, null=True, blank=True)
    microscopes_calibrated_cleaned = models.BooleanField(default=False, null=True, blank=True)
    freezers_functional_clean = models.BooleanField(default=False, null=True, blank=True)
    # Chemical Management - ADDED null=True, blank=True
    secondary_containment_ok = models.BooleanField(default=False, null=True, blank=True)
    evidence_of_spills_or_expired_stock = models.BooleanField(default=False, null=True, blank=True)
    chemicals_stored_labelled = models.BooleanField(default=False, null=True, blank=True)
    safety_data_sheets_available = models.BooleanField(default=False, null=True, blank=True)
    chemicals_in_inventory = models.BooleanField(default=False, null=True, blank=True)
    chemical_containers_closed_and_disposed = models.BooleanField(default=False, null=True, blank=True)
    spill_kit_accessible = models.BooleanField(default=False, null=True, blank=True)

    # Biological Storage & Training - ADDED null=True, blank=True
    bio_sample_temp_maintained = models.BooleanField(default=False, null=True, blank=True)
    lab_consumables_stock_ok = models.BooleanField(default=False, null=True, blank=True)
    storage_conditions_ok = models.BooleanField(default=False, null=True, blank=True)

    # Training (aggregate check for now) - ADDED null=True, blank=True
    training_up_to_date = models.BooleanField(default=False, null=True, blank=True)


    ######################### CHEMICAL WASTE ###############################

    # ADDED null=True, blank=True to all Char/Float/Boolean fields
    chemical_name = models.CharField(max_length=100, null=True, blank=True)
    quantity_liters = models.FloatField(default=0.0, help_text="Total quantity in liters", null=True, blank=True)
    container_size = models.CharField(max_length=50, help_text="E.g., 500ml, 1L, etc.", null=True, blank=True)
    stored_in = models.CharField(max_length=100, help_text="Storage location or cabinet", null=True, blank=True)
    used_by = models.CharField(max_length=100, help_text="Name of the person who used the chemical", null=True, blank=True)
    used_for = models.CharField(max_length=100, help_text="Purpose for which the chemical was used", null=True, blank=True)
    hazard_classification = models.CharField(max_length=100, null=True, blank=True)
    disposed = models.BooleanField(default=False, null=True, blank=True)
    disposed_date = models.DateField(null=True, blank=True) # Already had null=True, blank=True
    disposed_by = models.CharField(max_length=100, null=True, blank=True)

    ######################### HAZARDOUS WASTE INSPECTION ###############################

    # ADDED null=True, blank=True to all Boolean fields
    hazardous_waste_generated = models.BooleanField(default=False, verbose_name="Has hazardous waste been generated this week?", null=True, blank=True)
    containers_labeled = models.BooleanField(default=False, verbose_name="Are containers labeled?", null=True, blank=True)
    containers_segregated = models.BooleanField(default=False, verbose_name="Are containers segregated?", null=True, blank=True)
    containers_free_from_leaks = models.BooleanField(default=False, verbose_name="Are containers free from leaks?", null=True, blank=True)
    secondary_containment_in_place = models.BooleanField(default=False, verbose_name="Is secondary containment in place?", null=True, blank=True)
    storage_limit_exceeded = models.BooleanField(default=False, verbose_name="Has the storage limit been exceeded?", null=True, blank=True)
    remarks_or_corrective_action = models.TextField(blank=True, null=True, verbose_name="Remarks/Corrective Action Taken") # Added null=True


    def save(self, *args, **kwargs):
        if not self.AuditID:
            last = Audit.objects.order_by('-id').first()
            # Ensure next_number logic handles cases where last is None correctly for initial ID
            next_number = 0 if not last or not last.AuditID.isdigit() else int(last.AuditID)
            self.AuditID = str(next_number + 1).zfill(5)  # pad with zeros
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Audit number {self.AuditID} on {self.date}"
