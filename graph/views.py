from RightelGraph.settings import TIME_ZONE
from django.shortcuts import render, redirect, reverse
from graph.models import Panel_DataSources, Users, Panels, DataSources, DB_DataSource, Api_DataSource, Dashboard, Variables
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.views.generic.base import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from  django.contrib.auth.models import User
from django.utils import timezone
from django.http import HttpResponse
import sqlalchemy
from sqlalchemy   import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import URL
import cx_Oracle
import pymssql
from pyzabbix.api import ZabbixAPI
from sqlalchemy import text
import datetime 
import random
import time
import json
from json import JSONEncoder
from django.db import transaction, DatabaseError
import os


try:
    engine = sqlalchemy.create_engine("sqlite:///:memory:")
    # print ("ssssssssssssssss", sessionmaker(bind=engine)())
    ds = DataSources.objects.all()
    engines = []
    sessions = []
    for dbconninfo in ds:
        connectionString = ""
        if dbconninfo.DB_DataSource_id != None :
            if dbconninfo.Type == "PostgreSQL":
                driver = 'postgresql+psycopg2'
                url = URL(driver, dbconninfo.DB_DataSource.User, dbconninfo.DB_DataSource.Password, dbconninfo.DB_DataSource.Host, dbconninfo.DB_DataSource.Port, dbconninfo.DB_DataSource.DataBase)
            elif dbconninfo.Type == "MySQL":
                driver = 'postgresql+psycopg2'
                url = URL(driver, dbconninfo.DB_DataSource.User, dbconninfo.DB_DataSource.Password, dbconninfo.DB_DataSource.Host, dbconninfo.DB_DataSource.Port, dbconninfo.DB_DataSource.DataBase)
            elif dbconninfo.Type == "Oracle":
                driver = 'oracle'
                url = URL(driver, dbconninfo.DB_DataSource.User, dbconninfo.DB_DataSource.Password, dbconninfo.DB_DataSource.Host, dbconninfo.DB_DataSource.Port, dbconninfo.DB_DataSource.DataBase)
            elif dbconninfo.Type == "SqlServer":
                driver = 'mssql+pymssql'
                url = URL(driver, dbconninfo.DB_DataSource.User, dbconninfo.DB_DataSource.Password, dbconninfo.DB_DataSource.Host, dbconninfo.DB_DataSource.Port, dbconninfo.DB_DataSource.DataBase)

            engine = create_engine(url)
            engines.append(engine)
            sessions.append(sessionmaker(bind=engine)())
            
        else:
            zabbix_url = dbconninfo.Api_DataSource.URL
            # with ZabbixAPI(url=zabbix_url, user=dbconninfo.Api_DataSource.UserName, password=dbconninfo.Api_DataSource.Password) as zapi:
            #     result1 = zapi.host.get(monitored_hosts=1, output='extend')
                # print("hhhhhh", result1)
except DatabaseError:
    transaction.rollback()
    
# print("sdddfd", sessions)
Flag = False
def login(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if request.POST.get("UserName") != '':
            userName = request.POST.get("UserName")
        else:
            err = "Please insert your UserName!!"

        if request.POST.get("Password") != '':
            password = request.POST.get("Password")
        else:
            err = "Please insert your Password!!"

        user = Users.objects.filter(UserName=userName, Password=password)
        if form.is_valid():
            return redirect('dashboard/')
    else:
        form = AuthenticationForm()
        return render(request, 'login.html', {'form': form})



class indexView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/index.html'
    def get(self, request):
        dashboards = Dashboard.objects.all()
        return render(request, 'accounts/index.html',{'dashboards': dashboards})

    def post(self, request):
        DashboardTitle = request.POST.get("DashboardTitle")
        dashboard = Dashboard(Title=DashboardTitle)
        dashboard.save()
        return render(request, 'accounts/index.html') 

    def delete_dashboard(request, id=None):
        dashboard= Dashboard.objects.get(id= id)
        dashboard.delete()
        return redirect(reverse('index'))

class my_dictionary(dict): 
    def __init__(self): 
        self = dict() 

    def add(self, key, value): 
        self[key] = value 

class dashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/dashboard.html'
    
    def get(self, request):
        data={}
        try:
            request.session['dashId'] = request.GET.get("DashboardId")   
            panels = Panels.objects.filter(DashboardId= request.session['dashId'])
            variables = Variables.objects.all()
            datasource = DataSources.objects.all()
            var_dic = my_dictionary() 
            panel_dic = my_dictionary()
            for v in variables:
                
                if v.Type == "Query":
                    var_dic.key = v.Type
                    for session in sessions:
                        aa = session.execute(text(v.Query))
                        query_val = aa.fetchall()
                        var_dic.value = query_val
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    
                elif v.Type == "Custom":
                    var_dic.key = v.Type
                    custom_val = v.CustomValues
                    custom_values = custom_val.split(",")
                    var_dic.value = custom_values
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    
                elif v.Type == "Textbox":
                    var_dic.key = v.Type
                    var_dic.value = v.TextboxValues
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    
                elif v.Type == "Constant":
                    var_dic.key = v.Type
                    var_dic.value = v.ConstantValue
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    
                elif v.Type == "Datasource":
                    var_dic.key = v.Type
                    var_dic.value = v.DataSourceId
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    
                elif v.Type == "Interval":
                    var_dic.key = v.Type
                    var_dic.value = v.IntervalValues
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    
                elif v.Type == "Adhocfilters":
                    var_dic.key = v.Type
                    var_dic.value = v.DataSourceId
                    if v.Type not in var_dic:
                        var_dic[var_dic.key] = []
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])
                    else:
                        var_dic[var_dic.key].append([var_dic.value, v.Lable, v.PanelId, v.MultiValue])

            lcharttype = ''
            bcharttype = ''
            bchartdata = {}
            lchartdata = {}
            xdate = []
            counter = []
            counter2 = []
            for p in panels:
                panel_ds = Panel_DataSources.objects.filter(PanelId = p.id)
                for p_ds in panel_ds:
                    panel_dic.key = p_ds.id
                    panel_dic[panel_dic.key] = []
                    if p.ChartType == 'BarChart':
                        """
                        discretebarchart page
                        """

                        ds_id = p_ds.DataSourceId
                        ds = DataSources.objects.filter(id=ds_id)
                        for dd in ds:
                            db_ds_id = dd.DB_DataSource_id                       
                        db_ds = DB_DataSource.objects.filter(id = db_ds_id)
                        for dss in db_ds:
                            db_host = dss.Host
                        
                        for session in sessions:
                            ds_url = str(session.get_bind())
                            ds_url = ds_url.split('@')
                            ds_url = ds_url[1].split(':')
                            if ds_url[0] == db_host:
                                print("sdf", ds_url[0])
                                query = session.execute(text(panel_ds[0].Query))
                                query_val = query.fetchall()
                                # graphDate = list(query_val[2])
                                for i in query_val:
                                    xdate.append(i[0])
                                    counter.append(i[1])
                                # print('queryyy', counter[0])
                                xdata = xdate
                                ydata = counter

                                extra_serie1 = {"tooltip": {"y_start": "", "y_end": " cal"}}
                                bchartdata = {
                                    'x': xdata, 'name1': '', 'y1': ydata, 'extra1': extra_serie1,
                                }
                                bcharttype = "discreteBarChart"

                                panel_dic[panel_dic.key].append([bchartdata, bcharttype])

                    elif p.ChartType == 'LineChart':
                        """
                        lineChart page
                        """
                        ds_id = p_ds.DataSourceId
                        ds = DataSources.objects.filter(id=ds_id)
                        for dd in ds:
                            db_ds_id = dd.DB_DataSource_id                       
                        db_ds = DB_DataSource.objects.filter(id = db_ds_id)
                        for dss in db_ds:
                            db_host = dss.Host
                        
                        for session in sessions:
                            ds_url = str(session.get_bind())
                            ds_url = ds_url.split('@')
                            ds_url = ds_url[1].split(':')
                            if ds_url[0] == db_host:
                                query2 = session.execute(text(panel_ds[0].Query))
                                query_val2 = query2.fetchall()
                                # print('queryyy', query_val)
                                for i in query_val2:
                                    counter2.append(i[0])
                                nb_element = 100
                                start_time = int(time.mktime(datetime.datetime(2020, 12, 1).timetuple()))
                                xdata = range(len(counter2))
                                xdata = [i * start_time * 1000000000 for i in xdata]
                                
                                ydata = counter2
                                # ydata2 = counter2
                                
                                tooltip_date = '%Y-%m-%d %H:%M:%S'
                                extra_serie = {"tooltip": {"y_start": "", "y_end": " cal"},
                                    "date_format": tooltip_date}
                                    

                                lchartdata = {'x': xdata, 'name1': 'data 1', 'y1': ydata, 'extra1': extra_serie}
                                lcharttype = "lineChart"
                                panel_dic[panel_dic.key].append([lchartdata, lcharttype])
            data = {
                'panel_dict': panel_dic,
                'panels': panels, 
                'variables_dict': var_dic, 
                'datasources': datasource
            } 
            return render(request, 'accounts/dashboard.html',data)
        except:
            session.rollback()
            return render(request, 'chart.html',data)
            
            # return render(request, 'chart.html')

    def post(self, request):
        panelName = request.POST.get("panelName")
        dashboardId = request.session['dashId']
        chartType = request.POST.get("ChartType")
        DatasourceId = request.POST.getlist('DatasourceId')
        
        panel = Panels(SDATE=timezone.now(), PanelName=panelName, user=request.user, DashboardId= dashboardId, ChartType=chartType)
        panel.save()
        panelid = panel.id
        Query = request.POST.get("query")
        # input_names = [(name,v) for name,v in request.POST.keys() if name.startswith('query')]
        # for input_name in input_names.v:
        #     soft_name = request.POST[input_name]
            
        
        inputs = [(n, v) for n, v in request.POST.items() if n.startswith('query')]
        
        for ds_id in range(len(DatasourceId)):
            for q in inputs:
                query_name = q[0]
                query_value = q[1]
                query_id = query_name[:-1].split('[')
                # print("nasssss", DatasourceId[ds_id])
                if query_id[1] == DatasourceId[ds_id]:
                    panel_datasource = Panel_DataSources(PanelId= panelid, DataSourceId= DatasourceId[ds_id], Query= query_value)
                    panel_datasource.save()
        return redirect('/accounts/dashboard?DashboardId='+dashboardId)

    def delete_panel(request, id=None):
        dashboardId = request.session['dashId']
        panel= Panels.objects.get(id= id)
        panel.delete()
        return redirect('/accounts/dashboard?DashboardId='+dashboardId)

class settingsView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/settings.html'

class configurationView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/configuration.html'
    def get(self, request):
        dataSources = DataSources.objects.all()
        return render(request, 'accounts/configuration.html',{'dataSources': dataSources})

    def delete_datasource(request, id=None):
        datasource= DataSources.objects.get(id= id)
        datasource.delete()
        return redirect(reverse('configuration'))

def Add_DataSource(request):
    DataSourceName = request.POST.get("DataSourceName")
    DataSourceType = request.POST.get("DataSourceType")
    if DataSourceType != "Zabbix":
        Host = request.POST.get("Host")
        Port = request.POST.get("Port")
        DataBase = request.POST.get("DataBase")
        DB_User = request.POST.get("DB_User")
        DB_Password = request.POST.get("DB_Password")
        Max_opens = request.POST.get("Max_opens")
        Max_idels = request.POST.get("Max_idels")
        Max_lifetime = request.POST.get("Max_lifetime")
        db_datasource = DB_DataSource(Host=Host, DataBase=DataBase, User=DB_User, Password=DB_Password, Max_Opens=Max_opens, Max_Idels=Max_idels, Max_Lifetime=Max_lifetime, Port=Port)
        datasource = DataSources(Name=DataSourceName, Type=DataSourceType, DB_DataSource=db_datasource)
        db_datasource.save()
        datasource.save()
    else:
        URL = request.POST.get("URL")
        Access = request.POST.get("Access")
        if request.POST.get("Basic_Auth") == "on":
            Basic_Auth = True
        else:
            Basic_Auth = False
        if request.POST.get("TLS_Client_Auth") == "on":
            TLS_Client_Auth = True
        else:
            TLS_Client_Auth = False
        if request.POST.get("Skip_TLS_verify") == "on":
            Skip_TLS_verify = True
        else:
            Skip_TLS_verify = False
        if request.POST.get("Forward_OAuth_identity") == "on":
            Forward_OAuth_identity = True
        else:
            Forward_OAuth_identity = False
        if request.POST.get("With_Credentials") == "on":
            With_Credentials = True
        else:
            With_Credentials = False
        if request.POST.get("With_CA_Cert") == "on":
            With_CA_Cert = True
        else:
            With_CA_Cert = False

        Api_UserName = request.POST.get("Api_UserName")
        Api_Password = request.POST.get("Api_Password")

        if request.POST.get("Trends") == "on":
            Trends = True
        else:
            Trends = False
        After = request.POST.get("After")
        Range = request.POST.get("Range")
        Cache_TTL = request.POST.get("Cache_TTL")

        if request.POST.get("Direct_DB_Connection") == "on":
            Direct_DB_Connection = True
        else:
            Direct_DB_Connection = False
        if request.POST.get("Alerting") == "on":
            Alerting = True
        else:
            Alerting = False
        api_datasource = Api_DataSource(URL=URL, Access=Access, Basic_Auth=Basic_Auth, TLS_Client_Auth=TLS_Client_Auth,
                                        Skip_TLS_verify=Skip_TLS_verify, Forward_OAuth_identity=Forward_OAuth_identity,
                                        With_Credentials= With_Credentials, With_CA_Cert=With_CA_Cert, UserName=Api_UserName,
                                        Password=Api_Password, Trends= Trends, After=After, Range=Range, Cache_TTL=Cache_TTL,
                                        Direct_DB_Connection=Direct_DB_Connection, Alerting=Alerting)
        datasource = DataSources(Name=DataSourceName, Type=DataSourceType, Api_DataSource=api_datasource)
        api_datasource.save()
        datasource.save()

    return render(request, 'accounts/configuration.html',{'datasource': datasource}) 
        
class variablesView(LoginRequiredMixin, TemplateView):
    template_name = 'accounts/variables.html'
    def get(self, request):
        dataSources = DataSources.objects.all()
        panels = Panels.objects.all()
        variables = Variables.objects.all()
        data = {
            'dataSources': dataSources,
            'panels': panels,
            'variables': variables
        }

        return render(request, 'accounts/variables.html', data)


    def post(self, request):
        Var_Name = request.POST.get("Name")
        VariableType = request.POST.get("VariableType")
        Lable = request.POST.get("Lable")
        Hide = request.POST.get("Hide")
        Description = request.POST.get("Description")
        VariableScope = request.POST.get("VariableScope")
        PanelName = request.POST.get("PanelName")     
        QueryDatasource = request.POST.get("QueryDatasource")
        Refresh = request.POST.get("Refresh")
        Query = request.POST.get("Query")
        Regex = request.POST.get("Regex")
        SortType = request.POST.get("SortType")
        if request.POST.get("ValueGroupTag") == "on":
            ValueGroupTag =  True
        else:
            ValueGroupTag =  False
        if request.POST.get("MultiValue") == "on":
            MultiValue =  True
        else:
            MultiValue =  False
        if request.POST.get("IncludeAllOption") == "on":
            IncludeAllOption =  True
        else:
            IncludeAllOption =  False
         
        CustomValues = request.POST.get("CustomValues")
        TextboxValue = request.POST.get("TextboxValue")
        ConstantValue = request.POST.get("ConstantValue")
        DatasourceType = request.POST.get("DatasourceType")
        InstanceNameFilter = request.POST.get("InstanceNameFilter")
        IntervalValue = request.POST.get("IntervalValue")
        if request.POST.get("AutoOption") == "on":
            AutoOption =  True
        else:
            AutoOption =  False
        adhocDataSource = request.POST.get("adhocDataSource")

        variable = Variables(Name= Var_Name, Type= VariableType, Lable= Lable, Hide= Hide, Description= Description, 
                            VariableScope= VariableScope, PanelId= PanelName, DataSourceId= QueryDatasource, Refresh= Refresh, 
                            Query= Query, Regex= Regex, Sort= SortType, MultiValue= MultiValue, IncludeAllOptions=IncludeAllOption, 
                            ValueGroupTag= ValueGroupTag, CustomValues= CustomValues, TextboxValues= TextboxValue, ConstantValue= ConstantValue, 
                            InstanceNameFilter= InstanceNameFilter, IntervalValues= IntervalValue, IntervalAutoOption=AutoOption)

        variable.save()
        return redirect('/accounts/settings/variables')

    def delete_variable(request, id=None):
        variable= Variables.objects.get(id= id)
        variable.delete()
        return redirect(reverse('variables'))

def demo_discretebarchart(request):
    start_time = int(time.mktime(datetime.datetime(2012, 6, 1).timetuple()) * 1000)
    nb_element = 100
    xdata = range(nb_element)
    xdata = [i * start_time * 1000000000 for i in xdata]
    ydata = [i + random.randint(1, 10) for i in range(nb_element)]
    ydata2 = [i + random.randint(1, 10) for i in reversed(range(nb_element))]
    ydata3 = [i * 3 for i in ydata]
    ydata4 = [i * 4 for i in ydata]
    kwargs1 = {}
    kwargs1['bar'] = True

    tooltip_date = "%d %b %Y %H:%M:%S %p"
    extra_serie1 = {"tooltip": {"y_start": "$ ", "y_end": ""},
                    "date_format": tooltip_date}
    extra_serie2 = {"tooltip": {"y_start": "", "y_end": " min"},
                    "date_format": tooltip_date}

    chartdata = {
        'x': xdata,
        'name1': 'series 1', 'y1': ydata, 'extra1': extra_serie1, 'kwargs1': kwargs1,
        'name2': 'series 2', 'y2': ydata2, 'extra2': extra_serie2,
    }

    charttype = "linePlusBarChart"
    data = {
        'charttype': charttype,
        'chartdata': chartdata,
        'extra': {
            'focus_enable': True,}
    }
    return render(request,'chart.html', data)

# class DateTimeEncoder(JSONEncoder):
#         #Override the default method
#         def default(self, obj):
#             if isinstance(obj, (datetime.date, datetime.datetime)):
#                 return obj.isoformat()