from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('asistencia', '0001_inicial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso DROP FOREIGN KEY attendance_scanrecor_employee_id_ef474cfc_fk_employees",
            reverse_sql="ALTER TABLE registros_acceso ADD CONSTRAINT attendance_scanrecor_employee_id_ef474cfc_fk_employees FOREIGN KEY (employee_id) REFERENCES empleados(id)",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso DROP INDEX unq_employee_scanned_at",
            reverse_sql="ALTER TABLE registros_acceso ADD CONSTRAINT unq_employee_scanned_at UNIQUE (employee_id, scanned_at)",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso DROP INDEX registros_a_employe_2ddde8_idx",
            reverse_sql="ALTER TABLE registros_acceso ADD INDEX registros_a_employe_2ddde8_idx (employee_id, scanned_at)",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso CHANGE COLUMN employee_id empleado_id BIGINT NOT NULL",
            reverse_sql="ALTER TABLE registros_acceso CHANGE COLUMN empleado_id employee_id BIGINT NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso CHANGE COLUMN scanned_at marcado_en DATETIME(6) NOT NULL",
            reverse_sql="ALTER TABLE registros_acceso CHANGE COLUMN marcado_en scanned_at DATETIME(6) NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso CHANGE COLUMN raw_data datos_originales LONGTEXT NOT NULL",
            reverse_sql="ALTER TABLE registros_acceso CHANGE COLUMN datos_originales raw_data LONGTEXT NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso CHANGE COLUMN device_sn serial_dispositivo VARCHAR(50) NOT NULL",
            reverse_sql="ALTER TABLE registros_acceso CHANGE COLUMN serial_dispositivo device_sn VARCHAR(50) NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso CHANGE COLUMN created_at creado_en DATETIME(6) NOT NULL",
            reverse_sql="ALTER TABLE registros_acceso CHANGE COLUMN creado_en created_at DATETIME(6) NOT NULL",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso ADD INDEX registros_a_emplead_2ddde8_idx (empleado_id, marcado_en)",
            reverse_sql="ALTER TABLE registros_acceso DROP INDEX registros_a_emplead_2ddde8_idx",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso ADD CONSTRAINT unq_empleado_marcado_en UNIQUE (empleado_id, marcado_en)",
            reverse_sql="ALTER TABLE registros_acceso DROP INDEX unq_empleado_marcado_en",
        ),
        migrations.RunSQL(
            sql="ALTER TABLE registros_acceso ADD CONSTRAINT registros_acceso_empleado_id_fk_empleados_id FOREIGN KEY (empleado_id) REFERENCES empleados(id)",
            reverse_sql="ALTER TABLE registros_acceso DROP FOREIGN KEY registros_acceso_empleado_id_fk_empleados_id",
        ),
    ]
