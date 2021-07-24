from django.db import models
from  django.contrib.auth.models import User
from django.db.models.deletion import CASCADE

class Users(models.Model):
    UserName = models.CharField(max_length=50, primary_key=True)
    Password = models.CharField(max_length=30)
    FullName = models.CharField(max_length=80)
    Email = models.EmailField(max_length=50)
    SDATE = models.DateTimeField()

class DB_DataSource(models.Model):
    Host = models.CharField(max_length=100)
    Port = models.IntegerField()
    DataBase = models.CharField(max_length=50)
    User = models.CharField(max_length=50)
    Password = models.CharField(max_length=30)
    Max_Opens = models.IntegerField()
    Max_Idels = models.IntegerField()
    Max_Lifetime = models.IntegerField()
    

class Api_DataSource(models.Model):
    URL = models.CharField(max_length=100)
    Access = models.CharField(max_length=50)
    Basic_Auth = models.BooleanField()
    TLS_Client_Auth = models.BooleanField()
    Skip_TLS_verify = models.BooleanField()
    Forward_OAuth_identity = models.BooleanField()
    With_Credentials = models.BooleanField()
    With_CA_Cert = models.BooleanField()
    UserName = models.CharField(max_length=50)
    Password = models.CharField(max_length=30)
    Trends = models.BooleanField()
    After = models.IntegerField()
    Range = models.IntegerField()
    Cache_TTL = models.IntegerField()
    Direct_DB_Connection = models.BooleanField()
    Alerting = models.BooleanField()

class DataSources(models.Model):
    Name = models.CharField(max_length=60)
    Type = models.CharField(max_length=60)
    DB_DataSource = models.ForeignKey(DB_DataSource, on_delete=models.CASCADE, null=True)
    Api_DataSource = models.ForeignKey(Api_DataSource, on_delete=models.CASCADE, null=True)

class Dashboard(models.Model):
    Title = models.CharField(max_length= 80)

class Panels(models.Model):
    PanelName = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    SDATE = models.DateTimeField()
    DashboardId = models.IntegerField()
    ChartType = models.CharField(max_length=50, null=True)

class Panel_DataSources(models.Model):
    PanelId = models.IntegerField()
    DataSourceId = models.IntegerField()
    Query = models.CharField(max_length=300) 

class Variables(models.Model):
    Name = models.CharField(max_length=50)
    Type = models.CharField(max_length=50)
    Lable = models.CharField(max_length=50)
    Hide = models.CharField(max_length=20)
    Description = models.CharField(max_length=100)
    VariableScope = models.CharField(max_length=20)
    PanelId = models.IntegerField()
    DataSourceId = models.IntegerField()
    Refresh = models.CharField(max_length=30)
    Query = models.CharField(max_length=300)
    Regex = models.CharField(max_length=200)
    Sort = models.CharField(max_length=50)
    MultiValue = models.BooleanField()
    IncludeAllOptions = models.BooleanField()
    ValueGroupTag = models.BooleanField()
    CustomValues = models.CharField(max_length=100)
    TextboxValues = models.CharField(max_length=80)
    ConstantValue = models.CharField(max_length=80)
    InstanceNameFilter = models.CharField(max_length=80)
    IntervalValues = models.CharField(max_length=100)
    IntervalAutoOption = models.BooleanField()
    