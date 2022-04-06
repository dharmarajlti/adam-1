from collections import defaultdict

import pandas as pd
import numpy as np
import os
import openpyxl
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import json
from .models import *
import datetime
import itertools
from django.shortcuts import render,redirect
from django.db import connection
cursor = connection.cursor()


def file_config(**kwargs):
    filter_file = kwargs.get('filter_file',[])
    file_data = {
                    'Journal_Database'          : ['Journal Code','Journal','Current Price (USD)',
                                                    'Final Price (USD)','Round Inflation Adjusted Price',
                                                    'Final Price (EUR)','Round Inflation Adjusted Price (EUR)',
                                                    'Final Price (GBP)','Round Inflation Adjusted Price (GBP)',
                                                    'Revenue Change','% Revenue Change','Volume Change',
                                                    'Competitor Analysis','Price Adjustment Subscription',
                                                    'Corporate Revenue','Final Adjustment 5','Percentage Change','Ownership Structure','% category', 'Revenue change'],
                    'Competitor_analysis_adj'   : ['name','desc'], # Competitor_analysis_adj
                    'Corporate_adj_price'       : ['Corporate revenue per article','Warning'],
                    'Price_limits_adj_price'    : ['Price Limits','Price'],
                    'Journal_Info'              : ['Journal Code','Journal'],
                    'All_Panels': ['Market', 'Panel#', 'dbl_lat', 'dbl_lng', 'Status', 'Installed On', 'Retirement Date'],
                    'Inv_Static': ['Number', 'Number (Site)', 'City (Site)', 'Installed On', 'Retired On', 'Media type',
                                   'Unit type', '4 Wk Imp', 'Size', 'Submarket (Classification)', 'Full', 'Description'],
                    'Inv_Players': ['Player', 'Site #', 'Description', 'City', 'Active On', 'Retired On',
                                    '4 Wk Imp', 'Size', 'Submarket', 'Saleable Spots', 'Code', 'Description'],
                    'Reservations': ['From', 'To', 'Salesperson (Subcontract: Contract)', 'Contract Type',
                                     'Contract Number (Subcontract)', 'Advertiser (Subcontract: Contract)',
                                     'Subcontract Type (Subcontract)', 'Player (Location)', 'Segment',
                                     'Weekdays', 'Spots', 'Value', 'Signed On (Subcontract: Contract)',
                                     'Contract Date Check', 'AE#', 'Player Number', 'Segment Name'],
                    'Market_Code': ['market', 'code']
                    }
    file_data = filter_file and dict(filter(lambda elem: elem[0] in filter_file, file_data.items())) or file_data
    return file_data


def excel_to_csv(excelfile,**kwargs):
    import numpy
    # excelfile = 'D:\LTI Work\Documents\Adams\All_panels_attributes_input.xlsx'
    xl = pd.ExcelFile(excelfile)
    # sheet_list = ['All Panels','Inv Static','Inv Players','Reservations','Market Code']
    for sheet in xl.sheet_names:
        fsheet = sheet.replace(" ", "_")
        kwargs['filter_file'] = [fsheet]
        file_data = file_config(**kwargs)
        file_columns = file_data and file_data.get(fsheet) or []
        if os.path.exists(excelfile):
            tablename = False
            df = pd.read_excel(excelfile, sheet_name=sheet, usecols=file_columns)
            df = df.replace({"^\s*|\s*$": ""}, regex=True)
            rows_with_nan = [index for index, row in df.iterrows() if (row.isnull().all())]
            if rows_with_nan:
                df = df.iloc[:min(rows_with_nan)]
            sheet = sheet.replace(" ", "_")
            if sheet == 'All_Panels':
                columns_rename = {'Market': 'market_name',
                                  'Panel#': 'panel_no',
                                  'dbl_lat': 'latitude',
                                  'dbl_lng': 'longitude',
                                  'Status': 'status',
                                  'Installed On': 'installed_date_str',
                                  'Retirement Date': 'retirement_date_str'}
                df.rename(columns=columns_rename, inplace=True)
                df['latitude'] = df['latitude'].replace(np.nan, 0.00, regex=True)
                df['longitude'] = df['longitude'].replace(np.nan, 0.00, regex=True)
                df['installed_date_str'] = df['installed_date_str'].replace(np.NaN, '', regex=True)
                df['retirement_date_str'] = df['retirement_date_str'].replace(np.NaN, '', regex=True)
                tablename = 'adam_panelmaster'
            if sheet == 'Inv_Static':
                columns_rename = {'Number' : 'player_no',
                                  'Number (Site)' : 'site',
                                  'City (Site)' : 'city',
                                  'Installed On' : 'installed_date_str',
                                  'Retired On' : 'retirement_date_str',
                                  'Media type' : 'media_type',
                                  'Unit type' : 'unit_type',
                                  '4 Wk Imp' : 'wk4_imp',
                                  'Size' : 'size',
                                  'Submarket (Classification)' : 'submarket',
                                  'Full' : 'code',
                                  'Description' : 'description'}
                df.rename(columns = columns_rename, inplace = True)
                tablename = 'adam_panelstaticdetails'
            if sheet == 'Inv_Players':
                columns_rename = {'Player' : 'player_no',
                                  'Site #' : 'site',
                                  'Description' :	'description',
                                  'City' : 'city',
                                  'Active On' : 'installed_date_str',
                                  'Retired On' : 'retirement_date_str',
                                  '4 Wk Imp' : 'wk4_imp',
                                  'Size' : 'size',
                                  'Submarket' : 'submarket',
                                  'Saleable Spots' : 'sales_spot',
                                  'Code' : 'code'}
                df.rename(columns=columns_rename, inplace=True)
                tablename = 'adam_panelplayerdetails'
            if sheet == 'Reservations':
                columns_rename = {'From': 'from_date_str',
                                  'To': 'to_date_str',
                                  'Salesperson (Subcontract: Contract)': 'sales_person',
                                  'Contract Type': 'contract_type',
                                  'Contract Number (Subcontract)': 'contract_no',
                                  'Advertiser (Subcontract: Contract)': 'advertiser',
                                  'Subcontract Type (Subcontract)': 'sub_contract_type',
                                  'Player (Location)': 'panel_no',
                                  'Segment': 'segment',
                                  'Weekdays': 'weekdays',
                                  'Spots': 'spots',
                                  'Value': 'value',
                                  'Signed On (Subcontract: Contract)': 'contract_sign_date_str',
                                  'Contract Date Check': 'contract_date_check',
                                  'AE#': 'ae_no',
                                  'Player Number': 'player_no',
                                  'Segment Name': 'segment_name', }
                df.rename(columns=columns_rename, inplace=True)
                df['spots'] = df['spots'].replace(np.nan, 0, regex=True)
                df['value'] = df['value'].replace(np.nan, 0.00, regex=True)
                df['contract_date_check'] = df['contract_date_check'].replace(np.nan, 0, regex=True)
                tablename = 'adam_reservation'
            if sheet == 'Market_Code':
                columns_rename = {'code': 'code',
                                  'market': 'market'}
                df.rename(columns=columns_rename, inplace=True)
                tablename = 'adam_marketmaster'
            df.drop_duplicates(inplace=True)
            ### Starts Here ###
            from django.db import connection
            from sqlalchemy import create_engine
            from sqlalchemy.orm import sessionmaker
            dialect = 'postgresql'
            db_name = connection.settings_dict['NAME']
            pwd = connection.settings_dict['PASSWORD']
            user = connection.settings_dict['USER']
            host = connection.settings_dict['HOST']
            port = connection.settings_dict['PORT']
            engine = create_engine(f'{dialect}://{user}:{pwd}@{host}:{port}/{db_name}')
            Session = sessionmaker(bind=engine)
            with Session() as session:
                if tablename:
                    df.to_sql(tablename, con=engine, if_exists='append', index=False)
            from django.contrib.gis.geos.point import Point
            if sheet == 'All_Panels':
                q = '''select panel.id, panel.latitude, panel.longitude from adam_panelmaster as panel left join adam_spatialpoint as point on panel.id = point.panelmaster_id'''
                cursor.execute(q)
                add_list = []
                for c in cursor.fetchall():
                    point = Point((c[2], c[1]), srid=4326)
                    # s = SpatialPoint.objects.create(points=point, panelmaster=PanelMaster.objects.get(id=c[0]))
                    # s.save()
                    obj = SpatialPoint(points=point, panelmaster=PanelMaster.objects.get(id=c[0]))
                    add_list.append(obj)
                SpatialPoint.objects.bulk_create(add_list)
            ### Ends Here ###
    return True