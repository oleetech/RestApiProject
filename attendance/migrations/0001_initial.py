# Generated by Django 5.0.6 on 2024-10-18 12:12

import django.core.validators
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AttendanceLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('punch_datetime', models.DateTimeField(default=django.utils.timezone.now, verbose_name='Date & Time of Punch')),
                ('in_out_status', models.CharField(choices=[('IN', 'Check-In'), ('OUT', 'Check-Out'), ('BREAK_IN', 'Break-In'), ('BREAK_OUT', 'Break-Out')], default='IN', max_length=20, verbose_name='In/Out Status')),
                ('verification_method', models.CharField(choices=[('FP', 'Fingerprint'), ('FACE', 'Face'), ('CARD', 'Card'), ('PWD', 'Password'), ('GPS', 'GPS'), ('MANUAL', 'Manual')], default='FP', max_length=10, verbose_name='Verification Method')),
                ('punch_mode', models.CharField(choices=[('AUTO', 'Auto'), ('MANUAL', 'Manual')], default='AUTO', max_length=10, verbose_name='Punch Mode')),
                ('work_code', models.CharField(blank=True, max_length=20, null=True, verbose_name='Work Code')),
                ('sync', models.BooleanField(default=False)),
                ('locationName', models.CharField(blank=True, max_length=255, null=True)),
                ('latitude', models.FloatField(blank=True, null=True)),
                ('longitude', models.FloatField(blank=True, null=True)),
                ('createdAt', models.DateTimeField(auto_now_add=True)),
                ('updatedAt', models.DateTimeField(auto_now=True)),
            ],
            options={
                'verbose_name': 'Attendance Log',
                'verbose_name_plural': 'Attendance Logs',
                'ordering': ['-punch_datetime'],
            },
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_id', models.CharField(max_length=50, unique=True)),
                ('location', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=255, null=True)),
                ('ip_address', models.GenericIPAddressField(blank=True, null=True)),
                ('last_sync_time', models.DateTimeField(blank=True, null=True)),
                ('serial_number', models.CharField(max_length=255, null=True, unique=True)),
                ('port', models.IntegerField(default=4370)),
            ],
            options={
                'verbose_name': 'Device',
                'verbose_name_plural': 'Devices',
                'ordering': ['-last_sync_time'],
            },
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_id', models.CharField(max_length=20, verbose_name='Employee ID')),
                ('first_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='First Name')),
                ('last_name', models.CharField(blank=True, max_length=50, null=True, verbose_name='Last Name')),
                ('department', models.CharField(blank=True, max_length=50, null=True, verbose_name='Department name')),
                ('position', models.CharField(blank=True, max_length=50, null=True, verbose_name='Position title')),
                ('contact_number', models.CharField(blank=True, max_length=15, null=True, verbose_name='Contact number')),
                ('gender', models.CharField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], default='M', max_length=1)),
                ('bloodGroup', models.CharField(blank=True, choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], max_length=3, null=True)),
                ('religion', models.CharField(blank=True, choices=[('Christianity', 'Christianity'), ('Islam', 'Islam'), ('Hinduism', 'Hinduism'), ('Buddhism', 'Buddhism'), ('Sikhism', 'Sikhism'), ('Judaism', 'Judaism'), ('Other', 'Other')], max_length=20, null=True)),
                ('maritalStatus', models.CharField(blank=True, choices=[('Single', 'Single'), ('Married', 'Married'), ('Divorced', 'Divorced'), ('Widowed', 'Widowed')], max_length=10, null=True)),
                ('date_of_joining', models.DateField(blank=True, null=True, verbose_name='Date of joining')),
                ('email', models.EmailField(blank=True, max_length=255, null=True, verbose_name='Email Address')),
                ('date_of_birth', models.DateField(blank=True, null=True, verbose_name='Date of Birth')),
            ],
            options={
                'verbose_name': 'Employee',
                'verbose_name_plural': 'Employees',
                'ordering': ['date_of_joining'],
            },
        ),
        migrations.CreateModel(
            name='EmployeeDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_name', models.CharField(max_length=100)),
                ('document_type', models.CharField(choices=[('Resume', 'Resume'), ('Contract', 'Contract'), ('ID Card', 'ID Card'), ('Other', 'Other')], max_length=20)),
                ('upload_date', models.DateTimeField(auto_now_add=True)),
                ('document_file', models.FileField(upload_to='employee_documents/', validators=[django.core.validators.FileExtensionValidator(allowed_extensions=['pdf', 'docx', 'jpg', 'png'])])),
            ],
        ),
        migrations.CreateModel(
            name='Holiday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('reason', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Schedule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('break_duration', models.DurationField(blank=True, null=True)),
                ('status', models.CharField(choices=[('ACTIVE', 'Active'), ('INACTIVE', 'Inactive')], default='ACTIVE', max_length=10)),
            ],
            options={
                'verbose_name': 'Shift',
                'verbose_name_plural': 'Shifts',
                'ordering': ['start_time'],
            },
        ),
        migrations.CreateModel(
            name='TemporaryShift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
            ],
        ),
        migrations.CreateModel(
            name='Workday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('day', models.CharField(choices=[('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'), ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday'), ('SUN', 'Sunday')], max_length=10)),
            ],
        ),
        migrations.CreateModel(
            name='WorkHours',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('total_hours', models.DurationField()),
                ('overtime_hours', models.DurationField(blank=True, null=True)),
            ],
        ),
    ]
