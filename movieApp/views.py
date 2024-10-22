from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
import sqlite3
import os
import base64
from django.urls import reverse
from django.core.files.storage import default_storage

def home(request):
    return render(request, 'home.html')

def register(request):
    if request.method == 'POST':
        userName = request.POST.get('username')
        Password = request.POST.get('password')
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'movies.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credentials WHERE username = ?", (userName,))
        existing_user = cursor.fetchone()    
        if existing_user:
            error_message = "Username already exists. Please choose a different username."
            return render(request, 'register.html', {'error_message': error_message})        
        cursor.execute("INSERT INTO credentials (username, password) VALUES (?, ?)", (userName, Password))
        conn.commit()
        conn.close()
        messages.success(request, "Account successfully created.")
        return redirect('/login/')
    return render(request, 'register.html')


def login(request):
    if request.method == 'POST':
        userName = request.POST.get('username')
        Password = request.POST.get('password')
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'movies.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM credentials WHERE username = ?", (userName,))
        user = cursor.fetchone()
        if user:
            stored_password = user[1]
            if stored_password == Password:
                request.session['username'] = userName
                request.session['password'] = stored_password
                return redirect('/dashboard/')
            else:
                error_message = "Invalid password. Please try again."
        else:
            error_message = "Username does not exist. Please register."
        return render(request, 'login.html', {'error_message': error_message})
    return render(request, 'login.html')



def dashboard(request):
    username = request.session.get('username', 'Guest')
    return render(request, 'dashboard.html', {'username': username})




def submit_movie(request):
    if request.method == 'POST':
        movie_name = request.POST.get('movie_name')
        poster = request.FILES.get('poster')
        description = request.POST.get('description')
        release_date = request.POST.get('release_date')
        cast = request.POST.get('cast')
        rating = request.POST.get('rating')
        category = request.POST.get('category')
        link = request.POST.get('link')
        if not all([movie_name, description, release_date, cast, rating, category, link]):
            return JsonResponse({"error": "All fields are required."}, status=400)
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'movies.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute("SELECT * FROM movie WHERE name = ?", (movie_name,))
            existing_movie = cursor.fetchone()
            if existing_movie:
                return JsonResponse({"error": "Movie with this name already exists."}, status=400)
            if poster:
                poster_blob = poster.read()
            else:
                return JsonResponse({"error": "Poster is required."}, status=400)
            cursor.execute("""
                INSERT INTO movie (name, poster, description, date, cast, rating, category, links)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (movie_name, poster_blob, description, release_date, cast, rating, category, link))
            conn.commit()
            return redirect(reverse('movie_list'))
        except sqlite3.Error as e:
            return JsonResponse({"error": f"Database error: {str(e)}"}, status=500)
        finally:
            conn.close()
    return JsonResponse({"error": "Only POST requests are allowed."}, status=405)



def movie_list(request):
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    db_path = os.path.join(root_dir, 'movies.db')
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name, category FROM movie")
    movies = cursor.fetchall()
    conn.close()
    movie_list = [{'name': movie[0], 'category': movie[1]} for movie in movies]
    return render(request, 'movie_list.html', {'movies': movie_list})


def movies(request):
    if request.method == 'POST':
        movie_name = request.POST.get('movie_name')
        root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        db_path = os.path.join(root_dir, 'movies.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM movie WHERE name = ?", (movie_name,))
        movie_details = cursor.fetchone()
        if movie_details:
            name, poster_blob, description, date, cast, rating, category, links = movie_details
            poster_base64 = base64.b64encode(poster_blob).decode('utf-8')
            poster_data_url = f"data:image/jpeg;base64,{poster_base64}"
            return render(request, 'movie_details.html', {
                'name': name,
                'poster': poster_data_url, 
                'description': description,
                'date': date,
                'cast': cast,
                'rating': rating,
                'category': category,
                'links': links,
            })