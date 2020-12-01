import sys, os, requests, csv
from numpy.core.numeric import NaN
from numpy.lib.function_base import append
import pandas as pd
import numpy as np
import geopandas as gpd
#-------------------------------------------------------
'''
Project Plan
1.) Download covid data and fsa data
2.) Clean prep and aggegate covid data
3.) join cleaned data to FSA data and neighborhood data and geography the data that way
3.) join additional data to the new data (population, etc)
'''
#-------------------------------------------------------
#Functions
def download_csv(CSV_URL):
    # Returns a pandas dataframe from a link to a csv.
    with requests.Session() as s:
        download = s.get(CSV_URL)

        decoded_content = download.content.decode('utf-8')

        cr = csv.reader(decoded_content.splitlines(), delimiter=',')
        my_list = list(cr)
        column_names = my_list[0]
        my_list.remove(column_names)
        df = pd.DataFrame(my_list, columns= column_names)
        return df
def caseCounter(neighbourhoodName, casesDF):
    count = len(case_df.loc[case_df.Neighbourhood_Name == neighbourhoodName])
    return count

def sortByColumn(df, sort_col):
    # Sorts a df by a column by extracting the first letter of a string and sorting by that letter
    df['sort'] = df[sort_col].str.extract('(\d+)', expand=False)
    df = df.sort_values('sort', ascending=False)
    df = df.drop('sort', axis=1)
    return df
#-------------------------------------------------------
# Inputs
dataPath = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=csv'
nProfilesCSV = r'H:\TorontoCOVID_FSA\data\neighbourhood-profiles-2016-csv.csv'
neighbourhoods_json = r'H:\TorontoCOVID_FSA\data\Neighbourhoods.geojson'
outFolder = r'H:\TorontoCOVID_FSA\data'

#-------------------------------------------------------
#Logic

#Restructure Neighbourhood Profile data in pandas as it comes in a non-useful format
nProfiles = pd.read_csv(nProfilesCSV)
nProfiles = nProfiles.T #Transposes columns into rows and vice versa
nProfiles = nProfiles[4:]#Remove useless columns
nProfiles = nProfiles.drop(nProfiles.index[1]) # Remove Toronto wide data as we don't need it for the map

nProfiles.columns = list(nProfiles.iloc[0]) # Set column names to the first row
nProfiles.drop(['Characteristic'], inplace= True)
nProfiles['Index'] = np.array(range(0,len(nProfiles)))
nProfiles = nProfiles.reset_index().set_index('Index')
nProfiles.rename(columns={'index': 'Neighbourhood_Name'}, inplace= True)

#Download COVID data and convert it into a pandas dataframe
#Commented out for testing
# print('Downloading TO case data from source')
# case_df = download_csv(dataPath)
# case_df.to_csv(os.path.join(outFolder, 'case_df.csv'))
case_df = pd.read_csv(os.path.join(outFolder, 'case_df.csv'))
# casesByN = pd.DataFrame(list(nProfiles.Neighbourhood_Name), columns= ['Neighbourhood Name'])
# casesByN['Total Case Count'] = [len(case_df.loc[case_df['Neighbourhood Name'] == x]) for x in list(casesByN['Neighbourhood Name'])]

#Loop over case data by neighborhood and get counts
field_names = ['Neighbourhood_Name', 'Total_Case_Count']
out_rows = []
nh = case_df['Neighbourhood Name'].unique().tolist() # Get all unique N's
nh = [h for h in nh if str(h) != 'nan'] # Remove the nan that was showing up
for n in nh: # Aggregate Cases into summary data
    #Setup neighborhood df's
    n_cases_df = case_df.loc[case_df['Neighbourhood Name'] == n]
    new_row = [n, len(n_cases_df)] # Create new row to be added to the output df

    # Sort the age group row to ensure correct order
    n_cases_df['Age Group'].fillna('0_Unknown', inplace= True, )
    n_cases_df['sort'] = n_cases_df['Age Group'].str.extract('(\d+)', expand=False).astype(int)
    n_cases_df = n_cases_df.sort_values('sort', ascending=False)
    n_cases_df = n_cases_df.drop('sort', axis=1)
    #Append new count for specific age category to the new row list
    # Add field names to the field names list
    for age_cat in n_cases_df['Age Group'].unique().tolist():
        # Add the new column to the field names list
        if f'{age_cat}' not in field_names: field_names.append(f'{age_cat}')

        cat_cases_df = n_cases_df.loc[n_cases_df['Age Group'] == age_cat]
        if len(cat_cases_df) == 0:
            new_row.append(0)
        else:
            new_row.append(len(cat_cases_df))
    
    # Add client gender counts
    n_cases_df = sortByColumn(n_cases_df, 'Client Gender')
    
    out_rows.append(new_row)   
    # print(field_names)
    # print(new_row)
    # sys.exit()
n_covid_df = pd.DataFrame(out_rows, columns=field_names)
n_covid_df = n_covid_df.sort_values('Neighbourhood_Name', ascending=True)
n_covid_df['N_INT'] = range(1, len(n_covid_df)+1)
n_covid_df.to_csv(os.path.join(outFolder, 'To_COVID_n_Counts.csv'), index=False)

#Join the created covid cound csv to the neighbourhoods shp and export
n_gdf = gpd.read_file(neighbourhoods_json)
n_gdf['AREA_STRING'] = n_gdf['AREA_NAME'].str.split('(', 1).str[0]
n_gdf = n_gdf.sort_values('AREA_STRING', ascending= True)
n_gdf['AREA_INT'] = range(1, len(n_gdf)+1)
n_gdf = n_gdf.merge(n_covid_df, how='left', left_on= 'AREA_INT', right_on='N_INT')

n_gdf.to_file(os.path.join(outFolder, 'Neighbourhood_COVID.geojson'), driver= 'GeoJSON')
print('Done!')
