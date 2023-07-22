import requests
from geopy.geocoders import Nominatim
import json
from tqdm import tqdm
import time

# Function to fetch data from the API
def fetch_data(url):
    headers = {
        'authority': 'precoscombustiveis.dgeg.gov.pt',
        'accept': '*/*',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://precoscombustiveis.dgeg.gov.pt/',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': 'macOS',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
        'cookie': '_ga=GA1.1.843951460.1690047704; cookiekit=1; __cf_bm=BQJGz6Rri8ei7iQHXvb8Mr6D5Ng_DZtiyjRTROKhcYM-1690058531-0-AYEZaKB/q1ZQMOEWc0nQJWYcMfGQVQLIVgNFlhWDOq3Y+Fw1JpEqgARivRLtceb6dCte+Q2g5rGclrfVg85WQFU=; cf_clearance=U8tJc0Hnp5c2ysopPJHsrTU7przNLv.r22xwTlFF5aw-1690058590-0-0.2.1690058590; _ga_GXE3NPJVR6=GS1.1.1690058709.3.1.1690059324.0.0.0'
    }

    response = requests.get(url, headers=headers)
    return response.json()

# Function to perform geocoding using CodPostal and Localidade
def geocode_location(location):
    geolocator = Nominatim(user_agent="myGeocoder")
    return geolocator.geocode(location, exactly_one=True)

# Fetch the list of postos using asynchronous requests
async def fetch_postos(url_postos):
    async with aiohttp.ClientSession() as session:
        async with session.get(url_postos) as response:
            response.raise_for_status()  # Raise exception for failed requests
            return await response.json()

async def process_posto(posto):
    posto_id = posto['Id']
    url_bomba = f'https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/GetDadosPostoMapa?id={posto_id}&f=json'
    response_bomba = await fetch_data(url_bomba)

    # Use CodPostal for better accuracy
    cod_postal = response_bomba['resultado']['Morada']['CodPostal']
    location = await geocode_location(cod_postal)

    # If CodPostal doesn't provide a precise location, use the Localidade
    if not location:
        localidade = response_bomba['resultado']['Morada']['Localidade']
        location = await geocode_location(localidade)

        if not location:
            tqdm.write(f"\n⚠️ Warning: Latitude and Longitude not found for Posto Id: {posto_id}")

    latitude = location.latitude if location else None
    longitude = location.longitude if location else None

    # Save the latitude and longitude to the posto data
    posto['latitude'] = latitude
    posto['longitude'] = longitude

    # Simulate some delay for a fun progress bar animation
    time.sleep(0.1)

    # Display the progress bar with percentage of processed files
    progress = (index / len(response_postos['resultado'])) * 100
    tqdm.write(f"\r🌟 Processing postos: {index}/{len(response_postos['resultado'])} - {progress:.2f}% ", end="")

print("Fetching data for postos...")
url_postos = 'https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/ListarDadosPostos?qtdPorPagina=9999&pagina=1&orderDesc='
response_postos = fetch_data(url_postos)

# Create a progress bar with emojis
for _ in tqdm(range(100), desc="🔍 Fetching data", ascii=True, ncols=100):
    time.sleep(0.03)  # Adding a slight delay for fun

# Iterate through each posto and fetch additional details
for index, posto in enumerate(response_postos['resultado'], 1):
    posto_id = posto['Id']
    url_bomba = f'https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/GetDadosPostoMapa?id={posto_id}&f=json'
    response_bomba = fetch_data(url_bomba)

    # Use CodPostal for better accuracy
    cod_postal = response_bomba['resultado']['Morada']['CodPostal']
    geolocator = Nominatim(user_agent="myGeocoder")
    location = geolocator.geocode(cod_postal, exactly_one=True)

    # If CodPostal doesn't provide a precise location, use the Localidade
    if not location:
        localidade = response_bomba['resultado']['Morada']['Localidade']
        location = geolocator.geocode(localidade, exactly_one=True)

        if not location:
            tqdm.write(f"\n⚠️ Warning: Latitude and Longitude not found for Posto Id: {posto_id}")

    latitude = location.latitude if location else None
    longitude = location.longitude if location else None

    # Save the latitude and longitude to the posto data
    posto['latitude'] = latitude
    posto['longitude'] = longitude

    # Simulate some delay for a fun progress bar animation
    # time.sleep(0.1)

    # Display the progress bar with percentage of processed files
    progress = (index / len(response_postos['resultado'])) * 100
    tqdm.write(f"\r🌟 Processing postos: {index}/{len(response_postos['resultado'])} - {progress:.2f}% ", end="")

print("\n🎉 Data fetching and geocoding completed.")

# Save the modified posto data to a JSON file
output_file = 'postos_with_coords.json'
with open(output_file, 'w') as json_file:
    json.dump(response_postos['resultado'], json_file, indent=2)

print(f"📝 Data saved to {output_file}.")