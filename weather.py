import requests

API_KEY = "6283b672bcbaf50d81f928bf6d18e66b"


def get_weather(city):

    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?q={city}&appid={API_KEY}&units=metric"
    )

    try:

        response = requests.get(url)

        data = response.json()

        # DEBUG: show API response in terminal
        print("WEATHER API RESPONSE:")
        print(data)

        if data.get("cod") != 200:

            return f"Weather API Error: {data}"

        temp = data["main"]["temp"]

        feels_like = data["main"]["feels_like"]

        humidity = data["main"]["humidity"]

        description = data["weather"][0]["description"]

        return (
            f"In {city}, the temperature is {temp} degrees Celsius. "
            f"It feels like {feels_like} degrees. "
            f"The weather is {description}. "
            f"Humidity is {humidity} percent sir."
        )

    except Exception as e:

        return f"Weather Error: {e}"