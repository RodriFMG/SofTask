import json
import sqlite3
import requests

apikey = "a700c8ac"


def create_database():
    db = sqlite3.connect('cache.db')
    c = db.cursor()
    try:
        c.execute('''
                CREATE TABLE IF NOT EXISTS SeriePelicula(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    NameSerie TEXT NOT NULL UNIQUE
            )

            ''')

        c.execute('''
                CREATE TABLE IF NOT EXISTS Pelicula(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    NamePelicula TEXT NOT NULL,
                    Year INTEGER NOT NULL,
                    SerieId INTEGER,
                    FOREIGN KEY (SerieId) REFERENCES SeriePelicula (id)
                )
        ''')

        c.execute('''
                CREATE TABLE IF NOT EXISTS FlagCountry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    NameCountry TEXT NOT NULL,
                    ImgFlag TEXT NOT NULL
                )
        ''')

        c.execute('''
                CREATE TABLE IF NOT EXISTS FlagsMovie (
                    idMovie INTEGER,
                    idFlag INTEGER,
                    PRIMARY KEY (idMovie, idFlag),
                    FOREIGN KEY (idMovie) REFERENCES Pelicula (id),
                    FOREIGN KEY (idFlag) REFERENCES FlagCountry (id)
                )
        ''')
        db.commit()
        print("Tablas y bdd creadas correctamente")
    except Exception as e:
        print("Error en crear las tablas: ", e)
        db.rollback()
    finally:
        c.close()
        db.close()


def FetchAPI(SeriePelis):
    db = sqlite3.connect('cache.db')
    c = db.cursor()

    url = "https://www.omdbapi.com/?s=" + SeriePelis + "&apikey=" + apikey
    response = requests.get(url)

    try:
        if response.status_code == 200:

            try:
                c.execute('INSERT INTO SeriePelicula (NameSerie) VALUES (?)',
                          (SeriePelis,))
                db.commit()

                #Commit para qe salte el error si se inserta una Serie ya existente
                # ya que ese parámetro está colocado como UNIQUE.

            except sqlite3.IntegrityError:

                print("Ya se tiene registro de todas las peliculas de esa serie o saga.")
                return

            idSerie = c.lastrowid # Rescata el ID de la última inserción
            dataPelis = response.json() # El content rescatado del API lo transforma en formato JSON

            for Peli in dataPelis["Search"]:

                c.execute('INSERT INTO Pelicula (NamePelicula, Year, SerieId) VALUES (?,?,?)',
                          (Peli["Title"], Peli["Year"], idSerie))

                idPeli = c.lastrowid
                urlDetails = "https://www.omdbapi.com/?i=" + Peli["imdbID"] + "&apikey=" + apikey

                responseDetails = requests.get(urlDetails)

                if responseDetails.status_code == 200:
                    dataDetails = responseDetails.json()
                    countries = dataDetails.get("Country", "").split(", ")

                    for FlagCountry in countries:

                        nameCountry = FlagCountry

                        if nameCountry == "USA":
                            nameCountry = "United States"
                        elif nameCountry == "N/A":
                            nameCountry = "United States" # Para que no salga el error por esto ;b

                        urlFlag = f"https://restcountries.com/v3.1/name/{nameCountry}?fullText=true"
                        responseFlag = requests.get(urlFlag)

                        if responseFlag.status_code == 200:

                            dataFlag = responseFlag.json()

                            imgFlag = dataFlag[0]["flags"]["svg"]

                            c.execute('INSERT INTO FlagCountry (NameCountry, ImgFlag) VALUES (?, ?)',
                                      (nameCountry, imgFlag))

                            idFlag = c.lastrowid

                            c.execute('INSERT INTO FlagsMovie (idMovie, idFlag) VALUES (?, ?)',
                                      (idPeli, idFlag))
                        else:
                            print(f"Error al obtener la bandera para {nameCountry}."
                                  f"De la Peli: ", Peli["Title"], "  con id: ", Peli["imdbID"])

                else:
                    print("Error en la respuesta de la API.")
            db.commit()
            print("Se insertaron correctamente los datos")
        else:
            print("Error en la respuesta de la API.")
    except Exception as e:
        print(f"Error al realizar operaciones: {e}")
        db.rollback()
    finally:
        c.close()
        db.close()


def GetAll():

    db = sqlite3.connect('cache.db')
    c = db.cursor()

    c.execute('SELECT * FROM Pelicula')

    result = c.fetchall() # para rescatar la información de la ejecución.

    return result
