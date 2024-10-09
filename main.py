import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI
from openai import OpenAI


load_dotenv()
app = FastAPI()

weather_url = "http://api.weatherapi.com/v1"


def get_weather_data(date: str, zip_code: str):
    api_key = os.getenv("WEATHER_API_KEY")
    url = f"{weather_url}/future.json"
    data = {
        "key": api_key,
        "q": zip_code,
        "dt": date
    }

    resp = requests.post(url, params=data)
    return resp.json()


@app.post("/schedule")
def schedule_game(date: str, zip_code: str):
    client = OpenAI()
    assistant = client.beta.assistants.create(
        instructions="You are a weather bot. Use the provided functions to answer questions.",
        model="gpt-4o-2024-08-06",
        tools=[
            {
                "type": "function",
                "function": {
                    "name": "get_current_temperature",
                    "description": "Get the current temperature for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., San Francisco, CA"
                            },
                            "unit": {
                                "type": "string",
                                "enum": ["Celsius", "Fahrenheit"],
                                "description": "The temperature unit to use. Infer this from the user's location."
                            }
                        },
                        "required": ["location", "unit"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_rain_probability",
                    "description": "Get the probability of rain for a specific location",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "location": {
                                "type": "string",
                                "description": "The city and state, e.g., San Francisco, CA"
                            }
                        },
                        "required": ["location"],
                        "additionalProperties": False
                    },
                    "strict": True
                }
            }
        ]
    )

