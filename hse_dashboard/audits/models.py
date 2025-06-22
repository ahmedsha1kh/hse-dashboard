from django.db import models

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
        default='monthly'
    )

    date = models.DateField(default='2007-11-07')

    AuditID = models.CharField(max_length=5, unique=True, editable=False, blank=True)

    ######################### MONTHLY INSPECTIONS ###############################

    # Safety and Equipment
    fire_extinguishers_checked = models.BooleanField(default=False)
    emergency_exits_inspected = models.BooleanField(default=False)
    first_aid_kits_checked = models.BooleanField(default=False)
    spill_kits_stocked = models.BooleanField(default=False)
    ppe_stocked = models.BooleanField(default=False)
    lab_coats_clean = models.BooleanField(default=False)

    # Waste Disposal
    biohazard_waste_reviewed = models.BooleanField(default=False)
    chemical_waste_reviewed = models.BooleanField(default=False)
    glass_sharp_waste_reviewed = models.BooleanField(default=False)

    # Cleanliness and Surfaces
    lab_surfaces_clean = models.BooleanField(default=False)
    balances_calibrated_cleaned = models.BooleanField(default=False)
    microscopes_calibrated_cleaned = models.BooleanField(default=False)
    freezers_functional_clean = models.BooleanField(default=False)

    # Chemical Management
    secondary_containment_ok = models.BooleanField(default=False)
    evidence_of_spills_or_expired_stock = models.BooleanField(default=False)
    chemicals_stored_labelled = models.BooleanField(default=False)
    safety_data_sheets_available = models.BooleanField(default=False)
    chemicals_in_inventory = models.BooleanField(default=False)
    chemical_containers_closed_and_disposed = models.BooleanField(default=False)
    spill_kit_accessible = models.BooleanField(default=False)

    # Biological Storage & Training
    bio_sample_temp_maintained = models.BooleanField(default=False)
    lab_consumables_stock_ok = models.BooleanField(default=False)
    storage_conditions_ok = models.BooleanField(default=False)

    # Training (aggregate check for now)
    training_up_to_date = models.BooleanField(default=False)


    ######################### CHEMICAL WASTE ###############################

    chemical_name = models.CharField(max_length=100)
    quantity_liters = models.FloatField(default=0.0, help_text="Total quantity in liters")
    container_size = models.CharField(max_length=50, help_text="E.g., 500ml, 1L, etc.")
    stored_in = models.CharField(max_length=100, help_text="Storage location or cabinet")
    used_by = models.CharField(max_length=100, help_text="Name of the person who used the chemical")
    used_for = models.CharField(max_length=100, help_text="Purpose for which the chemical was used")
    hazard_classification = models.CharField(max_length=100)
    disposed = models.BooleanField(default=False)
    disposed_date = models.DateField(null=True, blank=True)
    disposed_by = models.CharField(max_length=100)

    ######################### HAZARDOUS WASTE INSPECTION ###############################

    hazardous_waste_generated = models.BooleanField(default=False, verbose_name="Has hazardous waste been generated this week?")
    containers_labeled = models.BooleanField(default=False, verbose_name="Are containers labeled?")
    containers_segregated = models.BooleanField(default=False, verbose_name="Are containers segregated?")
    containers_free_from_leaks = models.BooleanField(default=False, verbose_name="Are containers free from leaks?")
    secondary_containment_in_place = models.BooleanField(default=False, verbose_name="Is secondary containment in place?")
    storage_limit_exceeded = models.BooleanField(default=False, verbose_name="Has the storage limit been exceeded?")
    remarks_or_corrective_action = models.TextField(blank=True, verbose_name="Remarks/Corrective Action Taken")



    def save(self, *args, **kwargs):
        if not self.AuditID:
            last = Audit.objects.order_by('-id').first()
            next_number = 0 if not last else int(last.AuditID)
            self.AuditID = str(next_number + 1).zfill(5)  # pad with zeros
        super().save(*args, **kwargs)


    def __str__(self):
        return f"Audit number {self.AuditID} on {self.date}"

