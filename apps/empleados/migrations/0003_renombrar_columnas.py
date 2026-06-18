from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('empleados', '0002_cargar_empleados'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE empleados DROP INDEX raw_id",
            reverse_sql="ALTER TABLE empleados ADD UNIQUE INDEX raw_id (id_original)",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE empleados CHANGE COLUMN raw_id id_original VARCHAR(20) NOT NULL",
            reverse_sql="ALTER TABLE empleados CHANGE COLUMN id_original raw_id VARCHAR(20) NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE empleados CHANGE COLUMN name nombre VARCHAR(200) NOT NULL",
            reverse_sql="ALTER TABLE empleados CHANGE COLUMN nombre name VARCHAR(200) NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE empleados ADD UNIQUE INDEX id_original (id_original)",
            reverse_sql="ALTER TABLE empleados DROP INDEX id_original",
        ),
    ]
