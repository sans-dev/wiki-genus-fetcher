from pygbif import species as spec
from pygbif import occurrences as oc
import json

# load data as dict from json file
data_path = 'data/species_count.json'
with open(data_path,'r') as f:
    data = json.load(f)

out = {}
for order, genus_data in data.items():
    print(order)
    for genus, species_count in genus_data.items():
        print(f"    {genus}")
        try:
            gbif_data = spec.name_backbone(name=genus, rank='genus')
        except Exception as e:
            print(f"Retreiving genus info not possible for {genus}")
            print(e)
        try:
            geo_location = oc.search(genusKey=gbif_data['genusKey'])
            if not geo_location['results']:
                raise(IndexError)
        except Exception as e:
            print(f'No geoinformation found for genus {genus}')
            print(e)
            continue
        
        continents = []
        for res in geo_location['results']

        

