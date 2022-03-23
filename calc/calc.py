from collections import defaultdict

import pandas as pd
import numpy as np
import os
import openpyxl
from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import json
from calc.models import *
import datetime
import itertools
from django.shortcuts import render,redirect

def get_filelocation(**kwargs):
    calculator_directory = kwargs.get('calculator_directory',False)
    filelocation = settings.DATA_FILE_DIR + '/data/'
    filelocation = filelocation.replace("/", "\\")
    if calculator_directory:
        filelocation = settings.DATA_FILE_DIR + '/data/' + calculator_directory + '/'
        filelocation = filelocation.replace("/", "\\")
        if not os.path.exists(filelocation):
            os.makedirs(filelocation)
    return filelocation

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
                    }
    file_data = filter_file and dict(filter(lambda elem: elem[0] in filter_file, file_data.items())) or file_data
    return file_data

def get_filedataframe(**kwargs):
    filelocation = get_filelocation(**kwargs)
    file_data = file_config(**kwargs)
    file_dataframe = {}
    if file_data:
        for file in list(file_data.keys()):
            dataframe_temp = pd.DataFrame({}, columns=file_data.get(file))
            if os.path.exists(filelocation + file +'.csv'):
                dataframe_file = pd.read_csv(filelocation + file +'.csv')
                merge_df = dataframe_temp.merge(dataframe_file, how="outer")[file_data.get(file)]
                merge_df = merge_df.fillna('-')
                file_dataframe[file.lower()] = merge_df
            else:
                file_dataframe[file.lower()] = pd.DataFrame({},columns = file_data.get(file))
    return file_dataframe

def get_duplicate_code(*args):
    res = {}
    match_journal_code = list(map(lambda d: d.get(args[0],False), args[1]))
    if list(filter(lambda x: x != False, match_journal_code)):
        dup_journal_code = match_journal_code and {i:match_journal_code.count(i) for i in match_journal_code} or {}
        cond_check = dup_journal_code and [(i,dup_journal_code[i]) for i in dup_journal_code if dup_journal_code[i] > 1] or []
        cond_check = cond_check and dict(cond_check) or {}
        res = cond_check
    return res

def get_journal_details(**kwargs):
    calculator_id = kwargs.get('calculator_id',False)
    key = kwargs.get('search_key',False)
    journal_obj = JournalMaster.objects.filter(calculator_ids__in=[calculator_id],active=True)
    if key:
        journal_obj = JournalMaster.objects.filter(calculator_ids__in=[calculator_id], code = key, active=True)
    journal_data = journal_obj and journal_obj.values('code', 'name')
    if journal_data:
        return journal_data
    else:
        return redirect('home')

def calculator(*args,**kwargs): # is_inflation=0,is_bypass=0

    # Variable Declaration
    is_inflation = kwargs.get('is_inflation',0)
    is_bypass = kwargs.get('is_bypass',0)
    journal_list = []
    key_list = kwargs.get('journal_code',False) and kwargs.get('journal_code',False) or []
    filelocation = get_filelocation(**kwargs)
    output_dict = {}

    # File Data
    file_data = file_config()

    # Output Data ### Dummy
    output_dict['journal'] = '-'
    output_dict['current_price'] = 0.00
    output_dict['new_price_usd'] = 0.00
    output_dict['new_price_eur'] = 0.00
    output_dict['new_price_gbp'] = 0.00
    if is_bypass:
        output_dict['inf_new_price_usd'] = 0.00
        output_dict['inf_new_price_eur'] = 0.00
        output_dict['inf_new_price_gbp'] = 0.00
    output_dict['price_change'] = 0.00
    output_dict['inflation'] = "{}%".format(0.00)
    output_dict['rev_change'] = 0.00
    output_dict['rev_change_perc'] = "{}%".format(0.00)
    output_dict['vol_change'] = "{}%".format(0.00)
    output_dict['competitor_analysis_adj'] = '-'
    output_dict['sub_rev'] = '-'
    output_dict['corporate_rev'] = '-'
    output_dict['aggressive_price'] = '-'
    corporate_rev,aggressive_price,acronym_finder = "-", "None",""
    if args:
        for code in args:
            journal_list.append(code)
    else:
        journal_list = key_list

    # If file not exists, create dummy dataframe
    kwargs['filter_file'] = ['Journal_Database','Competitor_analysis_adj','Corporate_adj_price','Price_limits_adj_price','Journal_info']
    filedataframe = get_filedataframe(**kwargs)
    journal_database = filedataframe.get('journal_database',False)
    competitor_analysis_adj = filedataframe.get('competitor_analysis_adj',False)
    corporate_adj_price = filedataframe.get('corporate_adj_price',False)
    price_limits_adj_price = filedataframe.get('price_limits_adj_price',False)
    journal_info = filedataframe.get('journal_info',False)

    if journal_list:
        output_dict[journal_list[0]] = False
        result = {elem: True if elem in journal_database.values else False for elem in journal_list}
        if result[journal_list[0]] == False:
            return output_dict
    else:
        return output_dict

    #variant_price
    journal_database = journal_database.loc[journal_database['Journal Code'].isin(journal_list)].to_dict('records')
    journal_database = journal_database and journal_database[0] or journal_database
    journal = journal_database['Journal']
    current_price = journal_database['Current Price (USD)']
    new_price_usd = journal_database['Final Price (USD)']
    new_price_eur = journal_database['Final Price (EUR)']
    new_price_gbp = journal_database['Final Price (GBP)']
    inf_new_price_usd = journal_database['Round Inflation Adjusted Price']
    inf_new_price_eur = journal_database['Round Inflation Adjusted Price (EUR)']
    inf_new_price_gbp = journal_database['Round Inflation Adjusted Price (GBP)']
    rev_change = journal_database['Revenue Change']
    rev_change_perc = journal_database['% Revenue Change']
    vol_change = journal_database['Volume Change']
    sub_rev = journal_database['Price Adjustment Subscription']
    corp_rev = journal_database['Corporate Revenue']
    final_adj = journal_database['Final Adjustment 5']

    #Competitor Analysis note
    competitor_analysis_adj = competitor_analysis_adj.loc[competitor_analysis_adj['name'].isin([journal_database['Competitor Analysis']])].to_dict('records')
    competitor_analysis_adj = competitor_analysis_adj and competitor_analysis_adj[0] or competitor_analysis_adj
    competitor_analysis_adj = competitor_analysis_adj and competitor_analysis_adj['desc'] or ''

    #corporate_rev
    if corporate_adj_price.loc[corporate_adj_price['Warning'] == 'Corporate revenue exceeds', 'Corporate revenue per article'].empty:
        pricing_adjustments = 0.00
    else:
        pricing_adjustments = corporate_adj_price.loc[corporate_adj_price['Warning'] == 'Corporate revenue exceeds', 'Corporate revenue per article'].iloc[0]
    if isinstance(pricing_adjustments,list):
        pricing_adjustments = int(''.join(char for char in pricing_adjustments if char.isalnum()))
    else:
        pricing_adjustments = pricing_adjustments
    if corp_rev > pricing_adjustments:
        corporate_rev = "Corporate revenue per article exceeds $" + str(pricing_adjustments) + " please review."

    #Aggressive Price
    pricing_adjustments = price_limits_adj_price.loc[price_limits_adj_price['Price Limits'] == 'Maximum', 'Price']
    if pricing_adjustments.empty:
        pricing_adjustments = 0.00
    else:
        pricing_adjustments = int(pricing_adjustments)
    if final_adj > pricing_adjustments:
        aggressive_price = final_adj
    output_dict['journal'] = journal
    output_dict['current_price'] = current_price
    output_dict['new_price_usd'] = new_price_usd
    output_dict['new_price_eur'] = new_price_eur
    output_dict['new_price_gbp'] = new_price_gbp
    if is_bypass:
        output_dict['inf_new_price_usd'] = inf_new_price_usd
        output_dict['inf_new_price_eur'] = inf_new_price_eur
        output_dict['inf_new_price_gbp'] = inf_new_price_gbp
    output_dict['price_change'] = new_price_usd - current_price
    output_dict['rev_change'] = rev_change
    output_dict['rev_change_perc'] = "{}%".format(round((rev_change_perc * 100),2))
    output_dict['vol_change'] = "{}%".format(vol_change*100)
    output_dict['competitor_analysis_adj'] = competitor_analysis_adj
    output_dict['competitor_analysis_adj'] = competitor_analysis_adj
    output_dict['sub_rev'] = sub_rev
    output_dict['corporate_rev'] = corporate_rev
    output_dict['aggressive_price'] = aggressive_price
    output_dict[journal_list[0]] = True
    return output_dict

def analysis(**kwargs):
    filelocation = get_filelocation(**kwargs)
    output_dict = {}
    ownership = {
        'headers': ['Ownership:', 'Min of Current Price', 'Min of Proposed Price', 'Max of Current Price','Max of Proposed Price'],
        'rows' : [["J-Joint Owned",2500,250,4800,4900],
                  ["N-Society Owned",1001200,5200,5300],
                  ["O-Proprietary Owned",1500,1800,5000,5100],
                  ["Grand Total",1000,1200,5200,5300]
                  ]
     }
    # File Data
    file_data = {
        'Journal_Database': ['Journal Code', 'Journal','Percentage Change','Ownership Structure','% category','Revenue change']
    }
    journal_database = pd.read_csv(filelocation + 'Journal_Database.csv', usecols=file_data.get('Journal_Database'))
    bau_society_approval_rate = 50
    bau_analysis_data = bau_analysis(journal_database,bau_society_approval_rate)
    output_dict['ownership'] = ownership
    output_dict['bau_analysis_data'] = bau_analysis_data

    print(output_dict)
    return output_dict


def bau_analysis(jd_df,society_approval_rate):
    output_data = {}
    average_prie_increase = (jd_df['Percentage Change'].mean()) * (1 - society_approval_rate)
    output_data['average_prie_increase'] = average_prie_increase

    category = ['1-2%', '3-5%', '6-10%', '11-15%', '16-20%']

    data_unique = pd.Series({c: jd_df[c].dropna().unique() for c in jd_df[['Ownership Structure', '% category']]})
    # print(sorted(data_unique['% category']))

    a = jd_df.groupby(['Ownership Structure', '% category'])['Revenue change'].sum()
    b = jd_df.groupby(['Ownership Structure', '% category']).size().to_frame('Number of journals')
    result = pd.merge(a, b, left_index=True, right_index=True).reset_index()

    # print(result)
    pivot_table = defaultdict(dict)

    for index, row in result.iterrows():
        if row['% category'] in category and row['Ownership Structure'] in data_unique['Ownership Structure']:
            try:
                pivot_table[row['% category']][row['Ownership Structure']]['Revenue change'] = row['Revenue change']
                pivot_table[row['% category']][row['Ownership Structure']]['Number of journals'] = row[
                    'Number of journals']
            except KeyError:
                pivot_table[row['% category']][row['Ownership Structure']] = \
                    {'Revenue change': row['Revenue change'], 'Number of journals': row['Number of journals']}

            pivot_table[row['% category']]['Total Number Of Journal'] = \
                {'Total Number Of Journal': +row['Number of journals']}
            pivot_table[row['% category']]['Total Revenue Changes $'] = \
                {'Total Revenue Changes $': +row['Revenue change']}

            pivot_table['Grand Total'][row['Ownership Structure']] = \
                {'Revenue change': +row['Revenue change'], 'Number of journals': +row['Number of journals']}

    print(pivot_table)

    ownership_table = defaultdict(dict)
    category_separate = '0%'
    sum_noj = 0
    # print(dict(pivot_table))
    for k, v in sorted(pivot_table.items(), reverse=True):
        if k in category:
            for i, j in v.items():
                if i in data_unique['Ownership Structure']:
                    if i == "N-Society Owned":
                        revenue_change = (j.get('Revenue change') * society_approval_rate) / 100
                        no_of_journal = (j.get('Number of journals') * society_approval_rate) / 100

                        sum_noj += j.get('Number of journals')

                        category_separate_noj = (pivot_table['Grand Total'][i]['Number of journals']) - sum_noj
                    else:
                        revenue_change = j.get('Revenue change')
                        no_of_journal = j.get('Number of journals')

                        category_separate_noj = 0

                    ownership_table[k][i] = \
                        {'Revenue change': revenue_change,
                         'Number of journals': no_of_journal}

                    ownership_table[category_separate][i] = \
                        {'Revenue change': 0,
                         'Number of journals': category_separate_noj}

                    ownership_table[k]['Total Number Of Journal'] = \
                        {'Total Number Of Journal': +no_of_journal}
                    ownership_table[k]['Total Revenue Changes $'] = \
                        {'Total Revenue Changes $': +revenue_change}
                    ownership_table[category_separate]['Total Number Of Journal'] = \
                        {'Total Number Of Journal': +category_separate_noj}
                    ownership_table[category_separate]['Total Revenue Changes $'] = \
                        {'Total Revenue Changes $': 0}

                    ownership_table['Grand Total'][i] = \
                        {'Revenue change': +revenue_change, 'Number of journals': +no_of_journal}

    # print(dict(ownership_table))

    ownership = {
        'ownership': {
            'APC change %': {
                'APC change %': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total']
            },
            'N-Society Owned': {
                'Number of journals': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total'],
                'Revenue change $': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total'],
            },
            'J-Joint Owned': {
                'Number of journals': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total'],
                'Revenue change $': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total'],
            },
            'O-Proprietary Owned': {
                'Number of journals': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total'],
                'Revenue change $': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total'],
            },
            'Total Number of journals': {
                'Total Number of journals': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total']
            },
            'Total Revenue change $': {
                'Total Revenue change $': ['0', '1-2%', '3-5%', '6-10%', '11-15%', '16-20%', 'Grand Total']
            }
        }
    }

    output_data['ownership_table'] = ownership_table
    return output_data

### Export Excel to CSV Starts Here ###

def excel_to_csv(excelfile,**kwargs):
    filelocation = get_filelocation(**kwargs)
    xl = pd.ExcelFile(excelfile)
    for sheet in xl.sheet_names:
        if os.path.exists(excelfile):
            df = pd.read_excel(excelfile, sheet_name=sheet)
            df = df.replace({"^\s*|\s*$": ""}, regex=True)
            rows_with_nan = [index for index, row in df.iterrows() if (row.isnull().all())]
            if rows_with_nan:
                df = df.iloc[:min(rows_with_nan)]
            sheet = sheet.replace(" ", "_")
            if os.path.exists(filelocation + sheet + '.csv'):
                os.remove(filelocation + sheet + '.csv')
            df.to_csv(filelocation + sheet + '.csv', index=None, header=True, mode='w+')
    return True

### Export Excel to CSV Ends Here ###

### Import CSV to Database Starts Here ###

def prepare_csv_import_journal(**kwargs):
    filelocation = get_filelocation(**kwargs)
    calculator_id = kwargs.get('calculator_id')
    res_dict = {}
    if os.path.exists(filelocation + "\Journal_Info.csv"):
        JournalInfoDF = pd.read_csv(filelocation + "\Journal_Info.csv")
        journal_code_list = list(JournalInfoDF['Journal Code'])
        calc_sepc_journal_records_one = JournalMaster.objects.filter(code__in=journal_code_list)
        cal_spec_journal_codes = calc_sepc_journal_records_one.values_list('code')
        cal_spec_journal_codes = list(itertools.chain(*cal_spec_journal_codes[::1]))
        JournalInfoDF.drop(JournalInfoDF.index[JournalInfoDF['Journal Code'].isin(cal_spec_journal_codes)], inplace=True)
        JournalInfoDF = JournalInfoDF.rename(columns={'Journal Code': 'code', 'Journal': 'name'})
        now = datetime.datetime.now()
        JournalInfoDF['active'] = True
        JournalInfoDF['created_at'] = now
        JournalInfoDF['modified_at'] = now
        calc_obj = CalculatorMaster.objects.get(pk=calculator_id,active=True)
        for jr in calc_sepc_journal_records_one:
            jr.calculator_ids.add(calc_obj.id)
        res_dict = {'Dataframe': JournalInfoDF, 'tablename': 'journal_master'}
        return res_dict
    return res_dict

def import_csv_database(**kwargs):
    data = prepare_csv_import_journal(**kwargs)
    Dataframe = data.get('Dataframe',False)
    tablename = data.get('tablename',False)
    if (not Dataframe.empty) and tablename:
        from django.db import connection
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        dialect='postgresql'
        db_name = connection.settings_dict['NAME']
        pwd = connection.settings_dict['PASSWORD']
        user = connection.settings_dict['USER']
        host = connection.settings_dict['HOST']
        port = connection.settings_dict['PORT']
        engine = create_engine(f'{dialect}://{user}:{pwd}@{host}:{port}/{db_name}')
        Session = sessionmaker(bind=engine)
        with Session() as session:
            Dataframe.to_sql(tablename, con=engine, if_exists='append', index=False)
        return True
    return False

def create_sample_file(**kwargs):
    filelocation = get_filelocation(**kwargs)
    calculator_id = kwargs.get('calculator_id')
    document_data = {}
    if calculator_id:
        calc_rec = CalculatorMaster.objects.filter(pk=int(calculator_id))
        calc_rec = calc_rec and list(calc_rec) or []
        calc_rec = calc_rec and calc_rec[0] or False
        print(calc_rec)
        document_dynamic_filepath = get_upload_to(calc_rec.directory_name, False)
        new_filepath = os.path.join(settings.MEDIA_ROOT, document_dynamic_filepath)
        print(new_filepath)

    if os.path.exists(filelocation + "\Journal_Database.csv"):
        SampleDF = pd.read_csv(filelocation + "\Journal_Database.csv", nrows=5)

        SampleDF.to_csv(new_filepath + "\Sample_Document.csv", index=False)
        document_data['calculator_id'] = calc_rec
        document_data['document'] = document_dynamic_filepath + "\Sample_Document.csv"
        document_data["name"] = "Sample_Document"
        print(document_data)
        document_rec = Document.objects.create(**document_data)
### Import CSV to Database Ends Here ###

##test
