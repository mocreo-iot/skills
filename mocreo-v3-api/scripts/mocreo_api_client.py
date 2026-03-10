import requests
import time

class MocreoV3Client:
    """MOCREO v3 Public API Client for Smart System."""
    def __init__(self, api_key):
        self.base_url = "https://api.mocreo.com/v1"
        self.headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json"
        }

    def list_assets(self):
        """Need user session token (Bearer), not API Key for this specific endpoint in OpenAPI."""
        pass

    def get_devices(self, asset_id):
        """GET /assets/{assetId}/devices"""
        url = f"{self.base_url}/assets/{asset_id}/devices"
        resp = requests.get(url, headers=self.headers)
        return resp.json()

    def get_device_history(self, asset_id, device_id, field="temperature", duration_hours=24):
        """GET /assets/{assetId}/devices/{deviceId}/history"""
        now_ms = int(time.time() * 1000)
        start_ms = now_ms - (duration_hours * 3600 * 1000)
        
        params = {
            "from": start_ms,
            "to": now_ms,
            "tz": "Asia/Shanghai",
            "field": field
        }
        url = f"{self.base_url}/assets/{asset_id}/devices/{device_id}/history"
        resp = requests.get(url, headers=self.headers, params=params)
        return resp.json()
