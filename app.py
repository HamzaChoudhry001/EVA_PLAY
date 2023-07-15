import sqlite3
from allFunctions import *
from SqlQuery import *
from flask import Flask, redirect, render_template, request, jsonify, url_for, session, flash
import requests
from flask_mail import Mail, Message
import numpy as np
import pandas as pd
import nltk
import pickle
import sklearn
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
ps = PorterStemmer()

def signup_user_to_db(email, password, mobile):
    con = db_connection("users")
    cur = con.cursor()
    # Check if the email already exists
    cur.execute('SELECT email FROM users WHERE email=?', (email,))
    result = cur.fetchone()
    if result:
        # Email already exists, return error message
        con.close()
        return "Sorry, this email is already registered."
    # Insert the user into the database
    cur.execute('INSERT INTO users(email,password,mobile) values (?,?,?)', (email, password, mobile))
    con.commit()
    con.close()
    return None

app = Flask(__name__)
app.secret_key = "rhhah_d"
# Mail Config
app.config['MAIL_SERVER'] = 'smtp.googlemail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'mu8027641@gmail.com'
app.config['MAIL_PASSWORD'] = 'wqtg ykzx erfl hlkb'
mail = Mail(app)

# Home page
@app.route('/')
def index():
    return render_template("index.html")

# Sigup page
@app.route('/signup', methods=["POST", "GET"])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        mobile = request.form['mobile']
        if signup_user_to_db(email, password, mobile):
            flash('Account already registered!', 'error')
            return redirect(url_for('signup'))
        else:
            return render_template('signin.html')  
    else:
        return render_template('signup.html')

# Signin page
@app.route('/signin', methods=["POST", "GET"])
def signin():   
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == 'admin@evastream.com' and password == 'admin':
            return redirect(url_for('admin'))
        # connection
        con = db_connection("users")
        cur = con.cursor()
        cur.execute('Select email,password FROM users WHERE email=? and password=?', (email, password))
        result = cur.fetchone()
        if result:
            session['email'] = email
            return redirect(url_for('recommendations'))
        else:
            flash('Incorrect email or password', 'error')
            return redirect(url_for('signin'))    
    else:
        return render_template("signin.html")



# --------------------------------
# fetch movies data
global movies_result
conn = db_connection("pk_moviesnew")
cursor = conn.cursor()
cursor.execute(FETCH_ALL_MOVIES)
movies_result = cursor.fetchall()
conn.close()

@app.route('/getByGenre', methods=['GET', 'POST'])
def getByGenre():
    genre = request.form["genre"]
    genre_movies, genre_posters, years = get_genre(genre, movies_result)
    response = {"genre_movies": genre_movies}, {"genre_posters": genre_posters} , {"years": years}
    return jsonify(response)

@app.route('/getByYear', methods=['GET', 'POST'])
def getByYear():
    year = request.form["year"]
    year_movies, year_posters, yeard = get_year(year, movies_result)
    response_data = {"year_movies": year_movies}, {
        "year_posters": year_posters}, {"yeard": yeard}
    return jsonify(response_data)

# Recommendations page
@app.route('/recommendations', methods=['GET', 'POST'])
def recommendations():
    if "email" in session:
        genre_movies, genre_posters, years = get_genre("Action", movies_result)
        year_movies, year_posters, yeard = get_year("2022", movies_result)
        p_movies, p_posters, des, tagline, date = get_top(movies_result)
        return render_template("recommendations.html",movie_names=movie_names,movie_data=movie_infos, genre_movies=genre_movies,rec_yeard=yeard, rec_year=years, year_movies=year_movies, p_movies=p_movies, genre_posters=genre_posters, year_posters=year_posters, p_posters=p_posters, des=des, tagline=tagline, date=date)
    else:
        print("Session not found")
        return redirect(url_for("signin"))

movie_names = []
for row in movies_result:
    movie_names.append((row[2]))
    
movie_info = []
for row in movies_result:
    movie_info.append((row[7]))

movie_infos = []
for nameX, yearX in zip(movie_names, movie_info):
    movie_infos.append((nameX, yearX))

# Function to fetch movie details
def fetch_movie_details(movie_name, release_year):
    url = f"https://api.themoviedb.org/3/search/movie?api_key=0491d25d16d6fd177ba696230c2710b5&query={movie_name}"
    response = requests.get(url)
    if response.status_code == 200:
        search_results = response.json()
        matching_movies = [movie for movie in search_results["results"] if movie["release_date"].startswith(str(release_year))]
        if matching_movies:
            movie_id = matching_movies[0]["id"]
            if fetch_movie_details_by_id(movie_id):
                return True
        else:
            print("No movie found with the given name and release year")
            return False    
    else:
        print("Failed to fetch movie details")
        return False

# Function to fetch movie details by movie ID
def fetch_movie_details_by_id(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key=0491d25d16d6fd177ba696230c2710b5&append_to_response=credits,keywords"
    response = requests.get(url)
    if response.status_code == 200:
        movie_data = response.json()
        movie_title = movie_data["title"]
        movie_genres = [genre["name"] for genre in movie_data["genres"]]
        movie_overview = movie_data["overview"]
        movie_tagline = movie_data["tagline"]
        movie_keywords = [keyword["name"] for keyword in movie_data["keywords"]["keywords"]]
        cast_members = movie_data["credits"]["cast"][:4]
        cast_names = [cast["name"] for cast in cast_members]
        crew_members = movie_data["credits"]["crew"]
        director = next((crew["name"] for crew in crew_members if crew["job"] == "Director"), "")
        release_year = movie_data["release_date"].split("-")[0]
        popularity = movie_data["popularity"]
        poster_path = f"https://www.themoviedb.org/t/p/original{movie_data['poster_path']}" if movie_data['poster_path'] else ""
        movie_id = movie_data["id"]
        newgenre = "$".join(movie_genres)
        newcast = "$".join(cast_names)
        # 
        conn = db_connection("pk_popularnew")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pk_popularnew WHERE movie_id=?", (movie_id,))
        if cursor.fetchone() is None:
            cursor.execute("SELECT COUNT(*) FROM  pk_popularnew")
            total_movies = cursor.fetchone()[0]
            cursor.execute("INSERT INTO pk_popularnew (movie_index, movie_id, title, genres, release_date, popularity, cast) VALUES (?,?, ?, ?, ?, ?, ?)",
                           (total_movies, movie_id, movie_title, newgenre, release_year, popularity, newcast))
            conn.commit()
            print("Movie details added to the database.")
        else:
            print("Movie already exists in the database.")
        conn.close()
        # 
        conn = db_connection("pk_moviesnew")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM pk_moviesnew WHERE movie_id=?", (movie_id,))
        if cursor.fetchone() is None:
            cursor.execute("SELECT COUNT(*) FROM  pk_moviesnew")
            total_movies = cursor.fetchone()[0]
            cursor.execute("INSERT INTO pk_moviesnew (movie_index, movie_id, title, tagline, overview, genres, popularity, release_date, poster_path, cast) VALUES (?,?, ?, ?, ?, ?, ?,?,?,?)",
                           (total_movies, movie_id, movie_title, movie_tagline, movie_overview, newgenre, popularity, release_year, poster_path, newcast))
            conn.commit()
            movie_names.append(movie_title)
            movie_info.append(release_year)
            # for nameX, yearX in zip(movie_names, movie_info):
            movie_infos.append((movie_title, release_year))
            # movie_infos[movie_title] = release_year
            print("Movie details added ALL to the database.")
        else:
            print("Movie already exists aLL in the database.")
        conn.close()

        # Join all details with spaces
        tag = " ".join([movie_title] + movie_genres + [movie_overview] + movie_keywords + cast_names + [director])
        def stem(text):
            y=[]
            for i in text.split():
                y.append(ps.stem(i))
            return " ".join(y)
        newtag = stem(tag)
        # 
        conn = db_connection("data_moviesnew")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM data_moviesnew WHERE movie_id=?", (movie_id,))
        if cursor.fetchone() is None:
            cursor.execute("SELECT COUNT(*) FROM  data_moviesnew")
            total_movies = cursor.fetchone()[0]
            cursor.execute("INSERT INTO data_moviesnew (movie_index, movie_id, title, tags) VALUES (?,?,?,?)",
                           (total_movies, movie_id, movie_title, newtag))
            conn.commit()
            print("Movie tags details added to the database.")
        else:
            print("Movie tags already exists in the database.")
            return False
        conn.close()
    else:
        print("Failed to fetch movie details.")
        return False
    # Load the existing movie.pkl file into a DataFrame
    try:
        df = pd.read_pickle("./model/data/data_moviesnew.pkl")
    except FileNotFoundError:
        df = pd.DataFrame(columns=["movie_id", "title", "tags"])
    # Check if the movie_id already exists in the DataFrame
    if movie_id in df["movie_id"].values:
        print("Movie record already exists.")
        return
    # Append the new movie record to the DataFrame
    new_row = pd.DataFrame([[movie_id, movie_title, newtag]], columns=["movie_id", "title", "tags"])
    df = pd.concat([df, new_row], ignore_index=True)
    # Save the updated DataFrame back to the movie.pkl file
    df.to_pickle("./model/data/data_moviesnew.pkl")
    print("Movie record added successfully.")
    
    return newtag

# fetch_movie_details("Moana", 2009)
def train(name, year):
    if not fetch_movie_details(name, year):
        return False
    df = pd.read_pickle("./model/data/data_moviesnew.pkl")
    # Get the tags column
    tags = df["tags"]
    # Initialize the CountVectorizer
    cv = CountVectorizer(max_features=8000, stop_words='english')
    # Perform vectorization on the tags column
    vectors = cv.fit_transform(tags).toarray()
    pickle.dump(vectors, open('./model/data/vectors.pkl','wb'))
    with open("./model/data/vectors.pkl", "wb") as f:
        pickle.dump(vectors, f)
    print(vectors)  
    similarity = cosine_similarity(vectors)
    # Save the updated similarity matrix to the similarity.pkl file
    with open("./model/data/data_similaritynew.pkl", "wb") as f:
        pickle.dump(similarity, f)
    print("Similarity matrix updated and saved successfully.")
    return True

def get_movie_id(tit , year):
    conn = sqlite3.connect('./model/data/pk_moviesnew.sqlite')
    cursor = conn.cursor()
    cursor.execute("SELECT movie_id FROM pk_moviesnew WHERE title=? and release_date=?", (tit,year,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result
    else:
        return None

def recommends(movie, year):
        id = get_movie_id(movie, year)
        movies= pickle.load(open('./model/data/data_moviesnew.pkl', 'rb'))
        similarity = pickle.load(open('./model/data/data_similaritynew.pkl', 'rb'))
        index = movies[(movies['title']==movie) & (movies['movie_id']==id)].index[0]
        distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
        recommend_title = []
        recommend_poster = []
        for i in distances[0:7]:
            movie_id = movies.iloc[i[0]].movie_id
            recommend_poster.append(fetchPoster(movie_id, movies_result))
            recommend_title.append(movies.iloc[i[0]].title)
            print("SIMI",recommend_title," ",movie_id)  
        return recommend_title, recommend_poster

# recommends("Joy Ride", 2023)

# def recommends(movie):
#         movies= pickle.load(open('./model/data/data_moviesnew.pkl', 'rb'))
#         similarity = pickle.load(open('./model/data/data_similaritynew.pkl', 'rb')) 
#         index = movies[movies['title']==movie].index[0]
#         distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
#         recommend_title = []
#         recommend_poster = []     
#         for i in distances[0:7]:
#             movie_id = movies.iloc[i[0]].movie_id
#             recommend_poster.append(fetch_movie_poster(movie_id))
#             recommend_title.append(movies.iloc[i[0]].title)
#             print("SIMI",recommend_title," ",movie_id)  
#         return recommend_title, recommend_poster
# train("Transformers: Rise of the Beasts" , 2023)
# recommends("The Devil Conspiracy")

@app.route('/movie/<movie_name>/<movie_year>', methods=['GET', 'POST'])
def movie(movie_name,movie_year):
    global movie_id,movie_ide,movie_idx,title,year,over,tagline,recommend_title, recommend_poster 
    selected_movie = movie_name

    conn = db_connection("pk_moviesnew")
    cursor = conn.cursor()
    cursor.execute(FETCH_ALL_MOVIES)
    movies_resultx = cursor.fetchall()
    conn.close()
    for i in movies_resultx:
        if i[2] == selected_movie and i[7] == movie_year:
            movie_idx = i[0]
            movie_id = i[1]
            tagline = i[3]
            over = i[4]
            year = i[7]
            title = i[2]
            # movie_poster = i[8]
            break
    for row in movies_resultx:
        if row[1] == movie_id:
            movie_ide = row[1]
            break  
    trailer_key = get_trailer(movie_ide)
    # print("trailer_key", trailer_key)
    movie_poster = fetchPoster(movie_ide, movies_resultx)
    recommend_title, recommend_poster = recommends(movie_name,year)
    # extract the titles of the recommended movies
    recommended_titles = recommend_title
    # create an empty list to store the years of the recommended movies
    recommended_years = []
    # iterate over each recommended movie title
    for titled in recommended_titles:
        # search for the movie in the movies_result dictionary
        for movied in movies_resultx:
            # check if the current movie has the same title as the recommended movie
            if movied[2] == titled:
                # if it does, add the movie's year to the recommended_years list
                recommended_years.append(movied[7])
                # break out of the inner loop since we've found the movie we're looking for
                break

    # print the years of the recommended movies
    # print(recommended_years)
    mov_genre = []
    mov_cast = []
    for row in movies_resultx:
        mg = list(row[5].split("$"))
        mov_genre.append(mg)
        mc = list(row[9].split("$"))
        mov_cast.append(mc)
              
    return render_template("movie.html",movie_names=movie_names,movie_data=movie_infos ,movie_name=movie_name, movie_idx=movie_idx, movie_poster=movie_poster, mov_genre=mov_genre, mov_cast=mov_cast, tagline=tagline, over=over, year=year,trailer_key=trailer_key,recommend_title=recommend_title, recommend_poster= recommend_poster,rec_year=recommended_years)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        name = request.form['text']
        year = request.form['year']
        if train(name, year):
            flash("Movie record added successfully.", "success")
        else:
            flash("Movie record already exists.", "error")
    return render_template("admin.html")

@app.route('/update-popularity', methods=['POST'])
def update_popularity():
    from_year = request.form['year1']
    to_year = request.form['year2']
    update_status = update_movie_popularity(from_year, to_year)
    if update_status:
        flash('Records updated successfully', 'success')
    else:
        flash('Records could not be updated', 'error')
    return redirect(url_for('admin')) 
   
# Forget page
@app.route('/forget', methods=["POST", "GET"])
def forget():
    global e 
    if request.method == 'POST': 
        email = request.form['email']
        mobile = request.form['mobile']
        # connection
        con = db_connection("users")
        cur = con.cursor()
        cur.execute('Select email, mobile FROM users WHERE email=? and mobile=?', (email, mobile))
        result = cur.fetchone()
        if result:
            e = result[0]
            return redirect(url_for('reset'))
        else:
            flash('Incorrect email or mobile number', 'error')
            return redirect(url_for('forget'))
    else:
        return render_template('forget.html')

# Reset page
@app.route('/reset', methods=["POST", "GET"])
def reset():
    if request.method == 'POST':
        password1 = request.form['password1']
        password2 = request.form['password2']
        if password1 == password2:
            # connection
            con = db_connection("users")
            cur = con.cursor()
            cur.execute("UPDATE users SET password = ? WHERE email = ?", (password1, e))
            con.commit()
            con.close()
            flash("Password Changed Successfully")
            return redirect(url_for('reset'))
        else:
            flash("What?! Mismatched Passwords? ")
            return redirect(url_for('reset')) 
    else:
        return render_template('reset.html')

#Contact Page
@app.route('/contactus', methods=["POST", "GET"])  
def contactus():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        message = request.form['message']
        msg = Message('Contact from website', sender='email', recipients=['mu8027641@gmail.com'])
        msg.body = f'Name: {name}\nEmail: {email}\nMessage: {message}'
        mail.send(msg)
        return redirect('/contactus', code=302)

    else:
        return render_template('contactus.html')

#About Us Page
@app.route('/aboutus')  
def aboutus():
    # connection
    con = db_connection("users")
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total_users = cur.fetchone()[0]
    con.close()

    # connection
    conn = db_connection("pk_moviesnew")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM  pk_moviesnew")
    total_movies = cursor.fetchone()[0]
    conn.close()
    return render_template('aboutus.html', total_users=total_users, total_movies=total_movies)
     
# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=1000)
