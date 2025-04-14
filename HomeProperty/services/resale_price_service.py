import time
import requests

API_URL = "https://data.gov.sg/api/action/datastore_search?resource_id=d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
PAGE_SIZE = 100


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


def is_valid_record(record, flat_type, town, min_area, max_area, min_lease, max_lease):
    if record.get("flat_type") != flat_type or record.get("town") != town:
        return False

    area = float(record.get("floor_area_sqm", 0))
    if area < min_area or area > max_area:
        return False

    lease = parse_remaining_lease(record.get("remaining_lease", "0 years 0 months"))
    return min_lease <= lease <= max_lease


def fetch_and_filter_batch(flat_type, town, offset, min_area, max_area, min_lease, max_lease):
    records, _ = fetch_resale_data_from_api(flat_type, town, offset)
    return [
        record for record in records
        if is_valid_record(record, flat_type, town, min_area, max_area, min_lease, max_lease)
    ]


def fetch_resale_data_from_api(flat_type, town, offset=0):
    params = {
        'limit': PAGE_SIZE,
        'offset': offset
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data['result'].get('records', []), data['result'].get('total', 0)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return [], 0


def find_similar_past_prices(flat_type, town, floor_area, remaining_lease, max_time=60):
    matched_records = []
    start_time = time.time()

    print(f"🔍 Starting to fetch records for flat_type: {flat_type}, town: {town}, floor_area: {floor_area}, remaining_lease: {remaining_lease}")

    _, total_records = fetch_resale_data_from_api(flat_type, town, offset=0)
    if total_records == 0:
        print("❌ No records found for the given flat type and town.")
        return []

    last_offset = (total_records - 1) // PAGE_SIZE * PAGE_SIZE
    offset = last_offset

    min_area, max_area = int(floor_area) - 10, int(floor_area) + 10
    min_lease, max_lease = int(remaining_lease) - 5, int(remaining_lease) + 5

    while offset >= 0 and time.time() - start_time <= max_time:
        print(f"🔄 Fetching at offset: {offset}")
        filtered_batch = fetch_and_filter_batch(flat_type, town, offset, min_area, max_area, min_lease, max_lease)
        matched_records.extend(filtered_batch)

        if len(matched_records) >= 5:
            print("✅ Found enough matches. Returning.")
            return sorted(matched_records, key=lambda x: x.get('month', ''), reverse=True)[:5]

        offset -= PAGE_SIZE

    print(f"✅ Total matches found after full scan: {len(matched_records)}")
    return sorted(matched_records, key=lambda x: x.get('month', ''), reverse=True)[:5]