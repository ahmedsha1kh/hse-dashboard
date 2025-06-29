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

    completed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='completed_audits',
        verbose_name='Completed By',
        help_text='The user who completed this audit.'
    )

    ######################### MONTHLY INSPECTIONS ###############################

    #FIELDS FOR ALGAE LAB, AQUACULTURE LAB, DUBA LAB, JIZAN LAB, FISHERIES, JUBAIL LAB
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

    # FIELDS FOR AL RAYEES SEA CAGE FARMS
    over_accumulation_fish_waste = models.BooleanField(
        verbose_name="Is there any over accumulation of fish waste or unconsumed feed around the cages?",
        default=False,
        blank=True,
        null=True
    )
    nets_checked_for_damage = models.BooleanField(
        verbose_name="Are nets checked for tears or damage to prevent fish escape?",
        default=False,
        blank=True,
        null=True
    )
    cages_secured_to_sea_bed = models.BooleanField(
        verbose_name="Are the cages secured to the sea bed at all anchor points?",
        default=False,
        blank=True,
        null=True
    )
    operations_minimal_disturbance = models.BooleanField(
        verbose_name="Are all operations conducted with minimal disturbance to the surrounding environment?",
        default=False,
        blank=True,
        null=True
    )
    visible_impact_on_marine_life = models.BooleanField(
        verbose_name="Is there any visible impact on marine life outside the cage area?",
        default=False,
        blank=True,
        null=True
    )

    # Water Quality Monitoring
    water_parameters_recorded = models.BooleanField(
        verbose_name="Are water parameters (e.g., temperature, salinity, pH) being recorded at regular intervals?",
        default=False,
        blank=True,
        null=True
    )
    significant_variations_water_quality = models.BooleanField(
        verbose_name="Are there any significant variations in water quality parameters from baseline values?",
        default=False,
        blank=True,
        null=True
    )

    # Waste Management (Aquaculture specific)
    waste_materials_properly_disposed = models.BooleanField(
        verbose_name="Are waste materials (e.g., damaged nets, fish remains) being properly segregated and disposed?",
        default=False,
        blank=True,
        null=True
    )

    # Emergency Preparedness (Boats)
    adequate_spill_kits_on_boats = models.BooleanField(
        verbose_name="Are adequate spill kits present on boats for handling emergencies?",
        default=False,
        blank=True,
        null=True
    )

    # Incidents/Observations
    unusual_incidents_observations = models.BooleanField(
        verbose_name="Were there any unusual incidents or observations during the inspection?",
        default=False,
        blank=True,
        null=True
    )

    # Material Storage (Aquaculture specific)
    material_storage_well_maintained = models.BooleanField(
        verbose_name="Are material storage areas well-maintained, free from contamination and pests?",
        default=False,
        blank=True,
        null=True
    )
    spill_kit_available_storage_area = models.BooleanField(
        verbose_name="Is there a spill kit available in the stoage area?",
        default=False,
        blank=True,
        null=True
    )
    chemicals_lubricants_oils_secondary_containment = models.BooleanField(
        verbose_name="Are all chemicals, lubricants, and oils stored in designated secondary containments?",
        default=False,
        blank=True,
        null=True
    )
    storage_containers_sealed_free_leaks = models.BooleanField(
        verbose_name="Are storage containers sealed and free from leaks?",
        default=False,
        blank=True,
        null=True
    )
    hazardous_materials_properly_stored = models.BooleanField(
        verbose_name="Are hazardous materials stored properly with clear labels and SDS available?",
        default=False,
        blank=True,
        null=True
    )
    record_environmental_incidents_past_week = models.BooleanField(
        verbose_name="Is there a record of any environmental incidents (e.g., spills) from the past week?",
        default=False,
        blank=True,
        null=True
    )

    # FIELDS FOR ALGAE FACILITY AND ALGAE FACILITY PHASE 2
    coshh_register_valid_and_up_to_date = models.BooleanField(
        verbose_name="Is the COSHH register valid and up to date?",
        default=False,
        blank=True,
        null=True
    )
    chemical_inspection_monthly = models.BooleanField(
        verbose_name="Is chemical inspection carried out on a monthly basis?",
        default=False,
        blank=True,
        null=True
    )
    coshh_assessment_available_storage_location = models.BooleanField(
        verbose_name="Is COSHH assessment available at the storage location?",
        default=False,
        blank=True,
        null=True
    )
    all_chemicals_have_manufacturer_labels = models.BooleanField(
        verbose_name="Check all chemicals have manufacturer labels?",
        default=False,
        blank=True,
        null=True
    )
    fuels_oils_hazardous_liquids_secondary_containment = models.BooleanField(
        verbose_name="Check if all fuels, oils and hazardous liquid chemicals are stored within secondary containment?",
        default=False,
        blank=True,
        null=True
    )
    chemical_storage_room_proper_signage = models.BooleanField(
        verbose_name="Check if chemical storage room has proper signage. Signage must say 'Chemical Storage Area' and include hazard warning.",
        default=False,
        blank=True,
        null=True
    )
    secondary_containment_structures_good_condition = models.BooleanField(
        verbose_name="Are secondary containment structures in good condition with no visible signs of leakage?",
        default=False,
        blank=True,
        null=True
    )
    spill_kits_available_stocked_accessible = models.BooleanField(
        verbose_name="Are spill kits available, adequately stocked, and accessible?",
        default=False,
        blank=True,
        null=True
    )
    employees_trained_spcc_spill_response = models.BooleanField(
        verbose_name="Are all employees trained on Spill Prevention Control and New Measures (SPCC) requirements and spill response?",
        default=False,
        blank=True,
        null=True
    )

    # Evaporation Pond
    evaporation_pond_free_algal_growth_contamination = models.BooleanField(
        verbose_name="Is the evaporation pond free from any visible algal growth or contamination?",
        default=False,
        blank=True,
        null=True
    )
    evaporation_pond_clean_and_well_maintained = models.BooleanField(
        verbose_name="Is the evaporation pond clean and well-maintained?",
        default=False,
        blank=True,
        null=True
    )
    signs_overflow_leakage_evaporation_pond = models.BooleanField(
        verbose_name="Are there any signs of overflow or leakage from the evaporation pond?",
        default=False,
        blank=True,
        null=True
    )
    water_quality_evaporation_pond_acceptable = models.BooleanField(
        verbose_name="Is the water quality in the evaporation pond within acceptable parameters?",
        default=False,
        blank=True,
        null=True
    )
    # Waste Management
    log_maintained_reject_water_recycling = models.BooleanField(
        verbose_name="Is there a log maintained for the reject water recycling process?",
        default=False,
        blank=True,
        null=True
    )
    hazardous_waste_collected_stored_separately = models.BooleanField(
        verbose_name="Is hazardous waste collected and stored separately from general waste?",
        default=False,
        blank=True,
        null=True
    )
    general_waste_properly_segregated_disposed = models.BooleanField(
        verbose_name="Is general waste properly segregated and disposed of?",
        default=False,
        blank=True,
        null=True
    )
    hazardous_waste_containers_labeled_designated_areas = models.BooleanField(
        verbose_name="Are hazardous waste containers properly labeled and stored in designated areas?",
        default=False,
        blank=True,
        null=True
    )
    waste_collection_areas_free_spills_leaks_contamination = models.BooleanField(
        verbose_name="Are waste collection areas free from spills, leaks, or contamination?",
        default=False,
        blank=True,
        null=True
    )
    record_waste_collection_storage_disposal = models.BooleanField(
        verbose_name="Is there a record of waste collection, storage, and disposal?",
        default=False,
        blank=True,
        null=True
    )
    general_waste_properly_managed_no_waste_lying_around = models.BooleanField(
        verbose_name="Is general waste properly managed, and is there no waste lying around the site?",
        default=False,
        blank=True,
        null=True
    )

    # Pest Control
    all_drums_containers_free_stagnant_water = models.BooleanField(
        verbose_name="Are all drums and containers free from stagnant water?",
        default=False,
        blank=True,
        null=True
    )
    visible_mosquito_larvae_presence = models.BooleanField(
        verbose_name="Is there any visible mosquito or larvae presence on site?",
        default=False,
        blank=True,
        null=True
    )
    other_signs_pests_within_site = models.BooleanField(
        verbose_name="Are there any other signs of pests within the site?",
        default=False,
        blank=True,
        null=True
    )

    # Emissions and Odour
    visible_plume_emissions_spray_dryer = models.BooleanField(
        verbose_name="Are there any visible plume emissions from the spray dryer when it is operational?",
        default=False,
        blank=True,
        null=True
    )
    odours_from_site_operations = models.BooleanField(
        verbose_name="Are there any odours from the site operations?",
        default=False,
        blank=True,
        null=True
    )

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

