"""
Data downloaders for Pakistan traffic datasets.
Handles real downloads with fallback to mock data when DATA_MODE=mock.
"""
import pandas as pd
import geopandas as gpd
from pathlib import Path
import requests
from loguru import logger
from config.settings import DATA_MODE, HUGGINGFACE_TOKEN, RAW_DATA_DIR


def download_lahore_traffic_data():
    """Download Lahore traffic dataset from Hugging Face."""
    if DATA_MODE == "mock":
        logger.info("DATA_MODE=mock: Returning sample Lahore traffic data")
        return _get_sample_lahore_data()

    try:
        from datasets import load_dataset
        dataset = load_dataset(
            "HaajraMumtaz/LahoreTrafficData",
            token=HUGGINGFACE_TOKEN if HUGGINGFACE_TOKEN else None
        )
        df = pd.DataFrame(dataset['train'])
        logger.info(f"Downloaded {len(df)} Lahore traffic records")
        return df
    except ImportError as e:
        logger.warning(f"datasets library not installed: {e}")
        return _get_sample_lahore_data()
    except Exception as e:
        logger.error(f"Failed to download Lahore traffic data: {e}")
        return _get_sample_lahore_data()


def _get_sample_lahore_data():
    """Return representative sample data for Lahore."""
    return pd.DataFrame({
        'origin_zone': ['Gulberg', 'DHA', 'Model Town', 'Johar Town', 'Cantt'],
        'dest_zone': ['DHA', 'Gulberg', 'Johar Town', 'Model Town', 'DHA'],
        'road_type': ['Highway', 'Arterial', 'Local', 'Arterial', 'Highway'],
        'num_lanes': [4, 3, 2, 3, 4],
        'speed_limit_kmh': [80, 50, 30, 50, 80],
        'is_one_way': [False, True, False, False, False],
        'distance_km': [5.2, 3.1, 1.8, 4.5, 6.0],
        'road_curvature': [0.5, 0.8, 0.3, 0.6, 0.4],
        'has_signal': [True, True, False, True, True],
        'is_construction': [False, True, False, False, False],
        'weather_condition': ['Clear', 'Rain', 'Clear', 'Fog', 'Clear'],
        'time_slot': ['Rush', 'Normal', 'Off-peak', 'Rush', 'Normal'],
        'day_type': ['Weekday', 'Weekend', 'Weekday', 'Weekday', 'Weekend'],
        'congestion_multiplier': [1.5, 1.2, 0.8, 1.8, 1.1]
    })


def download_road_surface_data():
    """Download road surface data from HDX or return mock data."""
    if DATA_MODE == "mock":
        logger.info("DATA_MODE=mock: Returning sample road surface data")
        return _get_sample_surface_data()

    try:
        # HDX data download would go here
        # For now, return sample since HDX requires specific API usage
        logger.warning("HDX download not yet implemented; returning sample data")
        return _get_sample_surface_data()
    except Exception as e:
        logger.error(f"Failed to download road surface data: {e}")
        return _get_sample_surface_data()


def _get_sample_surface_data():
    return gpd.GeoDataFrame({
        'osm_id': ['way_1', 'way_2', 'way_3', 'way_4', 'way_5'],
        'pred_class': ['paved', 'unpaved', 'paved', 'paved', 'unpaved'],
        'urban': [True, False, True, True, False],
        'predicted_length': [1200, 800, 2500, 1500, 600],
        'geometry': gpd.GeoSeries.from_wkt([
            'POINT(74.3587 31.5204)',
            'POINT(74.4000 31.4800)',
            'POINT(74.3200 31.5500)',
            'POINT(74.3600 31.5100)',
            'POINT(74.4200 31.4600)'
        ])
    })


def load_accident_data():
    """Load compiled accident data from Pakistan."""
    return {
        'total_accidents_2019_2024': 2500000,
        'fatalities': 70600,
        'injuries': 4000000,
        'motorcycle_involvement': 0.71,
        'unlicensed_drivers': 0.60,
        'province_breakdown': {
            'Punjab': {'accidents': 1560000, 'fatalities': 18001},
            'Sindh': {'accidents': 700000, 'fatalities': 12286},
            'KPK': {'accidents': 314000, 'fatalities': 7545},
            'Balochistan': {'accidents': 111245, 'fatalities': 5969}
        }
    }


def load_challan_data():
    """Load e-challan statistics."""
    return {
        'Karachi_2026': {
            'Jan': 128990,
            'Feb': 156099,
            'Mar': 164033,
            'Apr': 144437
        },
        'Islamabad_2025': {
            'total_challans': 65784,
            'helmet_compliance': 0.96,
            'fatal_accidents_reduction': 0.45,
            'licensed_drivers_increase': '37% to 81%'
        }
    }


def download_osm_pakistan(city="Lahore, Pakistan", network_type="drive"):
    """Download road network from OSM for a specific city (not entire country)."""
    try:
        import osmnx as ox
        logger.info(f"Downloading OSM data for: {city}")
        graph = ox.graph_from_place(city, network_type=network_type, simplify=True)
        logger.info(f"Downloaded OSM graph with {len(graph.nodes)} nodes and {len(graph.edges)} edges")
        return graph
    except ImportError:
        logger.warning("osmnx not installed. Install with: pip install osmnx")
        return None
    except Exception as e:
        logger.error(f"Failed to download OSM data: {e}")
        return None
