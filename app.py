from copyreg import pickle
from types import new_class
import streamlit as st
import pandas as pd
import requests
import pickle
import numpy as np
# Security

# passlib,hashlib,bcrypt,scrypt
import hashlib


def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()


def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False


# DB Management
import sqlite3

conn = sqlite3.connect('data1.db')
c = conn.cursor()


# DB  Functions
def create_usertable():
    c.execute('CREATE TABLE IF NOT EXISTS userstable(username TEXT,password TEXT)')


def add_userdata(username, password):
    c.execute('INSERT INTO userstable(username,password) VALUES (?,?)', (username, password))

    conn.commit()


def login_user(username, password):
    c.execute('SELECT * FROM userstable WHERE username =? AND password = ?', (username, password))
    data = c.fetchall()
    if data == []:
        return False
    else:
        return True


def view_all_users():
    c.execute('SELECT * FROM userstable')
    data = c.fetchall()
    return data


def check_user(username):
    c.execute('SELECT * FROM userstable WHERE username =?', (username,))
    data = c.fetchall()
    if data == []:
        return True
    else:
        return False


def main():
    st.title("Movie Recommendation System")

    menu = ["Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":

        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.checkbox("Login"):
            flag = login_user(username, make_hashes(password))
            view_all_users()
            if flag == True:
                def fetch_poster(movie_id):
                    response = requests.get(
                        'https://api.themoviedb.org/3/movie/{}?api_key=8f4f2c3f1ca1ca155b60ba9f2ceabc92&language=en-US'.format(
                            movie_id))
                    data = response.json()

                    return "https://image.tmdb.org/t/p/w500/" + data['poster_path']

                def recommend(movie):
                    movie_index = movies[movies['title'] == movie].index[0]
                    distances = similarity[movie_index]
                    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[1:6]

                    recommended_movies = []
                    recommended_movies_posters = []
                    for i in movies_list:
                        movie_id = movies.iloc[i[0]].movie_id
                        # fetch_posters from API
                        recommended_movies.append(movies.iloc[i[0]].title)
                        recommended_movies_posters.append(fetch_poster(movie_id))
                    return recommended_movies, recommended_movies_posters

                movies_dict = pickle.load(open('movies_dict.pkl', 'rb'))
                movies = pd.DataFrame(movies_dict)

                similarity = pickle.load(open('similarity.pkl', 'rb'))
                selected_movie_name = st.selectbox('Enter Movie Name', movies['title'].values)

                if st.button('Recommend'):
                    names, posters = recommend(selected_movie_name)

                    col1, col2, col3, col4, col5 = st.columns(5)
                    with col1:
                        st.text(names[0])
                        st.image(posters[0])
                    with col2:
                        st.text(names[1])
                        st.image(posters[1])
                    with col3:
                        st.text(names[2])
                        st.image(posters[2])
                    with col4:
                        st.text(names[3])
                        st.image(posters[3])
                    with col5:
                        st.text(names[4])
                        st.image(posters[4])
            else:
                st.error("Enter the valid Username or password")
    elif choice == "SignUp":
        st.subheader("Create New Account")
        new_user = st.text_input("Username")
        new_password = st.text_input("Password", type='password')

        if st.button("Signup"):
            create_usertable()

            flag = check_user(new_user)
            if flag == False:
                st.error("The name already has been taken")
                st.error("Pls enter the new name or login with name and ")

            else:
                add_userdata(new_user, make_hashes(new_password))
                st.success("You have successfully created a valid Account")
                st.info("Go to Login Menu to login")


if __name__ == '__main__':
    main()
