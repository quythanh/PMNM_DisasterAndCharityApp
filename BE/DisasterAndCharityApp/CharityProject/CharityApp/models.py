from datetime import datetime
from idlelib.pyparse import trans

from cloudinary.models import CloudinaryField
from django.contrib.auth.models import AbstractUser
from django.db import models
from datetime import date
from django_enumfield import  enum

# Create your models here.
#ENUM
class UserRole(enum.Enum):
    CIVILIAN = 0
    CHARITY_ORG = 1
    ADMIN = 2

class ContentPictureType(enum.Enum):
    CONTENT = 0
    RESULT = 1

class LocationState(enum.Enum):
    NORMAL = 0
    PANDEMIC = 1
    DISASTER = 2



#CLASS MODELS
class BaseModel(models.Model):
    class Meta:
        abstract = True

    id = models.AutoField(primary_key=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

class User(AbstractUser):
    birthdate = models.DateField(null=False, default=date(2024, 1, 1))
    address = models.CharField(max_length=100, null=False, default='ABC')
    gender = models.BooleanField(null=False, default=True)
    avatar = CloudinaryField('image', default= None, null=True)
    role = enum.EnumField(UserRole, default=UserRole.CIVILIAN)
    bank = models.CharField(max_length=100, default="Vietcombank")
    bank_id = models.CharField(max_length=20, default="12345678910")

    @property
    def name(self):
        return self.last_name + ' ' + self.first_name

    @property
    def image_url(self):
        return self.avatar.url

class Civilian (models.Model):
    user_info = models.OneToOneField(User,related_name="civilian_info",on_delete=models.CASCADE, primary_key=True, null=False)
    money = models.IntegerField(default=0)

class Admin (models.Model):
    user_info = models.OneToOneField(User,related_name="admin_info",on_delete=models.CASCADE, primary_key=True, null=False)

    def __str__(self):
        return self.user_info.username

class CharityOrg (models.Model):
    user_info = models.OneToOneField(User,related_name="charity_org_info",on_delete=models.CASCADE, primary_key=True, null=False)
    is_verified = models.BooleanField(default=False)
    civilian_id = models.CharField(max_length=15)
    civilian_id_date = models.DateField()
    badge = models.ForeignKey('Badge', related_name='orgs', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user_info.username;
class Chat (BaseModel):
    civilian = models.ForeignKey(Civilian,on_delete=models.CASCADE, null= False, related_name="chat")
    org = models.ForeignKey(CharityOrg, on_delete=models.CASCADE, null= False, related_name="chat")
    firebase_id = models.CharField(max_length=20, null= False)

class Badge (BaseModel):
    tittle = models.CharField(max_length=100)
    condition = models.CharField(max_length=100)

class DonationPost(BaseModel):
    civilian = models.ForeignKey(Civilian, on_delete=models.CASCADE, related_name="posts")
    content = models.TextField()
    supply_type = models.ForeignKey("SupplyType", on_delete=models.CASCADE, related_name="posts", default=1)

class DonationPostPicture(BaseModel):
    post = models.ForeignKey(DonationPost, on_delete=models.CASCADE, related_name="pictures")
    picture = CloudinaryField('image', default= None, null=True)

class DonationPostApproval(models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='confirmed_post')
    post = models.OneToOneField(DonationPost, on_delete=models.CASCADE, primary_key=True)
    priority = models.IntegerField(default= 1)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

class DonationCampaign (BaseModel):
    org = models.ForeignKey(CharityOrg, on_delete=models.CASCADE, null=False, related_name="campaign")
    title = models.CharField(max_length=50, default="ABC")
    content = models.TextField()
    supply_type = models.ForeignKey("SupplyType", on_delete=models.CASCADE, related_name="campaigns", default=1)
    expected_charity_start_date = models.DateField()
    expected_charity_end_date = models.DateField()
    is_permitted = models.BooleanField(default=False)
    enclosed_article = models.ManyToManyField('Article', related_name='enclosed')

class DonationReport(BaseModel):
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE)
    total_used = models.IntegerField()
    total_left = models.IntegerField(default=0)

class DonationReportPicture(BaseModel):
    report = models.ForeignKey(DonationReport, related_name="pictures", on_delete=models.CASCADE)
    path = models.CharField(max_length=20)

class DetailDonationReport(BaseModel):
    report = models.OneToOneField(DonationReport, related_name="details", on_delete=models.CASCADE)
    paid_for = models.CharField(max_length=100)
    paid = models.IntegerField()

class ContentPicture (BaseModel):
    donation = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE, null=False, related_name="pictures")
    type = enum.EnumField(ContentPictureType, default=ContentPictureType.CONTENT)
    path = CloudinaryField('image', default= None, null=True)

class SupplyType (BaseModel):
    type = models.CharField(max_length=10)
    unit = models.CharField(max_length=10, default="Kg")
    
    def __str__(self):
        return f'{self.type} ({self.unit})'

class CampaignLocation (BaseModel):
    class Meta:
        unique_together = ['campaign', 'location']
    campaign = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE, related_name="locations")
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name="campaigns")
    expected_fund = models.IntegerField()
    current_fund = models.IntegerField(default=0)

class Storage (BaseModel):
    address = models.CharField(max_length=100)
    location = models.ForeignKey('Location', on_delete=models.CASCADE, related_name="storage")
class Stock (BaseModel):
    type = models.ForeignKey(SupplyType, related_name='stocks', null=False, on_delete=models.CASCADE)
    amount = models.IntegerField()
    wareHouse = models.ForeignKey(Storage,on_delete= models.CASCADE, null=False,related_name="stock")

class Approval (BaseModel):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name= 'approvals')
    donation = models.ForeignKey(DonationCampaign, on_delete=models.CASCADE)
    time_id = models.IntegerField(null=False, default=1)
    is_approved = models.BooleanField(null=True)
    is_final = models.BooleanField(default=False)

class Confimation (models.Model):
    admin = models.ForeignKey(Admin, on_delete=models.CASCADE, related_name='confirmed')
    report = models.OneToOneField(DonationReport, on_delete=models.CASCADE, primary_key=True)
    created_date = models.DateField(auto_now_add=True)
    updated_date = models.DateField(auto_now=True)
    active = models.BooleanField(default=True)

class Donation (BaseModel):
    civilian = models.ForeignKey(Civilian, on_delete=models.CASCADE, null=False, related_name="donated")
    campaign = models.ForeignKey(CampaignLocation, on_delete=models.CASCADE, null=False, related_name="donated")
    donated = models.IntegerField()

class Article (BaseModel):
    title = models.CharField(max_length=100)
    brief = models.TextField()
    real_path = models.CharField(max_length=100)

# class Comment (BaseModel):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     article = models.ForeignKey(Article, on_delete=models.CASCADE)
#     level = models.IntegerField(default=1)
#     content = models.CharField(max_length=100)
#
# class Reply (models.Model):
#     comment = models.OneToOneField(Comment, on_delete=models.CASCADE, primary_key=True, null=False, related_name='reply')
#     parent = models.OneToOneField(Comment, on_delete=models.CASCADE, null=False, related_name='childs')

class Location (BaseModel):
    location = models.CharField(max_length=45, unique=True)
    area = models.IntegerField(default = 1)
    current_status = enum.EnumField(LocationState, default=LocationState.NORMAL)

class StatInfo (BaseModel):
    location = models.ForeignKey(Location, related_name='stat_history', on_delete=models.CASCADE)
    status = enum.EnumField(LocationState, default=LocationState.NORMAL)
    label = models.CharField(max_length=40)
    number = models.FloatField()

class CompanySetting(BaseModel):
    topic = models.CharField(max_length=20)
    title = models.CharField(max_length=100)
    type = enum.EnumField(LocationState, default=LocationState.DISASTER)
    primary_color = models.CharField(max_length=20)
    secondary_color = models.CharField(max_length=20)
    button_color = models.CharField(max_length=20)
    log_color = models.CharField(max_length=20)
    logo = models.CharField(max_length=20)
    stat_data_source = models.CharField(max_length= 100)
    is_chosen = models.BooleanField(default=False)
