import requests 
import json
import pandas as pd
from tqdm import tqdm
import sys
sys.setrecursionlimit(10000) 

page = 'insecta'
base_url = 'https://species.wikimedia.org/w/rest.php/v1/page/'
url = base_url + page
headers = {
  'Authorization': 'Sebsan 90 eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIxMDE1ZmU3NTNjZGMxZTJmYzkxY2Y2ZGU0OTk4OGZjZSIsImp0aSI6IjlkNGE5ZTZiZWQwOGNiNTcxZmUyODdhYTNjYTc5NWU0Yjk5ZTBiZjMxZTI4MjdjODYwYzQ0YWRjZDRmZDI3MmRmZTVmNTAyMDdkY2NkOWUzIiwiaWF0IjoxNzEwNDAzMzI5LjE0NTg4NiwibmJmIjoxNzEwNDAzMzI5LjE0NTg5LCJleHAiOjMzMjY3MzEyMTI5LjE0MzI4LCJzdWIiOiI3NTE5ODgwNSIsImlzcyI6Imh0dHBzOi8vbWV0YS53aWtpbWVkaWEub3JnIiwicmF0ZWxpbWl0Ijp7InJlcXVlc3RzX3Blcl91bml0Ijo1MDAwLCJ1bml0IjoiSE9VUiJ9LCJzY29wZXMiOlsiYmFzaWMiXX0.QEQgd2mCuXrxTbdDjRKsUtZVlY_TTwroL-J3Chh9ByzTRjI_kD7AAdx45vAnagzKQU6e9gL09DmvUS8C1TkY_YCzimgq5L4-58X7qdy7bkmASwj-DX6POgQrI12r1iNwHwnNYn4OqHVrDk0I8WfKrNRnNjX0xJ-i6NVuIGAHkJBRjXhiazw_d6J3YzQ68MplNSXgXCThj8vV_E7VlFAFXQ9eTpLCfqMSV9Lk09n7g8lk2_NcxHXqyI3tmRGeM8PdulQi7RBGCoCjoy2o8Qv1yJ5YnQtOQ9AJwA4MTexSipW6dMK6mD12k05rdI7bpjtnhXUOHXg0jLAhQ4VLBJRNpN1A96NXHj9IHiqpdBy3aQyZpMt1NtbWeT1DJHC1HPZVe-iHf_5-hzqBRwJi2cR23q_QBXgI_JaT_bMDVWsBXHQFmFxtmpHKzNoUqXSajY5yd1wMbnF2xdZenNDIJHvotpEUEYaQ-AYlyjz7fKahj92vmX6EAurv8hP5Yc5uMlj9Rf_4qxNuMOStHEyO4NA0fDD2aKVNZEN3O0pRCFiroBHNXTSPBjKlNoFfSk8QeW2-RH8HJJd5XEr0gJXJHrleSue_pCJZRcJwMw5crd0QoBNmeVQF7x8Qy3df2udqyH3u9huRmjoOIdpintYcWtL-10G6t8wUPTl7PaeeQoH71ys',
  'User-Agent': 'Genus (seppelpie@googlemail.com)'
}

response = requests.get(url, headers=headers)
insecta_page = json.loads(response.text)
source_str = insecta_page['source'].splitlines()

def get_taxon_name(substring, taxon_level):
    if taxon_level in substring:
        taxon_name = substring.split("|")[-1].strip()[:-2]
        taxon_name = taxon_name.replace("}", "")
        taxon_name = taxon_name.replace("{", "")
        return taxon_name
    else: return None

def get_species_count(taxon_name, base_url, headers, pbar, species_count={}):
    url = base_url + taxon_name
    pbar.set_description(f"fetching results for {taxon_name}...")
    response = requests.get(url, headers=headers)
    content = json.loads(response.text)
    if 'source' in content.keys():
        source = content['source']          
        if '{sp' in source:
            count = 0
            for line in source.splitlines():
                species = get_taxon_name(line,'{sp')
                if species:
                    count += 1
            species_count[taxon_name] = count
            return species_count
        if '{g' in source:
            for line in source.splitlines():
                genus = get_taxon_name(line,'{g')
                if genus:
                    if genus == taxon_name:
                        return
                    get_species_count(genus,base_url,headers, pbar, species_count)
        if '{fam' in source:
            for line in source.splitlines():
                fam = get_taxon_name(line,'{fam')
                if fam:
                    if fam == taxon_name:
                        return
                    get_species_count(fam, base_url, headers, pbar, species_count)
        if '{superfam' in source:
            for line in source.splitlines():
                superfam = get_taxon_name(line,'{superfam')
                if superfam:
                    if superfam == taxon_name:
                        return
                    get_species_count(superfam, base_url, headers, pbar, species_count)                    
        if '{subordo' in source:
            for line in source.splitlines():
                suborder = get_taxon_name(line,'{subordo')
                if suborder:
                    if suborder == taxon_name:
                        return
                    get_species_count(suborder, base_url, headers, pbar, species_count)
        return species_count
    else:
        return
    
order_names = []
for substring in source_str:
    order_name = get_taxon_name(substring, taxon_level='ordo')
    if order_name:
        order_names.append(order_name.replace('"',''))

species_count = {}
pbar = tqdm(order_names)
for order in pbar:
    print(f"processing {order}...")
    species_count[order] = get_species_count(order, base_url, headers, pbar)

with open('species_count.json', 'w') as f:
    json.dump(species_count, f, indent=4)

# convert dictionary to list of tuples
data = [(order, genus, count) for order in species_count for genus, count in species_count[order].items()]

# create dataframe
species_df = pd.DataFrame(data, columns=['Order', 'Genus', 'species_count'])
species_df.to_csv('species_count.csv')