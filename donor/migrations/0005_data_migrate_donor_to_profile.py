from django.db import migrations

def forwards_func(apps, schema_editor):
    Donor = apps.get_model('donor', 'Donor')
    Profile = apps.get_model('accounts', 'Profile')
    BloodDonate = apps.get_model('donor', 'BloodDonate')
    CustomUser = apps.get_model('blood', 'CustomUser')

    # Create Profile for each Donor if not exists
    for donor in Donor.objects.all():
        profile, created = Profile.objects.get_or_create(
            user_id=donor.user_id,
            defaults={
                'profile_pic': donor.profile_pic,
                'blood_group': donor.bloodgroup,
                'age': donor.age,
                'address': donor.address,
                'phone': donor.mobile,
                'city': donor.city,
                'state': donor.state,
                'pincode': donor.pincode,
                'latitude': donor.latitude,
                'longitude': donor.longitude,
                'can_donate': True,
                'can_receive': True,
            }
        )
        # Update BloodDonate to point to Profile
        for donation in BloodDonate.objects.filter(donor_id=donor.id):
            donation.donor_id = profile.id
            donation.save()

def reverse_func(apps, schema_editor):
    # No reverse migration
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('donor', '0003_remove_blooddonate_disease_blooddonate_cause_and_more'),
        ('accounts', '0003_remove_profile_doctorname'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ] 