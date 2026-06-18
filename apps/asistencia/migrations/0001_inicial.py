from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('empleados', '0002_cargar_empleados'),
    ]

    operations = [
        migrations.CreateModel(
            name='RegistroAcceso',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('marcado_en', models.DateTimeField(verbose_name='Fecha/Hora')),
                ('datos_originales', models.TextField(blank=True, verbose_name='Línea original')),
                ('serial_dispositivo', models.CharField(blank=True, max_length=50, verbose_name='Serial del dispositivo')),
                ('creado_en', models.DateTimeField(auto_now_add=True, verbose_name='Recibido el')),
                ('empleado', models.ForeignKey(on_delete=models.CASCADE, related_name='registros', to='empleados.Empleado', verbose_name='Empleado')),
            ],
            options={
                'verbose_name': 'Registro de acceso',
                'verbose_name_plural': 'Registros de acceso',
                'db_table': 'registros_acceso',
                'ordering': ['-marcado_en'],
            },
        ),
        migrations.AddIndex(
            model_name='registroacceso',
            index=models.Index(fields=['empleado', 'marcado_en'], name='registros_a_emplead_2ddde8_idx'),
        ),
        migrations.AddConstraint(
            model_name='registroacceso',
            constraint=models.UniqueConstraint(fields=['empleado', 'marcado_en'], name='unq_empleado_marcado_en'),
        ),
    ]
