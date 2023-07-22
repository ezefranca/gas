import requests
import json

def fetch_data(url):
    headers = {
        'accept': 'application/vnd.github.v3+json',
    }

    response = requests.get(url, headers=headers)
    response.raise_for_status()  # Raise exception for failed requests
    return response.json()

# Fetch the existing postos_with_coords.json from the GitHub repository
github_repo_url = 'https://api.github.com/repos/ezefranca/gas/contents/postos_with_coords.json'
github_raw_url = fetch_data(github_repo_url)['download_url']
existing_data = fetch_data(github_raw_url)

# Fetch the latest data from the precoscombustiveis service
precoscombustiveis_url = 'https://precoscombustiveis.dgeg.gov.pt/api/PrecoComb/ListarDadosPostos?qtdPorPagina=9999&pagina=1&orderDesc='
latest_data = fetch_data(precoscombustiveis_url)['resultado']

# Extract the IDs from the existing data and the latest data
existing_ids = set(posto['Id'] for posto in existing_data)
latest_ids = set(posto['Id'] for posto in latest_data)

# Find the differences between the IDs
new_ids = latest_ids - existing_ids
removed_ids = existing_ids - latest_ids

# Check for any differences
if new_ids:
    for new_id in new_ids:
        print(f"Service has this new Id {new_id}")
else:
    print("No new Ids found.")

if removed_ids:
    for removed_id in removed_ids:
        print(f"Service does not have this Id anymore {removed_id}")
else:
    print("No removed Ids found.")