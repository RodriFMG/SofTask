from flask import Flask, render_template, request, jsonify
import requests
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)
apikey = "a700c8ac"

def searchfilms(search_text):
    url = f"https://www.omdbapi.com/?s={search_text}&apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data.get("Search", [])
    else:
        print("Failed to retrieve search results.")
        return None

def getmoviedetails(movie_id):
    url = f"https://www.omdbapi.com/?i={movie_id}&apikey={apikey}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None

def get_country_flag(fullname):
    url = f"https://restcountries.com/v3.1/name/{fullname}?fullText=true"
    response = requests.get(url)
    if response.status_code == 200:
        country_data = response.json()
        if country_data:
            return country_data[0].get("flags", {}).get("svg", None)
    print(f"Failed to retrieve flag for country: {fullname}")
    return None

def gather_movie_data(movie):
    details = getmoviedetails(movie["imdbID"])
    if not details:
        return None

    countries = details.get("Country", "").split(", ")
    countries_with_flags = [
        {"name": country.strip(), "flag": get_country_flag(country.strip())}
        for country in countries
    ]

    return {
        "title": details.get("Title", "N/A"),
        "year": details.get("Year", "N/A"),
        "countries": countries_with_flags
    }

def merge_data_with_flags(filter_text):
    movies = searchfilms(filter_text)
    if not movies:
        return []

    with ThreadPoolExecutor() as executor:
        movies_data = list(executor.map(gather_movie_data, movies))

    return [movie for movie in movies_data if movie is not None]

@app.route("/")
def index():
    filter_text = request.args.get("filter", "").upper()
    movies = merge_data_with_flags(filter_text)
    return render_template("index.html", movies=movies)

@app.route("/api/movies")
def api_movies():
    filter_text = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter_text))

if __name__ == "__main__":
    app.run(debug=True)
