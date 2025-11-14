from fastapi import FastAPI, HTTPException, UploadFile, Depends, File, Form, Response, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import shutil
import os
from datetime import datetime

from models import Movie, LoginResponse, UserProfileResponse, UserDataResponse
from token_manager import token_manager
from auth import get_current_user, get_optional_user, valid_users

app = FastAPI()
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def hello():
    return HTMLResponse("""
    <html>
        <head>
            <title>Landing</title>
        </head>
        <body>
            <h1>Здравствуйте</h1>
            <h3>Это моё решение курса FastAPI. Результаты доступны по ссылкам ниже</h3>
            <ul>
                <li><a href="/study">Информация о фузе</a></li>
                <li><a href="/movietop">Список Фильмов</a></li>
                <li><a href="/movietop/Аватар">Конкретный фильм</a></li>
                <li><a href="/add">Добавление фильма</a></li>
                <li><a href="/login-form">Окно регистрации</a></li>
            </ul>
        </body>
    </html>
    """)

# А
html_data = """
    <html>
        <head>
            <title>Информация об обучении</title>
        </head>
        <body>
            <h1>БГИТУ</h1>
            <img src="/static/BGITU.jpg" width="40%" height="40%" alt="БГИТУ (поверьте на слово)">
            <ul>
                <li><strong>Город:</strong> Брянск</li>
                <li><strong>Адрес</strong> Станке-Димитрова 3</li>
                <li><strong>Специальность:</strong> ИВТ</li>
                <li><strong>Курс:</strong> 2</li>
            </ul>
            <a href="/">Вернуться на лендинг</a>
        </body>
    </html>
    """

@app.get("/study", response_class=HTMLResponse)
async def get_study_page():
    return HTMLResponse(html_data)

movies = [
    Movie(id=1, name="Аватар", cost=237, director="Джеймс Кэмерон"),
    Movie(id=2, name="Мстители: Финал", cost=356, director="Энтони и Джо Руссо"),
    Movie(id=3, name="Титаник", cost=200, director="Джеймс Кэмерон"),
    Movie(id=4, name="Звёздные войны: Пробуждение силы", cost=245, director="Дж. Дж. Абрамс"),
    Movie(id=5, name="Мстители: Война бесконечности", cost=316, director="Энтони и Джо Руссо"),
    Movie(id=6, name="Человек-паук: Нет пути домой", cost=200, director="Джон Уоттс"),
    Movie(id=7, name="Король Лев", cost=45, director="Джон Фавро"),
    Movie(id=8, name="Мстители", cost=220, director="Джосс Уидон"),
    Movie(id=9, name="Форсаж 7", cost=190, director="Джеймс Ван"),
    Movie(id=10, name="Холодное сердце 2", cost=150, director="Крис Бак и Дженнифер Ли")
]

@app.get("/movietop")
def all_movies():
    return movies

@app.get("/movietop/{input_name}")
def search_movie(input_name: str):
    for movie in movies:
        if input_name.lower() == movie.name.lower():
            return movie
    raise HTTPException(status_code=404, detail="Not Found")

# Б
@app.get("/add")
def form():
    return HTMLResponse("""
        <form method="post" action="/add" enctype="multipart/form-data">
            Название: <input name="name" required><br><br>
            Режиссёр: <input name="director" required><br><br>
            Бюджет: <input name="cost" type="number" step="0.1" required><br><br>
            Описание: <input name="description"><br><br>
            Номинация на "Оскар": <input name="oscar" type="checkbox" value="true"><br><br>
            Обложка: <input name="photo" type="file" accept="image/*" required><br><br>
            <button>Добавить фильм</button>
        </form>
        <br>
    """)

@app.post("/add")
async def add_movie(
    name: str = Form(...),
    director: str = Form(...),
    cost: float = Form(...),
    description: str = Form(None),
    oscar: bool = Form(False),
    photo: UploadFile = File(...)
):
    file_extension = photo.filename.split('.')[-1]
    photo_filename = f"movie_{len(movies) + 1}.{file_extension}"
    photo_path = f"static/{photo_filename}"

    with open(photo_path, "wb") as buffer:
        shutil.copyfileobj(photo.file, buffer)

    new_id = len(movies) + 1

    new_movie = Movie(
        name=name, 
        director=director, 
        cost=cost, 
        id=new_id, 
        oscar=oscar,
        photo=f"/{photo_path}",
        description=description
    )
    movies.append(new_movie)

    return HTMLResponse(f"""
    <html>
        <body style="text-align: center; padding: 20px;">
            <h1>Фильм добавлен!</h1>
            <h2>Название: {new_movie.name}</h2>
            <h2>Режиссёр: {new_movie.director}</h2>
            <h2>Бюджет: {new_movie.cost} шекелей</h2>
            <h2>Номинация на Оскар: {'Да' if new_movie.oscar else 'Нет'}</h2>
            {f'<h3>Описание: {new_movie.description}</h3>' if new_movie.description else ''}
            <img src="{new_movie.photo}" alt="Обложка фильма" style="max-width: 400px;">
            <br><br>
            <a href="/">Перейти на лэндинг</a>
        </body>
    </html>
""")

# B
@app.post("/login", response_model=LoginResponse)
async def login(
    username: str = Form(...),
    password: str = Form(...),
    response: Response = None
):
    if username not in valid_users or valid_users[username] != password:
        raise HTTPException(status_code=401, detail="Wrong username or password")
    
    session_token = token_manager.create_session(username)
    session = token_manager.active_sessions[session_token]

    response.set_cookie(
        key="session_token",
        value=session_token,
        httponly=True,
        secure=False,
        max_age=120,
        samesite="lax"
    )

    return LoginResponse(
        message="Successful log in",
        username=username,
        session_created=session.created_at,
        session_expires=session.expires_at
    )

@app.post("/login-json", response_model=LoginResponse)
async def login_json(data:dict, response: Response):
    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        raise HTTPException(status_code=401, detail="Need username and password")
    
    return await login(username, password, response)

@app.get("/login-json", response_model=LoginResponse)
async def login_json_get(
    username: str = Query(..., description="Username for login"),
    password: str = Query(..., description="Password for login"), 
    response: Response = None
):
    return await login(username, password, response)

@app.get("/user")
def get_user_profile(current_user = Depends(get_current_user)):
    now =datetime.now()

    session_duration = now - current_user.created_at
    time_until_expiry = current_user.expires_at - now

    time_info = {
        "login_time": current_user.created_at,
        "session_start": current_user.created_at, 
        "last_activity": current_user.last_activity,
        "current_time": now,
        "session_expires": current_user.expires_at,
        "session_duration": session_duration,
        "time_until_expiry": time_until_expiry
    }

    user_info = {
        "username": current_user.username,
        "is_active": True
    }

    return UserDataResponse(
        user=user_info,
        time_info=time_info,
        message="Data successfully getted"
    )

@app.post("/logout")
async def logout_post(response: Response, current_user = Depends(get_optional_user)):
    if current_user:
        user_sessions = token_manager.get_user_sessions(current_user.username)
        for token in user_sessions.keys():
            token_manager.delete_session(token)
    
    response.delete_cookie(key="session_token")
    return {"message": "Successfully logged out"}

@app.get("/logout")
async def logout_get(response: Response, current_user = Depends(get_optional_user)):
    if current_user:
        user_sessions = token_manager.get_user_sessions(current_user.username)
        for token in user_sessions.keys():
            token_manager.delete_session(token)
    
    response.delete_cookie(key="session_token")
    return RedirectResponse(url="/", status_code=303)

@app.get("/login-form")
async def login_form():
    return HTMLResponse("""
    <html>
        <body style="font-family: Arial; max-width: 400px; margin: 50px auto; padding: 20px;">
            <h2>Вход в систему</h2>
            <form action="/login" method="post">
                <div style="margin: 10px 0;">
                    <label>Имя пользователя:</label><br>
                    <input type="text" name="username" required style="width: 100%; padding: 8px;">
                </div>
                <div style="margin: 10px 0;">
                    <label>Пароль:</label><br>
                    <input type="password" name="password" required style="width: 100%; padding: 8px;">
                </div>
                <button type="submit" style="background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer;">
                    Войти
                </button>
            </form>
            
            <div style="margin-top: 20px; padding: 15px; background: #f8f9fa;">
                <h4>Тестовые пользователи:</h4>
                <ul>
                    <li><strong>admin</strong> / password123</li>
                    <li><strong>user</strong> / 123456</li>
                    <li><strong>demo</strong> / demo</li>
                </ul>
            </div>
            
            <div style="margin-top: 20px;">
                <a href="/user">Попробовать получить профиль (требуется авторизация)</a>
            </div>
        </body>
    </html>
    """)