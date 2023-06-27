import zipfile
import os
import requests
import pandas as pd
from flask import Flask, request, render_template, session

app = Flask(__name__) 
app.secret_key = 'your_secret_key'

def fetch_poster(movie_id):
    url = "https://api.themoviedb.org/3/movie/{}?api_key=8265bd1679663a7ea12ac168da84d2e8&language=en-US".format(movie_id)
    data = requests.get(url)
    data = data.json()
    poster_path = data['poster_path']
    full_path = "https://image.tmdb.org/t/p/w500/" + poster_path
    return full_path

def recommend(movie):
    # Load the movies data from the movies_list.pkl file
    movies = pd.read_pickle('model/movies_list.pkl')

    index = movies[movies['title'] == movie].index[0]
    # Add your recommendation logic here
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    recommended_movies_name = []
    recommended_movies_poster = []
    for i in distances[1:6]:
        movie_id = movies.iloc[i[0]].movie_id
        recommended_movies_poster.append(fetch_poster(movie_id))
        recommended_movies_name.append(movies.iloc[i[0]].title)

    return recommended_movies_name, recommended_movies_poster

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template("about.html")

@app.route('/contact')
def contact():
    return render_template("contact.html")

@app.route('/recommendation', methods=['GET', 'POST'])
def recommendation():
    # Load the movies data from the movies_list.pkl file
    movies = pd.read_pickle('model/movies_list.pkl')

    movie_list = movies['title'].values
    status = False
    if request.method == "POST":
        try:
            if request.form:
                movie_name = request.form['movies']
                session['selected_movie'] = movie_name
                recommended_movies_name, recommended_movies_poster = recommend(movie_name)
                status = True
                return render_template("prediction.html", movies_name=recommended_movies_name,
                                       poster=recommended_movies_poster, movie_list=movie_list, status=status)
        except Exception as e:
            error = {'error': e}
            return render_template("prediction.html", error=error, movie_list=movie_list, status=status)
    else:
        session.pop('selected_movie', None)
        return render_template("prediction.html", movie_list=movie_list, status=status) 

if __name__ == '__main__':
    # Specify the path to the zip file
    zip_file_path = 'model/similarity.zip'

    # Specify the filename of the similarity file within the zip file
    similarity_file = 'similarity.pkl'

    # Open the zip file
    with zipfile.ZipFile(zip_file_path, 'r') as zipf:
        # Extract the similarity file from the zip file
        zipf.extract(similarity_file, 'model/')

    # Load the similarity data from the extracted file
    similarity = pd.read_pickle(f'model/{similarity_file}')

    # Remove the extracted file
    os.remove(f'model/{similarity_file}')

    # Run the Flask application
    app.run(debug=True)
