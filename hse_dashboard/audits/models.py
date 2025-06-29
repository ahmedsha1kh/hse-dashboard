# audits/models.py

from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User

class Audit(models.Model):

    ######################### GENERAL #########################

    AUDIT_TYPE_CHOICES = [
        ('chemical_waste', 'Hazardous Waste Log'),
        ('monthly', 'Monthly Inspection'),
        ('biannual', 'Biannual Environment Audit'),
        ('hazardous', 'Hazardous Waste Inspection'),
        ('annual_refresher', 'Annual Environmental Refresher'), 
        ('hse_induction', 'HSE Induction'),
        ('environmental_incidents', 'Environmental Incidents')
    ]

    audit_type = models.CharField(
        max_length=25,
        choices=AUDIT_TYPE_CHOICES,
        default='monthly'
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

    location = models.CharField(max_length=100, choices=LOCATION_CHOICES, blank=True, null=True)

    score = models.FloatField(
        null=True,
        blank=True,
        verbose_name="Inspection Score (%)",
        help_text="Automatically calculated percentage score for Monthly Inspections."
    )

    ######################### MONTHLY INSPECTIONS ###############################

    fire_extinguishers_checked = models.BooleanField(default=False, null=True, blank=True)
    emergency_exits_inspected = models.BooleanField(default=False, null=True, blank=True)
    first_aid_kits_checked = models.BooleanField(default=False, null=True, blank=True)
    spill_kits_stocked = models.BooleanField(default=False, null=True, blank=True)
    ppe_stocked = models.BooleanField(default=False, null=True, blank=True)
    lab_coats_clean = models.BooleanField(default=False, null=True, blank=True)

    biohazard_waste_reviewed = models.BooleanField(default=False, null=True, blank=True)
    chemical_waste_reviewed = models.BooleanField(default=False, null=True, blank=True)
    glass_sharp_waste_reviewed = models.BooleanField(default=False, null=True, blank=True)

    lab_surfaces_clean = models.BooleanField(default=False, null=True, blank=True)
    balances_calibrated_cleaned = models.BooleanField(default=False, null=True, blank=True)
    microscopes_calibrated_cleaned = models.BooleanField(default=False, null=True, blank=True)
    freezers_functional_clean = models.BooleanField(default=False, null=True, blank=True)

    secondary_containment_ok = models.BooleanField(default=False, null=True, blank=True)
    evidence_of_spills_or_expired_stock = models.BooleanField(default=False, null=True, blank=True)
    chemicals_stored_labelled = models.BooleanField(default=False, null=True, blank=True)
    safety_data_sheets_available = models.BooleanField(default=False, null=True, blank=True)
    chemicals_in_inventory = models.BooleanField(default=False, null=True, blank=True)
    chemical_containers_closed_and_disposed = models.BooleanField(default=False, null=True, blank=True)
    spill_kit_accessible = models.BooleanField(default=False, null=True, blank=True)

    bio_sample_temp_maintained = models.BooleanField(default=False, null=True, blank=True)
    lab_consumables_stock_ok = models.BooleanField(default=False, null=True, blank=True)
    storage_conditions_ok = models.BooleanField(default=False, null=True, blank=True)
    training_up_to_date = models.BooleanField(default=False, null=True, blank=True)


    ######################### CHEMICAL WASTE ###############################

    chemical_name = models.CharField(max_length=100, null=True, blank=True)
    quantity_liters = models.FloatField(default=0.0, help_text="Total quantity in liters", null=True, blank=True)
    container_size = models.CharField(max_length=50, help_text="E.g., 500ml, 1L, etc.", null=True, blank=True)
    stored_in = models.CharField(max_length=100, help_text="Storage location or cabinet", null=True, blank=True)
    used_by = models.CharField(max_length=100, help_text="Name of the person who used the chemical", null=True, blank=True)
    used_for = models.CharField(max_length=100, help_text="Purpose for which the chemical was used", null=True, blank=True)
    hazard_classification = models.CharField(max_length=100, null=True, blank=True)
    disposed = models.BooleanField(default=False, null=True, blank=True)
    disposed_date = models.DateField(null=True, blank=True)
    disposed_by = models.CharField(max_length=100, null=True, blank=True)

    ######################### HAZARDOUS WASTE INSPECTION ###############################

    hazardous_waste_generated = models.BooleanField(default=False, verbose_name="Has hazardous waste been generated this week?", null=True, blank=True)
    containers_labeled = models.BooleanField(default=False, verbose_name="Are containers labeled?", null=True, blank=True)
    containers_segregated = models.BooleanField(default=False, verbose_name="Are containers segregated?", null=True, blank=True)
    containers_free_from_leaks = models.BooleanField(default=False, verbose_name="Are containers free from leaks?", null=True, blank=True)
    secondary_containment_in_place = models.BooleanField(default=False, verbose_name="Is secondary containment in place?", null=True, blank=True)
    storage_limit_exceeded = models.BooleanField(default=False, verbose_name="Has the storage limit been exceeded?", null=True, blank=True)
    remarks_or_corrective_action = models.TextField(blank=True, null=True, verbose_name="Remarks/Corrective Action Taken")

    ######################### BIANNUAL AUDIT EXISTING FIELDS ###############################
    number_of_closeouts = models.IntegerField(default=0, null=True, blank=True)
    number_of_nonconformances = models.IntegerField(default=0, null=True, blank=True)

    ######################### ANNUAL ENVIRONMENTAL REFRESHER ###############################
    number_of_employees = models.IntegerField(default=220, null=True, blank=True)
    number_of_employees_trained = models.IntegerField(default=0, null=True, blank=True)

    ######################### HSE INDUCTIONS ###############################
    number_of_inductions = models.IntegerField(default=0, null=True, blank=True)

    ######################### ENVIRONMENTAL INCIDENTS ###############################
    number_of_incidents = models.IntegerField(null=True, blank=True, default=0, help_text="Number of environmental incidents recorded.")
    details = models.TextField(blank=True, null=True, help_text="Details of the environmental incidents.")


    def save(self, *args, **kwargs):
        if not self.AuditID:
            last = Audit.objects.order_by('-id').first()
            next_number = 0 if not last or not last.AuditID.isdigit() else int(last.AuditID)
            self.AuditID = str(next_number + 1).zfill(5)
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Audit {self.AuditID} ({self.get_audit_type_display()}) on {self.date}"

