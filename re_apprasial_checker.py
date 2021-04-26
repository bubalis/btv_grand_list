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


def fix_multipolygon(geom):
    new_geom = geom
    i = 1  
    while new_geom.geom_type =='MultiPolygon':
        new_geom = geom.buffer(i).union(geom)
        i+=1
    return new_geom
            
        

b_par_path = 'Burlington_parcels'
if not os.path.exists(b_par_path):
    gdf = gpd.read_file('VT_Data_-_Statewide_Standardized_Parcel_Data_-_parcel_polygons')
    gdf = gdf[gdf['TOWN']== 'BURLINGTON']
    
    gdf.to_file(b_par_path)
else:
    gdf = gpd.read_file(b_par_path)
    
#%%
outline = gdf.dissolve('TOWN')
outline['x'] = outline.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
outline['y'] = outline.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)

df = pd.read_csv('All Burlington Taxable properties Reappraisal Value 4.1.2021.csv', 
                     skiprows = 4)

gdf = gdf.merge(df, left_on = 'MAPID', right_on =  'ParcelID')
gdf = gdf[gdf['geometry'].is_valid]
gdf['geometry'] = gdf['geometry'].apply(fix_multipolygon)

gdf['Percent_change'] =  (gdf['CurrentAppraisedValue'] / gdf['PreviousAppraisedValue'] -1) *100



gdf['x'] = gdf.apply(getPolyCoords, geom='geometry', coord_type='x', axis=1)
gdf['y'] = gdf.apply(getPolyCoords, geom='geometry', coord_type='y', axis=1)

#%%
g_gdf = gdf[['OBJECTID', 'SPAN', 'GLIST_SPAN', 'MAPID', 'LandUseCode', 'PropertyAddress', 'OwnerName1',
       'OwnerName2', 'OwnerName3', 'StreetAddress1', 'StreetAddress2', 'City',
       'State', 'PostalCode', 'Country', 'PreviousAppraisedValue',
       'CurrentAppraisedValue', 'CurrentAssessedValue', 'Percent_change', 'x', 'y']]
#%%
def format_dol_val(n):
    n = str(int(n))
    new_string = ''
    for i in range(1, len(n)+1):
        
        new_string +=n[i*-1]
        if i%3 ==0 and i!=len(n):
            new_string+=','
    return '$'+new_string[::-1]
    #%%


g_gdf['CurrentAppraisedValue'] = g_gdf['CurrentAppraisedValue'].apply(format_dol_val)
g_gdf['PreviousAppraisedValue'] = g_gdf['PreviousAppraisedValue'].apply(format_dol_val)
#%%
gsource = ColumnDataSource(g_gdf)
osource = ColumnDataSource(outline[['x', 'y']])

color_mapper = LinearColorMapper(palette=viridis(100), low = 0, high = 200)

display_list = [(n, f'@{n}') for n in ['PropertyAddress','PreviousAppraisedValue',
       'CurrentAppraisedValue', 'Percent_change',
       'LandUseCode', 'OwnerName1']]

#add ts
hover = HoverTool(tooltips = display_list)
zoom = BoxZoomTool()
pan = PanTool()
reset = ResetTool()
p = figure(title="Change in Burlington Assessements", tools= [hover, 
                                                              zoom, pan, reset])
color_bar = ColorBar(color_mapper=color_mapper, title = 'Percent Increase in Assessment')
p.add_layout(color_bar, 'below')


p.multi_line('x', 'y', source=osource, color="k", line_width=2)
p.patches('x', 'y', source=gsource,
         fill_color={'field': 'Percent_change', 'transform': color_mapper},
         fill_alpha=1.0, line_color="black", line_width=0.05)

msg = 'Download the code for this visualization at https://github.com/bubalis/btv_grand_list'
caption = Title(text=msg)
p.add_layout(caption, 'below')

outfp = 'btv_reapp1.html'

show(p)
save(p, outfp)



#%%
'''
homes = ['R1 - Single Fam', 'R2 - 2 Family', 'R3 - 3 Family',
       'R4 - 4 Family']
ax = outline.plot(color = 'w', edgecolor = 'k')
gdf[gdf['LandUseCode'].isin(homes)].query('0<Percent_change <200').plot('Percent_change', legend = True, ax = ax,
                        legend_kwds={'label': "% Increase in Assessment",}
                        )
ax.axis('off')
#%%





dfh = df[df['LandUseCode'].isin(homes)]
dfh['PreviousAppraisedValue ($1000s)'] =  dfh['PreviousAppraisedValue']/1000
dfh['CurrentAppraisedValue ($1000s)'] =  dfh['CurrentAppraisedValue']/1000
sns.scatterplot('PreviousAppraisedValue ($1000s)', 'CurrentAppraisedValue ($1000s)', data = dfh,  
                hue = 'LandUseCode')
(dfh['CurrentAppraisedValue']/ dfh['PreviousAppraisedValue']).mean()'''