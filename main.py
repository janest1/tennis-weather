import os
from dotenv import load_dotenv
import requests
from fastapi import FastAPI
from openai import OpenAI


load_dotenv()
app = FastAPI()

weather_url = "http://api.weatherapi.com/v1"
weather_api_key = os.getenv("WEATHER_API_KEY")


@app.get("/")
def root():
    return {"message": "hello"}


def get_forecast(date: str, city: str):
    url = f"{weather_url}/forecast.json"
    data = {
        "key": weather_api_key,
        "q": city,
        "dt": date
    }

    resp = requests.post(url, params=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": "Failed to fetch weather data"}


@app.get("/get_current_weather/{city}")
def get_current_weather(city: str):
    url = f"{weather_url}/current.json"
    data = {
        "key": weather_api_key,
        "q": city
    }
    resp = requests.post(url, params=data)
    if resp.status_code == 200:
        return resp.json()
    else:
        return {"error": "Failed to fetch weather data"}


@app.post("/schedule_game/{city}")
def schedule_game(city: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    tools = [
        {
            "type": "function",
            "function": {
                "name": "get_current_weather",
                "description": "Get the day's weather for a specific location",
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
                    "required": ["location"],
                    "additionalProperties": False
                },
                "strict": True
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_forecast",
                "description": "Get the weather forecast for the next 5 days",
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
        }
    ]

    messages = [
        {"role": "system", "content": "You are an assistant that helps people schedule tennis games based on the weather"},
        {"role": "user", "content": f"Can I play tennis outside in {city} today?"}
    ]
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        tools=tools
    )
    print(completion)

    tool_calls = completion.choices[0].message.tool_calls

