from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_original', models.CharField(max_length=20, unique=True, verbose_name='ID original')),
                ('nombre', models.CharField(max_length=200, verbose_name='Nombre')),
            ],
            options={
                'verbose_name': 'Empleado',
                'verbose_name_plural': 'Empleados',
                'db_table': 'empleados',
                'ordering': ['nombre'],
            },
        ),
    ]
