#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 16 11:26:08 2021

@author: bdube
"""
import os
import pdfminer
import PyPDF2
import fitz
import re
import pandas as pd
#%%
file = open('Grand List Tax Book FY2021 printed 8.6.2020.pdf', 'rb')

pdf = PyPDF2.PdfFileReader(file)

file.close()


def parse_page(text):
    out_data = []
    items = re.split('[-+]{5,}', text)
    for i, item in enumerate(items[1:]):
        print(i)
        if item.strip():
            out_data.append(parse_entry(item))
       
    return out_data

regex = re.compile(r'\||(\s{25,})')

def parse_entry(item):
    out = {}
    lines = item.split('\n')
    rows = [regex.split(line) for line in lines]
    col1 = [row[0].strip() for row in rows]
    other_cols = [row[1:] for row in rows if len(row)>1]
    other_cols = [x for y in other_cols for x in y if x]
    
    out = dict(Owner = col1[1], 
                id_1 = col1[6], prop_address = col1[-5], 
                span = col1[-3].replace('SPAN:', '').strip(),
                id_2 = col1[-2],
                )
    try:
        out['Zoning'] = out['id_2'].split()[-2]
        out['Not sure about this column'] = out['id_2'].split()[-1]
    except:
        print(out['id_2'])
        print(col1)
        print(item)
        raise
        
    address_lines = ['owner street or mail', 'owner city', 
                     'owner state', 'owner zip', 'property_manager']
    address_string = '\n'.join(col1[2:7])
    try:
        out.update({k: v for k, v in zip(address_lines, 
                                     get_biz_address(address_string))})
    except:
        print(address_string)
        raise
    
    for name in ['NONHOMESTEAD', 'LOCAL AGREEME', 'REAL', 'MUNICIPAL', 'TOTAL TAX',
                 'MISCELLANEOUS FEE', 'GRAND LIST', 'TOTAL ACREAGE', 'HOMESTEAD', 
                 'MUN. HOUSESITE TAX', 'ED. HOUSESITE TAX', 'TOT HOUSE. TAX']:
    
        matches = [col for col in other_cols if name in col]
        if matches:
            try:
                out[name] = re.search('[\d\.,]+', matches[0]).group()
            except:
                print(matches[0])
                raise
        else:
            out[name] = ''
    
    return out
        
def get_biz_address(address):
    lines = [l for l in address.split('\n') if l]
    if re.search('(\s|^)(C\/O)(\s|$)', lines[0]) or re.search('^(CO)(\s|$)', lines[0]):
        prop_mgr = lines[0].replace('C/O', '').strip()
        lines = lines[1:]
    else:
        prop_mgr = None
    
    stre_or_mail = lines[0]
    
    for line in lines: 
        if re.search('\d{5}', line):
            
            zip_code =  re.search('[\d|-]+', line).group()
            city_state = line.replace(zip_code, '').strip()
            state = city_state.split()[-1]
            city = city_state.replace(state, '').strip()
            return stre_or_mail,  city, state, zip_code, prop_mgr
    else:
        try:
            line = lines[-2]
            return stre_or_mail, line[0], line[1], line[2], prop_mgr
        except:
            return ["Could not Parse"]*5




if __name__ == '__main__':
    with fitz.open('Grand List Tax Book FY2021 printed 8.6.2020.pdf') as doc:
        out_data = []
        for i in range(0, len(doc), 2): 
            print(f'Page {i}')
            if i>=len(doc)-1:
                break
            text = doc[i].getText()+doc[i+1].getText()
            parsed_data = parse_page(text)
            for record in parsed_data:
                record['page'] = i
            out_data += parsed_data

    df = pd.DataFrame(out_data)

    df.to_csv('BTV_grand_list.csv')
