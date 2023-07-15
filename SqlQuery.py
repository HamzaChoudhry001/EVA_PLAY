import sqlite3
FETCH_ALL_MOVIES = "Select * from pk_moviesnew"
FETCH_GENRES_POPULAR = "Select movie_id, genres FROM pk_popularnew ORDER BY popularity DESC"
FETCH_DATE_POPULAR = "Select movie_id, release_date from pk_popularnew"
Fetch_top = "SELECT movie_id, popularity FROM pk_moviesnew ORDER BY popularity DESC LIMIT 5"
# SELECT * FROM popular088 ORDER BY popularity DESC
Tags = "Select * from data_moviesnew"





