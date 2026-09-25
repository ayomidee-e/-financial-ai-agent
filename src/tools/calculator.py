import numexpr as ne
from langchain_core.tools import tool

@tool
def safe_calculator(expression: str) -> str:
    """Evaluates a mathematical expression safely. Use this for all financial math."""
    try:
        # numexpr for math
        result = ne.evaluate(expression)
        return str(result)
    except Exception as e:
        return f"Error in calculation: {str(e)}"