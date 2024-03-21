from pygbif import species as spec
from pygbif import occurrences as oc
import json
import pandas as pd
from tqdm import tqdm

# load data as dict from json file
data_path = 'data/species_count.json'
with open(data_path,'r') as f:
    data = json.load(f)

out_json = {}
columns = ['order', 'family', 'genus', 'continent', 'n-genus-species']
out_csv = []
pbar = tqdm(data.items(),total=len(data.values()))
for order, genus_data in pbar:
    pbar.set_description(f'Processing genera for order {order}')
    genus_pbar = tqdm(genus_data.items(), total=len(genus_data.values()))
    for genus, species_count in genus_pbar:
        genus_pbar.set_description(f'fetching geo information for genus {genus}')
        try:
            gbif_data = spec.name_backbone(name=genus, rank='genus')
        except Exception as e:
            print(f"Retreiving genus info not possible for {genus}")
        try:
            geo_location = oc.search(genusKey=gbif_data['genusKey'])
            if not geo_location['results']:
                raise(IndexError(f'IndexError: No geoinformation found for genus {genus}.'))
        except Exception as e:
            print(e)
        
        continents = set([location.get('continent') for location in geo_location['results']])
        countries = set([location.get('country') for location in geo_location['results']])

        continents = list(filter(lambda continent : continent is not None, continents))
        countries = list(filter(lambda country : country is not None, countries))

        family = gbif_data.get('family', 'NA')

        out_json[genus] = {
            'order' : order,
            'family' : family,
            'continents' : continents,
            'countries' : countries
            }
        if not continents:
            csv_entry = [order, family, genus, "NA", species_count]
            out_csv.append(csv_entry)
            continue
        for continent in continents:
            csv_entry = [order, family, genus, continent, species_count]
            out_csv.append(csv_entry)

# save the data
df = pd.DataFrame(out_csv, columns=columns)
df.to_csv('data/species-count-region.csv')
with open('data/species-count-region.json', 'w') as f:
        json.dump(out_json, f, indent=4)