import requests
import json
from tqdm import tqdm
import time
from geopy.geocoders import Nominatim

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

def is_within_portugal(latitude, longitude):
    # Check if the latitude and longitude fall within Portugal's boundaries
    return 36.8383 <= latitude <= 42.1542 and -9.5266 <= longitude <= -6.1892

# Fetch the list of postos
url_postos = 'https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/ListarDadosPostos?qtdPorPagina=9999&pagina=1&orderDesc='
response_postos = fetch_data(url_postos)

print("Fetching data for postos...")
# Create a progress bar with emojis
for _ in tqdm(range(100), desc="🔍 Fetching data", ascii=True, ncols=100):
    time.sleep(0.03)  # Adding a slight delay for fun

# Initialize the geolocator
geolocator = Nominatim(user_agent="myGeocoder")

# Lists to store logs
not_found_locations = []
locations_outside_portugal = []

# Iterate through each posto and fetch additional details
for index, posto in enumerate(response_postos['resultado'], 1):
    posto_id = posto['Id']
    url_bomba = f'https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/GetDadosPostoMapa?id={posto_id}&f=json'
    response_bomba = fetch_data(url_bomba)

    # Use CodPostal for better accuracy
    cod_postal = response_bomba['resultado']['Morada']['CodPostal']
    location = geolocator.geocode(cod_postal, exactly_one=True, country_codes=['pt'])

    # If CodPostal doesn't provide a precise location, use the Localidade
    if not location:
        localidade = response_bomba['resultado']['Morada']['Localidade']
        location = geolocator.geocode(localidade, exactly_one=True, country_codes=['pt'])

    # Check if the location is within Portugal's boundaries
    latitude = location.latitude if location else None
    longitude = location.longitude if location else None
    if latitude and longitude:
        if not is_within_portugal(latitude, longitude):
            locations_outside_portugal.append(posto_id)
            latitude = None
            longitude = None
    else:
        not_found_locations.append(posto_id)

    # Save the latitude and longitude to the posto data
    posto['latitude'] = latitude
    posto['longitude'] = longitude

    # Display the progress bar with percentage of processed files
    progress = (index / len(response_postos['resultado'])) * 100
    tqdm.write(f"\r🌟 Processing postos: {index}/{len(response_postos['resultado'])} - {progress:.2f}% ", end="")

print("\n🎉 Data fetching and geocoding completed.")

# Save the modified posto data to a JSON file
output_file = 'postos_with_coords.json'
with open(output_file, 'w') as json_file:
    json.dump(response_postos['resultado'], json_file, indent=2)

print(f"📝 Data saved to {output_file}.")

# Logging
if not_found_locations:
    print(f"\n🚫 Locations not found for postos with IDs: {', '.join(map(str, not_found_locations))}")

if locations_outside_portugal:
    print(f"\n⚠️ Locations found outside Portugal for postos with IDs: {', '.join(map(str, locations_outside_portugal))}")
