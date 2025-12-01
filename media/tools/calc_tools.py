from typing import Dict, Any
from sympy import sympify, Symbol


def calculate_risk_probability(param_a: float, param_b: float) -> float:
    """
    Calculate probabilistic risk score using SymPy
    
    Simulates a probabilistic risk scoring calculation.
    Formula: (param_a * 0.6) + (param_b * 0.4)
    
    Args:
        param_a: First risk parameter (weight: 0.6)
        param_b: Second risk parameter (weight: 0.4)
        
    Returns:
        Calculated risk probability (0-10 scale)
    """
    try:
        # Simple weighted formula: (a * 0.6) + (b * 0.4)
        expr = sympify(f"{param_a} * 0.6 + {param_b} * 0.4")
        result = float(expr.evalf())
        # Normalize to 0-10 scale
        return min(max(result, 0.0), 10.0)
    except Exception:
        # Fallback calculation
        return min(max((param_a * 0.6 + param_b * 0.4), 0.0), 10.0)


def calculate_composite_risk(factors: Dict[str, float]) -> float:
    """
    Calculate composite risk from multiple factors
    
    Args:
        factors: Dictionary of risk factors and their values
        
    Returns:
        Composite risk score (0-10 scale)
    """
    try:
        if not factors:
            return 5.0  # Default medium risk
        
        # Weighted average of all factors
        total_weight = 0.0
        weighted_sum = 0.0
        
        for factor_name, value in factors.items():
            # Simple weighting (can be customized)
            weight = 1.0 / len(factors)
            weighted_sum += value * weight
            total_weight += weight
        
        if total_weight > 0:
            result = weighted_sum / total_weight
        else:
            result = 5.0
        
        return min(max(result, 0.0), 10.0)
    except Exception:
        return 5.0