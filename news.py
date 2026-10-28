import requests

API_KEY = "3260021bf58b4038b464ca4b0c8709d7"


def get_news():

    url = (
        f"https://newsapi.org/v2/top-headlines"
        f"?country=in&apiKey={API_KEY}"
    )

    try:

        response = requests.get(url)

        data = response.json()

        print("NEWS API RESPONSE:")
        print(data)

        if data.get("status") != "ok":

            return f"News API Error: {data}"

        articles = data.get("articles", [])[:5]

        if not articles:

            return "No news articles found sir"

        headlines = []

        for article in articles:

            headlines.append(article["title"])

        return (
            "Here are today's top Indian headlines sir. "
            + ". ".join(headlines)
        )

    except Exception as e:

        return f"News Error: {e}"