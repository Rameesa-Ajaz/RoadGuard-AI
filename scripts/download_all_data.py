"""
Download all Pakistan traffic datasets.
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_pipeline.downloaders import (
    download_lahore_traffic_data,
    download_road_surface_data,
    load_accident_data,
    load_challan_data,
    download_osm_pakistan
)
from config.settings import RAW_DATA_DIR
from loguru import logger


def main():
    logger.info("📥 Downloading Pakistan Traffic Data...")
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("  • Lahore Traffic Data...")
    lahore = download_lahore_traffic_data()
    lahore.to_csv(RAW_DATA_DIR / "lahore_traffic.csv", index=False)
    print(f"    ✓ {len(lahore)} records saved")

    print("  • Road Surface Data...")
    surface = download_road_surface_data()
    if hasattr(surface, 'to_file'):
        surface.to_file(RAW_DATA_DIR / "road_surface.geojson", driver="GeoJSON")
    else:
        surface.to_csv(RAW_DATA_DIR / "road_surface.csv", index=False)
    print(f"    ✓ {len(surface)} records saved")

    print("  • Accident Data...")
    accidents = load_accident_data()
    import json
    with open(RAW_DATA_DIR / "accidents.json", "w") as f:
        json.dump(accidents, f, indent=2)
    print("    ✓ Accident statistics saved")

    print("  • Challan Data...")
    challans = load_challan_data()
    with open(RAW_DATA_DIR / "challans.json", "w") as f:
        json.dump(challans, f, indent=2)
    print("    ✓ Challan statistics saved")

    print("  • OSM Lahore (sample city)...")
    osm = download_osm_pakistan(city="Lahore, Pakistan")
    if osm is not None:
        import osmnx as ox
        ox.save_graphml(osm, RAW_DATA_DIR / "lahore_osm.graphml")
        print("    ✓ OSM graph saved")
    else:
        print("    ⚠ OSM download skipped (osmnx not installed or error)")

    logger.info("✅ All data downloaded successfully!")


if __name__ == "__main__":
    main()
