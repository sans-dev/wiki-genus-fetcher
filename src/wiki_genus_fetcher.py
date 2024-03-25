import requests 
import json
import pandas as pd
from tqdm import tqdm
import argparse
from configparser import ConfigParser
from pygbif import species as spec
from datetime import date
import sys
from datetime import datetime as dt
sys.setrecursionlimit(10000)

BASE_URL = 'https://species.wikimedia.org/w/rest.php/v1/page/'
HEADERS = {}


def get_iso_date():
    now = dt.now()
    now = now.strftime("%Y-%m-%dT%H-%M")
    return now

def get_taxon_name(substring, taxon_level):
    """
    Extracts the taxon name from a given substring.

    Parameters:
    substring (str): The string from which the taxon name is to be extracted.
    taxon_level (str): The taxon level to be checked in the substring.

    Returns:
    str|None: The taxon name if found, otherwise None.
    """
    if taxon_level not in substring:
        return None
    taxon_name = substring.split("|")[-1].strip()[:-2].replace("}", "").replace("{", "")
    return taxon_name

def get_species_count(taxon_name, pbar, species_count={}):
    """ This function fetches and counts the number of species under a given taxon from a web resource.

    The function takes the following parameters:

    taxon_name (str): The name of the taxon for which the species count is required.
    pbar (ProgressBar object): A progress bar object to track the progress of the operation.
    species_count (dict, optional): An existing dictionary to which the count of species for the taxon will be added. If not provided,
    a new dictionary will be created.

    The function uses the requests library to send an HTTP GET request to the web resource and parses the response using the json library. 
    It then checks the 'source' field in the response for certain keys 
    ('{sp', '{g', '{fam', '{superfam', '{subordo') that indicate the presence of species, genus, family, superfamily, or suborder information, respectively.
    For each key found, the function counts the number of lines in the 'source' field that contain that key and adds the count to the species_count dictionary 
    with the taxon_name as the key. If a key is found that matches the taxon_name, the function stops counting and returns the species_count dictionary.
    If no keys are found in the 'source' field, the function returns an empty dictiotaxon
    Note: This function is recursive, meaning it calls itself when it finds a key in the 'source' field that doesn't match the taxon_name. 
    The recursion stops when a key matching the taxon_name is found or when all lines in the 'source' field have been checked. """
    url = BASE_URL + taxon_name
    pbar.set_description(f"fetching results for {taxon_name}...")
    response = requests.get(url, headers=HEADERS)
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
                    get_species_count(genus, pbar, species_count)
        if '{fam' in source:
            for line in source.splitlines():
                fam = get_taxon_name(line,'{fam')
                if fam:
                    if fam == taxon_name:
                        return
                    get_species_count(fam, pbar, species_count)
        if '{superfam' in source:
            for line in source.splitlines():
                superfam = get_taxon_name(line,'{superfam')
                if superfam:
                    if superfam == taxon_name:
                        return
                    get_species_count(superfam, pbar, species_count)                    
        if '{subordo' in source:
            for line in source.splitlines():
                suborder = get_taxon_name(line,'{subordo')
                if suborder:
                    if suborder == taxon_name:
                        return
                    get_species_count(suborder, pbar, species_count)
        return species_count
    else:
        return

def main(args):
    # build header from config
    config = ConfigParser()
    config.read(args.config)
    config = config[args.section]

    auth_str = config['user_name'] + config['api_token']
    user_agent_str = config['user_agend'] + f"({config['email']})"

    HEADERS = {
        'Authorization' : auth_str,
        'User-Agent' : user_agent_str
    }

    url = BASE_URL + args.start_taxon
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
    except requests.exceptions.HTTPError as err:
        raise err


    init_page = json.loads(response.text)
    source_str = init_page['source'].splitlines()

    taxon_names = []
    for substring in source_str:
        taxon_name = get_taxon_name(substring, taxon_level='ordo')
        if taxon_name:
            taxon_names.append(taxon_name.replace('"',''))
    
    species_count = {}
    pbar = tqdm(taxon_names)
    for order in pbar:
        print(f"processing {order}...")
        sc = get_species_count(order, pbar, species_count={})
        if sc is not None:
            species_count[order] = sc

    out_path = f'data/{get_iso_date()}_{args.out}'
    with open(f'{out_path}.json', 'w') as f:
        json.dump(species_count, f, indent=4)
    
    # convert dictionary to list of tuples
    data = [(order, genus, count) for order in species_count for genus, count in species_count[order].items()]

    # create dataframe
    species_df = pd.DataFrame(data, columns=['Order', 'Genus', 'species_count'])
    species_df.to_csv(f'{out_path}.csv')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="This python program fetches the number of species for all genera within a start taxon.")
    parser.add_argument("--config", type=str, help="Path of the config file containing the user credentials for wikimedia.")
    parser.add_argument("--section", type=str, default="WIKI", help="Section of the configuration. Default is 'WIKI'.")
    parser.add_argument("--start-taxon", type=str, help="Initial Taxon from which species numbers will be fetched for each genus.")
    parser.add_argument('--out', default='speecies_count', type=str)
    args = parser.parse_args()
    main(args)