"""
Risk-aware route optimization.
"""
from typing import Dict, List
from loguru import logger


class RiskAwareRouteOptimizer:
    def __init__(self):
        self.roads = {}

    def add_road_risk(self, road_id: str, risk: float):
        """Add risk score to a road segment."""
        self.roads[road_id] = risk

    def find_alternative_routes(self, origin: str, destination: str) -> Dict:
        """Find alternative routes with risk analysis.

        NOTE: This is a simplified mock. For production, integrate with
        Google Maps Directions API or OSRM for real routing.
        """
        logger.info(f"Finding routes from {origin} to {destination}")

        # In production, these would come from a real routing engine
        return {
            'fastest': {
                'time_min': 22,
                'risk_score': 92,
                'distance_km': 12,
                'type': 'fastest',
                'roads': ['Shahrah-e-Faisal', 'Korangi Road'],
                'description': 'Direct main artery, highest speed but dangerous'
            },
            'balanced': {
                'time_min': 28,
                'risk_score': 45,
                'distance_km': 15,
                'type': 'balanced',
                'roads': ['Rashid Minhas Road', 'University Road'],
                'description': 'Moderate speed with better infrastructure'
            },
            'safest': {
                'time_min': 35,
                'risk_score': 22,
                'distance_km': 18,
                'type': 'safest',
                'roads': ['Service Road', 'DHA Phase 8'],
                'description': 'Slower but well-maintained with enforcement'
            }
        }

    def get_route_explanation(self, route: dict) -> dict:
        """Explain why a route was chosen or avoided."""
        route_type = route.get('type', 'unknown')

        explanations = {
            'fastest': {
                'rationale': "Fastest route uses main arteries but passes through high-risk segments.",
                'avoided_risks': [],
                'accepted_risks': ['High speeding tendency', 'Poor signal coordination']
            },
            'balanced': {
                'rationale': "Balanced route avoids the highest-risk segments while maintaining reasonable travel time.",
                'avoided_risks': ['Shahrah-e-Faisal (92% risk)', 'Korangi Road (78% risk)'],
                'accepted_risks': ['Moderate congestion']
            },
            'safest': {
                'rationale': "Safest route prioritizes well-maintained roads with traffic enforcement.",
                'avoided_risks': [
                    'Shahrah-e-Faisal (92% risk)',
                    'Korangi Road (78% risk)',
                    'Rashid Minhas Road (55% risk)'
                ],
                'accepted_risks': ['Longer travel time']
            }
        }

        return explanations.get(route_type, {
            'rationale': 'Route selected based on user preference.',
            'avoided_risks': [],
            'accepted_risks': []
        })

    def rank_routes_by_preference(self, routes: Dict, risk_tolerance: float = 0.5) -> List[Dict]:
        """Rank routes based on user risk tolerance (0=only safe, 1=only fast)."""
        route_list = []
        for key, route in routes.items():
            route['id'] = key
            # Composite score: lower is better
            time_score = route['time_min'] / 60  # normalize
            risk_score = route['risk_score'] / 100
            route['composite_score'] = (1 - risk_tolerance) * risk_score + risk_tolerance * time_score
            route_list.append(route)

        route_list.sort(key=lambda x: x['composite_score'])
        return route_list
