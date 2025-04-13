import time
import requests

# Constants
API_URL = "https://data.gov.sg/api/action/datastore_search?resource_id=d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
PAGE_SIZE = 100  # We fetch 100 records per request


def parse_remaining_lease(lease_str):
    try:
        if not lease_str:
            return 0
        lease_str = lease_str.replace("years", "").replace("year", "").replace("months", "").replace("month", "").strip()
        parts = lease_str.split()
        years = int(parts[0]) if len(parts) >= 1 else 0
        months = int(parts[1]) if len(parts) >= 2 else 0
        return round(years + months / 12, 1)
    except Exception as e:
        print(f"Error parsing lease string: {e}")
        return 0


def fetch_resale_data_from_api(flat_type, town, offset=0):
    params = {
        'limit': PAGE_SIZE,
        'offset': offset
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if 'result' in data and 'records' in data['result']:
            return data['result']['records'], data['result']['total']
        else:
            return [], 0
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return [], 0


def filter_and_sort_records(records, flat_type, town, min_area=None, max_area=None, min_lease=None, max_lease=None):
    filtered = []
    for record in records:
        if record.get("flat_type") != flat_type or record.get("town") != town:
            continue

        area = float(record.get("floor_area_sqm", 0))
        if min_area is not None and (area < min_area or area > max_area):
            continue

        lease = parse_remaining_lease(record.get("remaining_lease", "0 years 0 months"))
        if min_lease is not None and (lease < min_lease or lease > max_lease):
            continue

        filtered.append(record)

    return sorted(filtered, key=lambda x: x.get('month', ''), reverse=True)


def find_similar_past_prices(flat_type, town, floor_area, remaining_lease, max_time=60):
    matched_records = []
    start_time = time.time()

    print(f"🔍 Starting to fetch records for flat_type: {flat_type}, town: {town}, floor_area: {floor_area}, remaining_lease: {remaining_lease}")

    # Step 1: Get total number of records first
    _, total_records = fetch_resale_data_from_api(flat_type, town, offset=0)
    if total_records == 0:
        print("❌ No records found for the given flat type and town.")
        return []

    print(f"📊 Total records available: {total_records}")
    
    # Step 2: Calculate the last offset
    last_offset = (total_records - 1) // PAGE_SIZE * PAGE_SIZE  # e.g., if total=615, last_offset=600

    offset = last_offset
    while offset >= 0:
        elapsed_time = time.time() - start_time
        if elapsed_time > max_time:
            print(f"⏱️ Time limit of {max_time} seconds reached.")
            break

        print(f"🔄 Fetching at offset: {offset}, elapsed time: {elapsed_time:.2f}s")
        records, _ = fetch_resale_data_from_api(flat_type, town, offset=offset)

        if not records:
            print("❌ No more records at this offset.")
            break

        filtered_batch = filter_and_sort_records(
            records,
            flat_type,
            town,
            min_area=int(floor_area) - 10,
            max_area=int(floor_area) + 10,
            min_lease=int(remaining_lease) - 5,
            max_lease=int(remaining_lease) + 5
        )

        matched_records.extend(filtered_batch)

        if len(matched_records) >= 5:
            print("✅ Found at least 5 matching records. Returning early.")
            return matched_records[:5]

        offset -= PAGE_SIZE  # Move backward

    print(f"✅ Total matches found after full scan: {len(matched_records)}")
    return matched_records[:5]

