"""
Fuzzy logic decision engine for traffic interventions.
"""
import numpy as np
from loguru import logger


class TrafficDecisionEngine:
    def __init__(self):
        self.thresholds = {
            'critical': 80,
            'high': 60,
            'moderate': 40,
            'low': 20
        }

    def decide_action(self, risk_score: float, traffic_flow: float, divergence: float) -> dict:
        """Make decision based on current conditions."""
        if risk_score >= self.thresholds['critical']:
            return {
                'priority': 5,
                'action_type': 'IMMEDIATE_INTERVENTION',
                'recommended_actions': [
                    'Deploy traffic police immediately to manage flow',
                    'Activate variable message signs for diversion',
                    'Adjust signal timing to reduce conflict points',
                    'Notify emergency services to standby'
                ],
                'alert_level': 92,
                'alert_color': 'red',
                'estimated_impact': '45% risk reduction within 2 hours'
            }
        elif risk_score >= self.thresholds['high']:
            return {
                'priority': 3,
                'action_type': 'MONITOR_AND_ADJUST',
                'recommended_actions': [
                    'Recommend alternative routes via VMS/app',
                    'Increase signal green time for congested approaches',
                    'Deploy traffic wardens at key intersections',
                    'Monitor for 30 minutes before escalation'
                ],
                'alert_level': 70,
                'alert_color': 'orange',
                'estimated_impact': '25% risk reduction within 1 hour'
            }
        elif risk_score >= self.thresholds['moderate']:
            return {
                'priority': 2,
                'action_type': 'PREVENTIVE_MEASURES',
                'recommended_actions': [
                    'Continue monitoring traffic patterns',
                    'Prepare diversion routes if conditions worsen',
                    'Check signal timing optimization'
                ],
                'alert_level': 45,
                'alert_color': 'yellow',
                'estimated_impact': '15% risk reduction through prevention'
            }
        else:
            return {
                'priority': 1,
                'action_type': 'ROUTINE_MONITORING',
                'recommended_actions': [
                    'Continue automated monitoring',
                    'Log traffic statistics for trend analysis'
                ],
                'alert_level': 20,
                'alert_color': 'green',
                'estimated_impact': 'Baseline risk maintained'
            }

    def generate_timeline(self, action_plan: dict) -> list:
        """Generate a timeline of recommended actions."""
        timeline = []
        priority = action_plan['priority']

        if priority >= 5:
            timeline = [
                {'time': '0 min', 'action': 'Deploy traffic police', 'owner': 'Traffic Police'},
                {'time': '5 min', 'action': 'Activate VMS diversion', 'owner': 'Control Room'},
                {'time': '15 min', 'action': 'Adjust signal timing', 'owner': 'Signal Engineer'},
                {'time': '30 min', 'action': 'Reassess risk level', 'owner': 'AI System'}
            ]
        elif priority >= 3:
            timeline = [
                {'time': '0 min', 'action': 'Display alternative routes', 'owner': 'VMS/App'},
                {'time': '10 min', 'action': 'Increase green time', 'owner': 'Signal Engineer'},
                {'time': '30 min', 'action': 'Evaluate effectiveness', 'owner': 'AI System'}
            ]
        else:
            timeline = [
                {'time': 'Continuous', 'action': 'Automated monitoring', 'owner': 'AI System'}
            ]

        return timeline
