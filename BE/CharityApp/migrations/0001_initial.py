# Generated by Django 5.1.3 on 2024-12-03 09:33

import CharityApp.models
import cloudinary.models
import datetime
import django.contrib.auth.models
import django.contrib.auth.validators
import django.db.models.deletion
import django.utils.timezone
import django_enumfield.db.fields
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('birthdate', models.DateField(default=datetime.date(2024, 1, 1))),
                ('address', models.CharField(default='ABC', max_length=100)),
                ('gender', models.BooleanField(default=True)),
                ('avatar', cloudinary.models.CloudinaryField(default=None, max_length=255, null=True, verbose_name='image')),
                ('role', django_enumfield.db.fields.EnumField(default=0, enum=CharityApp.models.UserRole)),
                ('bank', models.CharField(default='Vietcombank', max_length=100)),
                ('bank_id', models.CharField(default='12345678910', max_length=20)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(max_length=100)),
                ('brief', models.TextField()),
                ('real_path', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Badge',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('tittle', models.CharField(max_length=100)),
                ('condition', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CompanySetting',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('topic', models.CharField(max_length=20)),
                ('title', models.CharField(max_length=100)),
                ('type', django_enumfield.db.fields.EnumField(default=2, enum=CharityApp.models.LocationState)),
                ('primary_color', models.CharField(max_length=20)),
                ('secondary_color', models.CharField(max_length=20)),
                ('button_color', models.CharField(max_length=20)),
                ('log_color', models.CharField(max_length=20)),
                ('logo', models.CharField(max_length=20)),
                ('stat_data_source', models.CharField(max_length=100)),
                ('is_chosen', models.BooleanField(default=False)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DonationReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('total_used', models.IntegerField()),
                ('total_left', models.IntegerField(default=0)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DonationCampaign',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('title', models.CharField(default='ABC', max_length=50)),
                ('content', models.TextField()),
                ('expected_charity_start_date', models.DateField()),
                ('expected_charity_end_date', models.DateField()),
                ('is_permitted', models.BooleanField(default=False)),
                ('enclosed_article', models.ManyToManyField(related_name='enclosed', to='CharityApp.article')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DonationPost',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('content', models.TextField()),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('location', models.CharField(max_length=45, unique=True)),
                ('area', models.IntegerField(default=1)),
                ('current_status', django_enumfield.db.fields.EnumField(default=0, enum=CharityApp.models.LocationState)),
                ('latitude', models.DecimalField(decimal_places=6, default=0.0, max_digits=9)),
                ('longitude', models.DecimalField(decimal_places=6, default=0.0, max_digits=9)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='SupplyType',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('type', models.CharField(max_length=10)),
                ('unit', models.CharField(default='Kg', max_length=10)),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('user_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='admin_info', serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='CharityOrg',
            fields=[
                ('user_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='charity_org_info', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('is_verified', models.BooleanField(default=False)),
                ('civilian_id', models.CharField(max_length=15)),
                ('civilian_id_date', models.DateField()),
                ('badge', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='orgs', to='CharityApp.badge')),
            ],
        ),
        migrations.CreateModel(
            name='Civilian',
            fields=[
                ('user_info', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='civilian_info', serialize=False, to=settings.AUTH_USER_MODEL)),
                ('money', models.IntegerField(default=0)),
            ],
        ),
        migrations.CreateModel(
            name='DetailDonationReport',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('paid_for', models.CharField(max_length=100)),
                ('paid', models.IntegerField()),
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='details', to='CharityApp.donationreport')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='donationreport',
            name='campaign',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CharityApp.donationcampaign'),
        ),
        migrations.CreateModel(
            name='ContentPicture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('type', django_enumfield.db.fields.EnumField(default=0, enum=CharityApp.models.ContentPictureType)),
                ('path', cloudinary.models.CloudinaryField(default=None, max_length=255, null=True, verbose_name='image')),
                ('donation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='CharityApp.donationcampaign')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DonationPostPicture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('picture', cloudinary.models.CloudinaryField(default=None, max_length=255, null=True, verbose_name='image')),
                ('post', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='CharityApp.donationpost')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DonationReportPicture',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('path', models.CharField(max_length=20)),
                ('report', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pictures', to='CharityApp.donationreport')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='CampaignLocation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('expected_fund', models.IntegerField()),
                ('current_fund', models.IntegerField(default=0)),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='locations', to='CharityApp.donationcampaign')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='CharityApp.location')),
            ],
            options={
                'unique_together': {('campaign', 'location')},
            },
        ),
        migrations.CreateModel(
            name='StatInfo',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('status', django_enumfield.db.fields.EnumField(default=0, enum=CharityApp.models.LocationState)),
                ('label', models.CharField(max_length=40)),
                ('number', models.FloatField()),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stat_history', to='CharityApp.location')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Storage',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('address', models.CharField(max_length=100)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='storage', to='CharityApp.location')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Stock',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('amount', models.IntegerField()),
                ('wareHouse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stock', to='CharityApp.storage')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='stocks', to='CharityApp.supplytype')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='donationpost',
            name='supply_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='CharityApp.supplytype'),
        ),
        migrations.AddField(
            model_name='donationcampaign',
            name='supply_type',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, related_name='campaigns', to='CharityApp.supplytype'),
        ),
        migrations.CreateModel(
            name='Approval',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('time_id', models.IntegerField(default=1)),
                ('is_approved', models.BooleanField(null=True)),
                ('is_final', models.BooleanField(default=False)),
                ('donation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='CharityApp.donationcampaign')),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='approvals', to='CharityApp.admin')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AddField(
            model_name='donationcampaign',
            name='org',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='campaign', to='CharityApp.charityorg'),
        ),
        migrations.AddField(
            model_name='donationpost',
            name='civilian',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='CharityApp.civilian'),
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('donated', models.IntegerField()),
                ('campaign', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donated', to='CharityApp.campaignlocation')),
                ('civilian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='donated', to='CharityApp.civilian')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Chat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('firebase_id', models.CharField(max_length=20)),
                ('org', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat', to='CharityApp.charityorg')),
                ('civilian', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='chat', to='CharityApp.civilian')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Confimation',
            fields=[
                ('report', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='CharityApp.donationreport')),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmed', to='CharityApp.admin')),
            ],
        ),
        migrations.CreateModel(
            name='DonationPostApproval',
            fields=[
                ('post', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='CharityApp.donationpost')),
                ('priority', models.IntegerField(default=1)),
                ('created_date', models.DateField(auto_now_add=True)),
                ('updated_date', models.DateField(auto_now=True)),
                ('active', models.BooleanField(default=True)),
                ('admin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='confirmed_post', to='CharityApp.admin')),
            ],
        ),
    ]
