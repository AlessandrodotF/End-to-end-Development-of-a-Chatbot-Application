import json
import os

from langchain.tools import tool
from pydantic import BaseModel

# some random tools
@tool("calculator",description="Performs arithmetic calculations. Use this for any math problems.",
)
def calc(expression: str) -> str:
    """Evaluate mathematical expressions."""
    return str(eval(expression))


@tool(
    "translator",
    description="Perform translation from Italian into English. Use this function for any translation problem.s",
)
def transl(expression: str) -> str:
    """Transalate from Italian into English."""
    return str(expression)


@tool
def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


