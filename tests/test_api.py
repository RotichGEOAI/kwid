from api.nasa_power import NASAPowerClient
from api.chirps import CHIRPSClient
from api.wra import WRAClient


def test_nasa_power_fallback_shape():
    client = NASAPowerClient()
    data, meta = client.fetch_climate_point(-1.28, 36.8, start="20250101", end="20250103")
    assert meta["status"] in {"success", "fallback"}
    assert "precipitation_mm" in data


def test_chirps_fallback_shape():
    client = CHIRPSClient()
    data, meta = client.fetch_rainfall(-1.28, 36.8)
    assert meta["status"] in {"success", "fallback"}
    assert "annual_total_mm" in data


def test_chirps_region_fallback_shape():
    client = CHIRPSClient()
    square = {
        "type": "Polygon",
        "coordinates": [[[36.7, -1.4], [36.9, -1.4], [36.9, -1.2], [36.7, -1.2], [36.7, -1.4]]],
    }
    data, meta = client.fetch_rainfall_for_region(square)
    assert meta["status"] in {"success", "fallback"}
    assert "period_precipitation_mm" in data


def test_wra_fallback_shape():
    client = WRAClient()
    data, meta = client.fetch_borehole_registry("Nairobi")
    assert meta["status"] in {"success", "fallback"}
    assert "registered_boreholes" in data
