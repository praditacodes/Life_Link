from django.db import migrations

def forwards_func(apps, schema_editor):
    Patient = apps.get_model('patient', 'Patient')
    Profile = apps.get_model('accounts', 'Profile')
    CustomUser = apps.get_model('blood', 'CustomUser')

    for patient in Patient.objects.all():
        profile, created = Profile.objects.get_or_create(
            user_id=patient.user_id,
            defaults={
                'profile_pic': patient.profile_pic,
                'blood_group': patient.bloodgroup,
                'age': patient.age,
                'address': patient.address,
                'phone': patient.mobile,
                'city': patient.city,
                'state': patient.state,
                'pincode': patient.pincode,
                'latitude': patient.latitude,
                'longitude': patient.longitude,
                'cause': patient.cause,
                'can_donate': False,
                'can_receive': True,
            }
        )
        # If already exists, update fields
        if not created:
            profile.profile_pic = patient.profile_pic
            profile.blood_group = patient.bloodgroup
            profile.age = patient.age
            profile.address = patient.address
            profile.phone = patient.mobile
            profile.city = patient.city
            profile.state = patient.state
            profile.pincode = patient.pincode
            profile.latitude = patient.latitude
            profile.longitude = patient.longitude
            profile.cause = patient.cause
            profile.can_receive = True
            profile.save()

def reverse_func(apps, schema_editor):
    # No reverse migration
    pass

class Migration(migrations.Migration):
    dependencies = [
        ('patient', '0002_remove_patient_disease_patient_cause'),
        ('accounts', '0003_remove_profile_doctorname'),
    ]

    operations = [
        migrations.RunPython(forwards_func, reverse_func),
    ] 