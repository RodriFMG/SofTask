from flask import Flask, render_template, request, jsonify
from ConnectDB import create_database, FetchAPI
import sqlite3
import os

app = Flask(__name__)
apikey = "a700c8ac"
db = 'cache.db'

def CreateFilterInDB(filter):
    if not os.path.exists(db):
        create_database()

    DataBase = sqlite3.connect(db)
    c = DataBase.cursor()

    try:
        c.execute('SELECT * FROM SeriePelicula WHERE NameSerie = ?', (filter,))
        ExistsFilter = c.fetchall()

        if len(ExistsFilter) == 0:
            print(f"El filtro {filter} no se tenía registrado. Rescatando e insertando contenido a la BDD...")
            FetchAPI(filter)
    except Exception as e:
        print("Error al momento de crear DB o verificar si el filtro existe.")
    finally:
        c.close()
        DataBase.close()

def merge_data_with_flags(filter):

    CreateFilterInDB(filter)

    DataBase = sqlite3.connect(db)
    c = DataBase.cursor()

    try:
        c.execute('''
            SELECT Pelicula.NamePelicula, Pelicula.Year, FlagCountry.NameCountry, FlagCountry.ImgFlag
            FROM Pelicula
            JOIN SeriePelicula ON Pelicula.SerieId = SeriePelicula.id
            LEFT JOIN FlagsMovie ON Pelicula.id = FlagsMovie.idMovie
            LEFT JOIN FlagCountry ON FlagsMovie.idFlag = FlagCountry.id
            WHERE SeriePelicula.NameSerie = ?
        ''', (filter,))
    except Exception as e:
        print("Error pipipi: ", e)
        return

    result = c.fetchall()
    pelicaulas = []

    for pelicula in result:

        title = pelicula[0]
        year = pelicula[1]
        country = pelicula[2]
        flag = pelicula[3]

        found = False
        for p in pelicaulas:
            if p["title"] == title:
                found = True
                p["countries"].append({
                    "name" : country,
                    "flag" : flag
                })
                break

        if not found:
            pelicaulas.append({
                "title" : title,
                "year" : year,
                "countries" : [{
                    "name" : country,
                    "flag" : flag
                }]
            })

    return pelicaulas


@app.route("/")
def index():
    filter = request.args.get("filter", "").upper()
    return render_template("index.html", movies = merge_data_with_flags(filter))

@app.route("/api/movies")
def api_movies():
    filter = request.args.get("filter", "")
    return jsonify(merge_data_with_flags(filter))



if __name__ == "__main__":
    app.run(debug=True)
