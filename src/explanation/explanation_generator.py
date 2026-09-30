"""
Natural language explanation generator for traffic risk.
"""
from datetime import datetime
from loguru import logger
from sqlalchemy.util import counter


class ExplanationGenerator:
    def __init__(self):
        self.templates = {
            'infrastructure': "Poor road infrastructure (score: {:.1f}/100) is contributing {:.1f}% to the danger. Lane markings, lighting, and surface condition are substandard.",
            'divergence': "High divergence rate of {:.1f} vehicles/min indicates chaotic lane changes and abrupt turns, contributing {:.1f}%.",
            'challan': "Challan ratio of {:.1f}% indicates {} enforcement presence, contributing {:.1f}%.",
            'flow': "Traffic flow of {:.0f} vehicles/hour during {} creates congestion stress, contributing {:.1f}%.",
            'control': "Signal efficiency at {:.1f}% means poor traffic control coordination, contributing {:.1f}%."
        }

    def generate_explanation(self, risk_scores: dict, causal_chain: list, counterfactual: dict) -> dict:
        """Generate comprehensive natural language explanation."""
        attribution = self._generate_attribution(risk_scores, causal_chain)
        causal_text = self._generate_causal_chain(causal_chain)
        temporal = self._generate_temporal_context()
        counter = self._generate_counterfactual(counterfactual)

        full = f"""{attribution}

{causal_text}

{temporal}

{counter}"""

        return {
            'full_explanation': full,
            'attribution': attribution,
            'causal_chain': causal_text,
            'temporal_context': temporal,
            'counterfactual': counter
        }

    def _generate_attribution(self, risk_scores: dict, causal_chain: list) -> str:
        if not causal_chain:
            return "Risk level is moderate with no dominant factors."

        top_factors = causal_chain[:3]
        parts = [f"{item['factor']} ({item['contribution']}%)" for item in top_factors]
        return f"""This road segment is primarily dangerous due to: {', '.join(parts)}.
Overall risk score: {risk_scores.get('risk_score', 'N/A')}/100 ({risk_scores.get('risk_level', 'unknown')} level)."""

    def _generate_causal_chain(self, chain: list) -> str:
        if not chain:
            return "No significant causal chain detected."

        # Build narrative
        steps = []
        for item in chain:
            factor = item['factor']
            state = item['state']
            if factor == 'Infrastructure' and state == 'poor':
                steps.append("Poor Infrastructure → Low visibility & surface quality")
            elif factor == 'Divergence' and state == 'high':
                steps.append("High Divergence → Chaotic lane changes & conflict points")
            elif factor == 'ChallanRatio' and state == 'low':
                steps.append("Low Enforcement → Speeding & signal violations")
            elif factor == 'Flow' and state == 'high':
                steps.append("High Traffic Flow → Congestion & driver frustration")
            elif factor == 'ControlEfficiency' and state == 'poor':
                steps.append("Poor Signal Control → Intersection conflicts")

        if steps:
            steps.append("→ Increased Accident Probability")
            formatted_steps = "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
            return f"**Causal Chain:**\n{formatted_steps}"
        
        return "**Causal Chain:** General traffic conditions contribute to baseline risk."
    def _generate_temporal_context(self) -> str:
        hour = datetime.now().hour
        if 7 <= hour <= 10:
            period = "morning rush (7-10 AM)"
            note = "School and office traffic peaks."
        elif 12 <= hour <= 14:
            period = "midday (12-2 PM)"
            note = "Commercial delivery traffic is high."
        elif 17 <= hour <= 20:
            period = "evening rush (5-8 PM)"
            note = "Return traffic with fatigued drivers."
        elif 0 <= hour <= 5:
            period = "late night (12-5 AM)"
            note = "Reduced visibility, higher speeding tendency."
        else:
            period = "non-peak hours"
            note = "Traffic is moderate."

        return f"""**Temporal Context:**
Current time falls in {period}. {note}
Risk may vary significantly outside this window."""

    def _generate_counterfactual(self, counter: dict) -> str:
        if not counter:
            return "**Counterfactual:** No improvement scenario analyzed."

        return f"""**What If? (Counterfactual Analysis)**
If {counter['target_factor']} were improved to '{counter['suggested_value']}':
- Current estimated risk: {counter['original_risk']}%
- Projected risk: {counter['counterfactual_risk']}%
- **Potential reduction: {counter['percentage_reduction']}%**

This suggests prioritizing {counter['target_factor'].lower()} improvements could have significant impact."""
