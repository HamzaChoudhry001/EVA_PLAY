from SqlQuery import *
import sqlite3
import requests

# Database connections
def db_connection(name):
    conn = None
    try:
        conn = sqlite3.connect("./model/data/"+name+".sqlite")
    except sqlite3.error as e:
        print(e)
    return conn



# Get poster image path
# def fetchPoster(movie_id, movies_result):
#     movie_idex = None
#     for row in movies_result:
#         if row[1] == movie_id:
#             movie_idex = row[0]
#             break
#     poster = movies_result[movie_idex][8]
#     return poster

def fetchPoster(movie_id, movies_result):
    movie_index = None
    for row in movies_result:
        if row[1] == movie_id:
            movie_index = row[0]
            break
    if movie_index is not None:
        poster = movies_result[movie_index][8]
        return poster
    else:
        return None

# Get most popular movies based on genre
def get_genre(genre, movies_result):
    counter = 0
    genre_movies = []
    genre_posters = []
    years = []
    # FETCH_GENRES_POPULAR = "Select movie_id, genres from popular"
    conn = db_connection("pk_popularnew")
    cursor = conn.cursor()
    cursor.execute(FETCH_GENRES_POPULAR)
    results = cursor.fetchall()
    # print("Res: ",results) //(157354, 'Comedy$Drama')
    for row in results:
        if counter != 6:
            mov_gen = list(row[1].split("$"))
            for gen in mov_gen:
                if gen == genre: 
                    cursor.execute("Select title, release_date from pk_popularnew where movie_id = '"+str(row[0])+"'")
                    info = cursor.fetchall()
                    genre_movies.append(info[0][0])
                    years.append(info[0][1])
                    genre_posters.append(fetchPoster(row[0], movies_result))
                    counter += 1
                    break
        else:
            break
    return genre_movies, genre_posters , years

# Function to update movie popularity
def update_movie_popularity(from_year, to_year):
    conn = db_connection("pk_popularnew")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM pk_popularnew")
    movies = cursor.fetchall()
    
    con = db_connection("pk_moviesnew")
    cur = con.cursor()
    cur.execute("SELECT * FROM pk_moviesnew")
    movie = cur.fetchall()
    update_status = False
    for movie in movies:
        movie_id = movie[1]
        release_year = movie[4]  # Assuming the release year is stored in the second column
        if from_year <= release_year <= to_year:
            updated_popularity = fetch_updated_popularity(movie_id)
            if updated_popularity is not None:
                cursor.execute("UPDATE pk_popularnew SET popularity = ? WHERE movie_id = ?", (updated_popularity, movie_id))
                cur.execute("UPDATE pk_moviesnew SET popularity = ? WHERE movie_id = ?", (updated_popularity, movie_id))
                conn.commit()
                con.commit()
                update_status = True
            else:
                print(f"doesn't exist or couldn't be updated.")
    con.close()
    con.close()
    return update_status

# Function to fetch updated popularity from TMDB
def fetch_updated_popularity(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0491d25d16d6fd177ba696230c2710b5"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        updated_popularity = movie_data["popularity"]
        return updated_popularity
    else:
        print("Failed to fetch updated popularity.")

# Get most popular movies based on each year
def get_year(year , movies_result):
    counter = 0
    year_movies = []
    year_posters = []
    years = []
    conn = db_connection("pk_popularnew")
    cursor = conn.cursor()
    cursor.execute(FETCH_DATE_POPULAR)
    results = cursor.fetchall()

    for row in results:
        if counter != 6:
            if year == row[1]:
                # REPLACE(title, '''', '')
                cursor.execute("Select title, release_date from pk_popularnew where movie_id = '"+str(row[0])+"'")
                title = cursor.fetchall()
                year_movies.append(title[0][0])
                years.append(title[0][1])
                year_posters.append(fetchPoster(row[0], movies_result))
                # fetch_movie_poster(row[0])
                counter += 1
        else:
            break
    return year_movies, year_posters, years

# Get most top popular movies overall
def get_top(movies_result):
    counter = 0
    p_movies = []
    p_posters = []
    des = []
    tagline = []
    date = []
    conn = db_connection("pk_moviesnew")
    cursor = conn.cursor()
    cursor.execute(Fetch_top)
    result = cursor.fetchall()
    for row in result:
        if counter != 5:
                cursor.execute("Select title from pk_moviesnew where movie_id = '"+str(row[0])+"'")
                title = cursor.fetchall()
                p_movies.append(title[0][0])
                p_posters.append(fetchBackdrop(row[0]))
                cursor.execute("Select overview from pk_moviesnew where movie_id = '"+str(row[0])+"'")
                overview = cursor.fetchall()
                des.append(overview[0][0])
                cursor.execute("Select tagline from pk_moviesnew where movie_id = '"+str(row[0])+"'")
                tag = cursor.fetchall()
                tagline.append(tag[0][0])
                cursor.execute("Select release_date from pk_moviesnew where movie_id = '"+str(row[0])+"'")
                date_r = cursor.fetchall()
                date.append(date_r[0][0])
                counter += 1
        else:
            break
    return p_movies,p_posters,des,tagline,date

def fetchPosterB(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=0491d25d16d6fd177ba696230c2710b5&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/original" + str(data['poster_path'])

# Get Backdrop image path
def fetchBackdrop(movie_id):
    response = requests.get(
        'https://api.themoviedb.org/3/movie/{}?api_key=0491d25d16d6fd177ba696230c2710b5&language=en-US'.format(
            movie_id))
    data = response.json()
    return "https://image.tmdb.org/t/p/original"+str(data['backdrop_path'])

# Get poster image path
def fetch_movie_poster(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0491d25d16d6fd177ba696230c2710b5&append_to_response=images"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        if "images" in movie_data:
            images = movie_data["images"]["posters"] 
            if images:
                poster_path = images[0]["file_path"]  # Fetch the first poster
                poster_url = f"https://image.tmdb.org/t/p/w500/{poster_path}"
                return poster_url
    return None


def fetch_all_trailer_videos(movie_id):
    # Define TMDB API endpoint and parameters
    base_url = 'https://api.themoviedb.org/3'
    api_key = '0491d25d16d6fd177ba696230c2710b5' # Replace with your TMDB API key
    endpoint = f'{base_url}/movie/{movie_id}/videos'
    params = {'api_key': api_key}

    # Send request to TMDB API
    response = requests.get(endpoint, params=params)
    if response.status_code == 200:
        data = response.json()
        results = data.get('results', [])
        return results
    else:
        return None

def get_trailer(movie_id):
    # Fetch all trailer video keys
    results = fetch_all_trailer_videos(movie_id)
    if results:
        trailer_results = [result for result in results if result['type'].lower() == 'trailer' and result['site'].lower() == 'youtube' or result['type'].upper() == 'Trailer']
        num_trailers = len(trailer_results)
        if num_trailers > 0:
            # Find the middle trailer video key
            middle_index = num_trailers // 2
            video_key = trailer_results[middle_index]['key']
            return video_key
        else:
            # If no working trailer video key found, return None
            return None
    else:
        return None



