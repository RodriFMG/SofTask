from flask import Flask, render_template, request, jsonify
import requests
import json

app = Flask(__name__)
apikey = "a700c8ac"

def searchfilms(search_text):
    url = "https://www.omdbapi.com/?s=" + search_text + "&apikey=" + apikey
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        print("Failed to retrieve search results.")
        return None
    
def getmoviedetails(movie):
    url = "https://www.omdbapi.com/?i=" + movie["imdbID"] + "&apikey=" + apikey
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
        # Si country data existe pues retorna su value.
        if country_data:
            return country_data[0].get("flags", {}).get("svg", None)
    print(f"Failed to retrieve flag for country code: {fullname}")
    return None

def merge_data_with_flags(filter):

    # Apartir de un tipo, encuentras las peliculas que sean de ese tipo, o la pelicula en cuestion
    # (no estoy seguro)
    filmssearch = searchfilms(filter)

    #
    moviesdetailswithflags = []

    # Itera todas las peliculas que se encontró en el filtro.
    for movie in filmssearch["Search"]:

        # Cada pelicula, encuentro los detalles
         moviedetails = getmoviedetails(movie)

        # Cada pelicula, encuentro sus paises articies.
         countriesNames = moviedetails["Country"].split(",")

        # Restaca todas las bandera de los detalles de los paises correspondientes en la pelicula.
         countries = []

        # De cada country rescata su nombre, y apartir del nombre, en una API resacata la img de la bandera.
         for country in countriesNames:
            countrywithflag = {
                "name": country.strip(),
                "flag": get_country_flag(country.strip())
            }
            countries.append(countrywithflag)

        #Rescata los detalles findamentales que se necesitan de la pelicula. Año, pais y paises usados.
         moviewithflags = {
            "title": moviedetails["Title"],
            "year": moviedetails["Year"],
            "countries": countries
         }

        # Por cada país del filtro, todos esos detalles y paises, se rescata y se coloca en un contendor
         moviesdetailswithflags.append(moviewithflags)

    return moviesdetailswithflags

@app.route("/")
def index():

    # Rescata los argumentos en minuscula del RIQUEST
    filter = request.args.get("filter", "").upper()

    # RENDERIZA HTTP rescatado.
    return render_template("index.html", movies = merge_data_with_flags(filter))

@app.route("/api/movies")
def api_movies():

    # RESCATA LOS ARGUMENTOS DEL FILTRO REALIZADO.
    filter = request.args.get("filter", "")

    # TODO LO RESCATADO, LO COLECCIONA Y RETORNA EN FORMATO JSON.
    return jsonify(merge_data_with_flags(filter))    

if __name__ == "__main__":
    app.run(debug=True)

