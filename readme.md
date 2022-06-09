This repo contains projects related to Burlington VT property assessments. 

Primarily, it contains the code to make the data visualization found here: https://bubalis.github.io/btv_reappraisal.html 

The newspaper Seven Days eventually made a much slicker version of this visualization (see here: https://www.sevendaysvt.com/vermont/burlingtons-property-reassessment-has-set-record-high-values-whats-the-cost-to-residents/Content?oid=32909386)
but I beat them to it by several weeks!



The script grand_list_parser.py parses a pdf table version on the grand list (all the assessed propery values in the city) to extract it into a csv file.

The script interactive_figure.py builds an interactive bokeh figure of Burlington re-appraisal data.


To run this the reappraisal script, you need to download parcel data from vermont open geodata. 
From this url:
https://geodata.vermont.gov/datasets/e12195734d38410185b3e4f1f17d7de1_17?geometry=-80.786%2C42.478%2C-64.098%2C45.249

And unzip it into a folder called VT_Data_-_Statewide_Standardized_Parcel_Data_-_parcel_polygons.

https://opendata.arcgis.com/datasets/e12195734d38410185b3e4f1f17d7de1_17.zip?geometry=%7B%22xmin%22%3A-80.786%2C%22ymin%22%3A42.478%2C%22xmax%22%3A-64.098%2C%22ymax%22%3A45.249%2C%22type%22%3A%22extent%22%2C%22spatialReference%22%3A%7B%22wkid%22%3A4326%7D%7D&outSR=%7B%22latestWkid%22%3A32145%2C%22wkid%22%3A32145%7D
