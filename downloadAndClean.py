import sys, os, requests, csv
import pandas as pd
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
#-------------------------------------------------------
# Inputs
dataPath = 'https://ckan0.cf.opendata.inter.prod-toronto.ca/download_resource/e5bf35bc-e681-43da-b2ce-0242d00922ad?format=csv'
nProfilesCSV = r'H:\TorontoCOVID_FSA\data\neighbourhood-profiles-2016-csv.csv'
outFolder = r'H:\COVID_Data'

#-------------------------------------------------------
#Logic

#Restructure Neighbourhood Profile data in pandas as it comes in a non-useful format
nProfiles = pd.read_csv(nProfilesCSV, header== False)

print(nProfiles.head())
sys.exit() #Below works fix the neighborhoods first thats more work
#Download COVID data and convert it into a pandas dataframe
caseData = os.path.join(outFolder, 'TO_CaseData.csv')
print('Downloading TO case data from source')
case_df = download_csv(dataPath)


print('Done!')
