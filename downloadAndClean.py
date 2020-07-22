import sys, os, requests, csv
import pandas as pd
import numpy as np
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
#-------------------------------------------------------
# Inputs
dataPath = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=csv'
nProfilesCSV = r'H:\TorontoCOVID_FSA\data\neighbourhood-profiles-2016-csv.csv'
outFolder = r'H:\COVID_Data'

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
print('Downloading TO case data from source')
case_df = download_csv(dataPath)
casesByN = pd.DataFrame(list(nProfiles.Neighbourhood_Name), columns= ['Neighbourhood Name'])
casesByN['Total Case Count'] = [len(case_df.loc[case_df['Neighbourhood Name'] == x]) for x in list(casesByN['Neighbourhood Name'])]


for n in list(nProfiles.Neighbourhood_Name): # Aggregate Cases into summary data
    ndf = casesByN.loc[casesByN['Neighbourhood Name'] == n]
    


print(casesByN.head())

print('Done!')
