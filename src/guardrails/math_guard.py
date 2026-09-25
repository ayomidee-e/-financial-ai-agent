import re
from langchain_core.tools import tool

@tool
def strict_financial_calculator(expression: str) -> str:
    """ONLY use this for ALL math. Supports +, -, *, /, and %."""
    # Strip any non-math characters to prevent code injection
    clean_expr = re.sub(r'[^0-9+\-*/().%]', '', expression)
    if not clean_expr:
        return "Error: Invalid mathematical expression."
    try:
        # Use evaluator
        import numexpr as ne
        return str(ne.evaluate(clean_expr))
    except Exception as e:
        return f"Calculation Error: {str(e)}"