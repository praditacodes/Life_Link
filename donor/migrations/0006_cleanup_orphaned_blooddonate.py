from django.db import migrations

def forwards_func(apps, schema_editor):
    BloodDonate = apps.get_model('donor', 'BloodDonate')
    Donor = apps.get_model('donor', 'Donor')
    valid_donor_ids = set(Donor.objects.values_list('id', flat=True))
    # Delete orphaned BloodDonate records
    BloodDonate.objects.exclude(donor_id__in=valid_donor_ids).delete()

def reverse_func(apps, schema_editor):
    # No reverse migration
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('donor', '0005_data_migrate_donor_to_profile'),
    ]
    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ] 