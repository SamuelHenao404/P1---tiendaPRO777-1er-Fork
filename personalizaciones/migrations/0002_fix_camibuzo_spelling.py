# Generated manually to fix spelling

from django.db import migrations

def fix_camibuzo_spelling(apps, schema_editor):
    """
    Actualiza cualquier registro de PlantillaBase que tenga 'camibuzo' a 'camibuzo'
    """
    PlantillaBase = apps.get_model('personalizaciones', 'PlantillaBase')
    PlantillaBase.objects.filter(tipo='camibuzo').update(tipo='camibuso')

def reverse_fix_camibuzo_spelling(apps, schema_editor):
    """
    Función reversa para deshacer el cambio si es necesario
    """
    PlantillaBase = apps.get_model('personalizaciones', 'PlantillaBase')
    PlantillaBase.objects.filter(tipo='camibuzo').update(tipo='camibuso')

class Migration(migrations.Migration):

    dependencies = [
        ('personalizaciones', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(
            fix_camibuzo_spelling,
            reverse_fix_camibuzo_spelling,
        ),
    ]
