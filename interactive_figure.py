#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 16 16:56:56 2021

@author: bdube
"""
import os
import pandas as pd
import geopandas as gpd
from bokeh.plotting import figure, save
from bokeh.models import ColumnDataSource, DataTable, HoverTool, ResetTool, LogColorMapper, ColorBar, BoxZoomTool, PanTool
from bokeh.palettes import  viridis
from bokeh.models import LogColorMapper, Title, Label, LinearColorMapper
from bokeh.io import show
from bokeh.embed import file_html 
from bokeh.resources import CDN



def getPolyCoords(row, geom, coord_type):
    """Returns the coordinates ('x' or 'y') of edges of a Polygon exterior
    From: https://automating-gis-processes.github.io/2017/lessons/L5/interactive-map-bokeh.html
    
    """

    # Parse the exterior of the coordinate
    exterior = row[geom].exterior

    if coord_type == 'x':
        # Get the x coordinates of the exterior
        return list( exterior.coords.xy[0] )
    elif coord_type == 'y':
        # Get the y coordinates of the exterior
        return list( exterior.coords.xy[1] )

def format_dol_val(n):
    n = str(int(n))
    new_string = ''
    for i in range(1, len(n)+1):
        
        new_string +=n[i*-1]
        if i%3 ==0 and i!=len(n):
            new_string+=','
    return '$'+new_string[::-1]

def fix_multipolygon(geom):
    '''Fix a multipolygon shape by iteratively growing the shapes
    and calculating their union until there is only one shape.'''

    new_geom = geom
    i = 1  
    while new_geom.geom_type =='MultiPolygon':
        new_geom = geom.buffer(i).union(geom)
        i+=1
    return new_geom
            
        
if __name__ == '__main__':
    
    
    b_par_path = 'Burlington_parcels'
    if not os.path.exists(b_par_path):
        #filter the parcel shapefile
        btv_map = gpd.read_file('VT_Data_-_Statewide_Standardized_Parcel_Data_-_parcel_polygons')
        btv_map = btv_map[btv_map['TOWN']== 'BURLINGTON']
        
        btv_map.to_file(b_par_path)
        
        
    else: #if it already exists, just load it
        btv_map = gpd.read_file(b_par_path)
        
    #%%
    # make outline of the city of burlignton
    outline = btv_map.dissolve('TOWN')
    outline['x'] = outline.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
    outline['y'] = outline.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)
    
    assess_data = pd.read_csv(
        'All Burlington Taxable properties Reappraisal Value 4.1.2021.csv', 
                         skiprows = 4)
    
    #merge the shapes to the city tax data
    
    btv_map = btv_map.merge(assess_data, 
                            left_on = 'MAPID', right_on =  'ParcelID')
    
    #fix un-plottable geometries
    btv_map = btv_map[btv_map['geometry'].is_valid] 
    btv_map['geometry'] = btv_map['geometry'].apply(fix_multipolygon)
    
    
    btv_map['Percent_change'] =  (btv_map['CurrentAppraisedValue'] / btv_map['PreviousAppraisedValue'] -1) *100
    
    #get x, y coordinates for polygon lines
    btv_map['x'] = btv_map.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
    btv_map['y'] = btv_map.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)
    
    #%%
    btv_map= btv_map[['OBJECTID', 'SPAN', 'GLIST_SPAN', 'MAPID', 'LandUseCode', 'PropertyAddress', 'OwnerName1',
           'OwnerName2', 'OwnerName3', 'StreetAddress1', 'StreetAddress2', 'City',
           'State', 'PostalCode', 'Country', 'PreviousAppraisedValue',
           'CurrentAppraisedValue', 'CurrentAssessedValue', 'Percent_change', 'x', 'y']]
   
    
    #format dollar values as strings
    btv_map['CurrentAppraisedValue'] = btv_map['CurrentAppraisedValue'].apply(format_dol_val)
    btv_map['PreviousAppraisedValue'] = btv_map['PreviousAppraisedValue'].apply(format_dol_val)
    #%%
    
    # convert data into proper form for bokeh:
    parcel_source = ColumnDataSource(btv_map)
    border_source = ColumnDataSource(outline[['x', 'y']])
    
    color_mapper = LinearColorMapper(palette=viridis(100), low = 0, high = 200)
    
    
    display_list = [(n, f'@{n}') for n in ['PropertyAddress','PreviousAppraisedValue',
           'CurrentAppraisedValue', 'Percent_change',
           'LandUseCode', 'OwnerName1']]
    
    #configure tools
    hover = HoverTool(tooltips = display_list)
    zoom = BoxZoomTool()
    pan = PanTool()
    reset = ResetTool()
    
    p = figure(title="Change in Burlington Assessements", 
               tools= [hover, 
                                                                  zoom, pan, reset])
    color_bar = ColorBar(color_mapper=color_mapper, title = 'Percent Increase in Assessment')
    p.add_layout(color_bar, 'below')
    
    #plot town boundary
    p.multi_line('x', 'y', source=border_source, color="k", line_width=2)
    
    #plot parcels
    p.patches('x', 'y', source=parcel_source,
             fill_color={
                 'field': 'Percent_change', 
                 'transform': color_mapper},
             fill_alpha=1.0, line_color="black", line_width=0.05)
    
    
    
   
    outfp = 'btv_reapp1.html'
    
    show(p)
    html = file_html(p, CDN, 'Burlington VT 2021 Reappraisals')
    
    #add annotations to the bottom 
    added_text = ' '.join(['<br>\n<br>\n'
        '\n Download the <a href ="https://github.com/bubalis/btv_grand_list"> code </a> for this visualization from github.',
     '\n<br>\n',
    'Access a <a href ="https://www.burlingtonvt.gov/Assessor/Grand-List"> spreadsheet </a> of the underlying data.',
    '</html>'])
    
    html = html.replace('</html>', added_text)
    with open(outfp, 'w+') as file:
        file.write(html)
        
        
    #save(p, outfp)
    
    
    
    #%%
    