# Wiki Genus Fetcher
This Python program fetches the number of species for all genera within a start classis (e.g. Insecta). 
It uses the requests library to send HTTP GET requests to  the  Wikimedia species API and parses the responses using the json library.
## Installtion
First, clone this repo with and cd into it:

``` 
git clone git@github.com:sans-dev/wiki-genus-fetcher.git
cd wiki-genus-fetcher/
```
Best practice is to create a conda or python environment.
After activating it run:
```
pip install requirements.txt
```

## Setting Up a config.ini file
To set up a config.ini file for this program, follow these steps:
1. Create a new file named config.ini in the configs directory.
2. Add the following sections  and options  to the file:


```
[WIKI]
user_name = YOUR_WIKIMEDIA_USERNAME
api_token = YOUR_WIKIMEDIA_API_TOKEN
user_agent = YOUR_USER_AGENT_STRING (Name of the Application)
email = YOUR_EMAIL_ADDRESS
```

- **user_name**: Your Wikimedia username.
- **api_token**: Your Wikimedia API token.
- **user_agent**: This is a string that identifies this program to the Wikimedia API.
- **email**: Your email address. This is used to identify yourself to the Wikimedia API servers.

## Running the Program
Once you have set up your config.ini file, you can run the program by calling the following command:
```
python wiki_genus_scraper.py --config configs/config.ini --start-taxon YOUR_START_TAXON
```

where YOUR_START_TAXON is the name of the taxon from which you want to start fetching species counts.

## Output
The program will output a JSON file named species_count.json that contains a dictionary of species counts for each genus within the start taxon. The program will also output a CSV file named species_count.csv that contains the same data in a tabular format.
