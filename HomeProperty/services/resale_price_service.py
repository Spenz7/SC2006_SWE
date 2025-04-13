import time
import requests

API_URL = "https://data.gov.sg/api/action/datastore_search?resource_id=d_8b84c4ee58e3cfc0ece0d773c8ca6abc"
PAGE_SIZE = 100

class ResalePriceService:
    def __init__(self, flat_type, town, floor_area, lease_remaining, max_time=60):
        self.flat_type = flat_type
        self.town = town
        self.floor_area = int(floor_area)
        self.lease_remaining = int(lease_remaining)
        self.max_time = max_time
        self.start_time = time.time()

    def _parse_remaining_lease(self, lease_str):
        try:
            lease_str = lease_str.replace("years", "").replace("year", "").replace("months", "").replace("month", "").strip()
            parts = lease_str.split()
            years = int(parts[0]) if len(parts) >= 1 else 0
            months = int(parts[1]) if len(parts) >= 2 else 0
            return round(years + months / 12, 1)
        except Exception as e:
            print(f"Error parsing lease string: {e}")
            return 0

    def _fetch_api_page(self, offset):
        try:
            response = requests.get(API_URL, params={'limit': PAGE_SIZE, 'offset': offset})
            response.raise_for_status()
            data = response.json()
            return data['result']['records'], data['result']['total']
        except Exception as e:
            print(f"Error fetching API data: {e}")
            return [], 0

    def _filter_records(self, records):
        min_area = self.floor_area - 10
        max_area = self.floor_area + 10
        min_lease = self.lease_remaining - 5
        max_lease = self.lease_remaining + 5

        filtered = []
        for record in records:
            if record.get("flat_type") != self.flat_type or record.get("town") != self.town:
                continue

            area = float(record.get("floor_area_sqm", 0))
            lease = self._parse_remaining_lease(record.get("remaining_lease", "0 years 0 months"))

            if not (min_area <= area <= max_area and min_lease <= lease <= max_lease):
                continue

            filtered.append(record)

        return sorted(filtered, key=lambda x: x.get('month', ''), reverse=True)

    def get_recent_similar_sales(self):
        all_records = []
        offset = 0
        total_records = None

        print(f"🔍 Searching for: {self.flat_type} in {self.town} — {self.floor_area} sqft, {self.lease_remaining} yrs")

        while True:
            if time.time() - self.start_time > self.max_time:
                print(f"⏱️ Stopped after {self.max_time} seconds")
                break

            records, total = self._fetch_api_page(offset)
            if not records:
                break

            all_records.extend(records)
            offset += PAGE_SIZE

            if total_records is None:
                total_records = total
            if offset >= total_records:
                break

        filtered = self._filter_records(all_records)
        print(f"✅ Found {len(filtered)} filtered records")
        return filtered[:5]