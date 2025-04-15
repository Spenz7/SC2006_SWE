import requests

DATASET_ID = "d_07c63be0f37e6e59c07a4ddc2fd87fcb"
AGENT_API_URL = f"https://data.gov.sg/api/action/datastore_search?resource_id={DATASET_ID}"

def check_agent_id(agent_id):
    """
    Verifies if the provided agent ID exists in the official dataset.
    Returns True if found, else False.
    """
    try:
        response = requests.get(AGENT_API_URL)
        response.raise_for_status()
        data = response.json()

        if 'result' in data and 'records' in data['result']:
            for record in data['result']['records']:
                if record.get('registration_no') == agent_id:
                    return True
    except Exception as e:
        print(f"Error checking agent ID: {e}")

    return False