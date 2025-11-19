from fastapi import FastAPI, HTTPException, UploadFile, Depends, File, Form, Response, Query, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import shutil
import os
from datetime import datetime
from typing import Optional

from models import Movie, LoginResponse, UserProfileResponse, UserDataResponse, TokenResponse, UserLogin
from jwt_manager import jwt_manager, TokenData
from jwt_auth import get_current_user, get_optional_user, valid_users

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
                <li><a href="/study">Информация о ВУЗе</a></li>
                <li><a href="/movietop">Список Фильмов</a></li>
                <li><a href="/movietop/Аватар">Конкретный фильм</a></li>
                <li><a href="/add">Добавление фильма</a></li>
                <li><a href="/login-form">Окно регистрации</a></li>
                <li><a href="/docs">Документация API</a></li>
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
    Movie(id=1, name="Аватар", cost=237.0, director="Джеймс Кэмерон"),
    Movie(id=2, name="Мстители: Финал", cost=356.0, director="Энтони и Джо Руссо"),
    Movie(id=3, name="Титаник", cost=200.0, director="Джеймс Кэмерон"),
    Movie(id=4, name="Звёздные войны: Пробуждение силы", cost=245.0, director="Дж. Дж. Абрамс"),
    Movie(id=5, name="Мстители: Война бесконечности", cost=316.0, director="Энтони и Джо Руссо"),
    Movie(id=6, name="Человек-паук: Нет пути домой", cost=200.0, director="Джон Уоттс"),
    Movie(id=7, name="Король Лев", cost=45.0, director="Джон Фавро"),
    Movie(id=8, name="Мстители", cost=220.0, director="Джосс Уидон"),
    Movie(id=9, name="Форсаж 7", cost=190.0, director="Джеймс Ван"),
    Movie(id=10, name="Холодное сердце 2", cost=150.0, director="Крис Бак и Дженнифер Ли")
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

# Б + Г
@app.get("/add")
def form(current_user: Optional[TokenData] = Depends(get_optional_user)):
    if not current_user:
        return HTMLResponse("""
            <h2>Требуется авторизация</h2>
            <p>Пожалуйста, войдите в систему чтобы добавить фильм.</p>
            <a href="/login-form">Войти</a> | 
            <a href="/">На главную</a>
        """)
    
    return HTMLResponse(f"""
        <h2><strong>👤 Авторизован как:</strong> {current_user.username}</h2>
        <form method="post" action="/add_film" enctype="multipart/form-data">
            Название: <input name="name" required><br><br>
            Режиссёр: <input name="director" required><br><br>
            Бюджет: <input name="cost" type="number" step="0.1" required><br><br>
            Описание: <input name="description"><br><br>
            Номинация на "Оскар": <input name="oscar" type="checkbox" value="true"><br><br>
            Обложка: <input name="photo" type="file" accept="image/*" required><br><br>
            <button>Добавить фильм</button>
        </form>
        <br>
        <a href="/">На главную</a>
    """)

@app.post("/add_film")
async def add_film_protected(
    name: str = Form(...),
    director: str = Form(...),
    cost: float = Form(...),
    description: str = Form(None),
    oscar: bool = Form(False),
    photo: UploadFile = File(...),
    current_user: TokenData = Depends(get_current_user)
):
    try:
        # Сохраняем обложку
        file_extension = photo.filename.split('.')[-1]
        # Очищаем имя пользователя от потенциально опасных символов
        safe_username = "".join(c for c in current_user.username if c.isalnum() or c in ('-', '_'))
        photo_filename = f"movie_{len(movies) + 1}_{safe_username}.{file_extension}"
        photo_path = f"static/{photo_filename}"

        with open(photo_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)

        # Создаем новый фильм
        new_id = max([movie.id for movie in movies], default=0) + 1
        new_movie = Movie(
            name=name, 
            director=director, 
            cost=cost, 
            id=new_id, 
            oscar=oscar,
            photo=f"/static/{photo_filename}",
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
                <h2><strong>👤 Авторизован как:</strong> {current_user.username}</h2>
                <br><br>
                <a href="/">Перейти на лэндинг</a> | 
                <a href="/add">Добавить еще фильм</a>
            </body>
        </html>
        """)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ошибка при добавлении фильма: {str(e)}")

# Г
@app.get("/login-form")
async def login_form_page():
    return HTMLResponse("""
    <html>
        <head>
            <title>Get JWT Token</title>
        </head>
        <body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h2>Получение JWT токена</h2>
            
            <form method="post" action="/login-form">
                <div style="margin: 10px 0;">
                    <label>Имя пользователя:</label><br>
                    <input type="text" name="username" required style="width: 100%; padding: 8px;">
                </div>
                <div style="margin: 10px 0;">
                    <label>Пароль:</label><br>
                    <input type="password" name="password" required style="width: 100%; padding: 8px;">
                </div>
                <button type="submit" style="background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer;">
                    Получить JWT токен
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
                <a href="/">На главную</a>
            </div>
        </body>
    </html>
    """)

@app.post("/login-form")
async def process_login_form(
    username: str = Form(...),
    password: str = Form(...)
):
    try:
        # Проверяем учетные данные
        if username not in valid_users:
            raise HTTPException(status_code=401, detail="Invalid username")
        
        if valid_users[username]["password"] != password:  # Исправлено здесь
            raise HTTPException(status_code=401, detail="Invalid password")
        
        # Создаем токен
        access_token = jwt_manager.create_access_token(
            username=username,
            user_id=valid_users[username]["user_id"]
        )
        
        expiry = jwt_manager.get_token_expiry(access_token)
        
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>✅ JWT Token получен!</h2>
                
                <div style="background: #d4edda; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3>Ваш JWT токен:</h3>
                    <div style="background: white; padding: 15px; border: 1px solid #ccc; border-radius: 3px;">
                        <textarea style="width: 100%; height: 100px; font-family: monospace; border: none; resize: none;" readonly>{access_token}</textarea>
                    </div>
                    
                    <div style="margin-top: 15px;">
                        <p><strong>Тип токена:</strong> bearer</p>
                        <p><strong>Истекает через:</strong> {jwt_manager.access_token_expire_minutes * 60} секунд</p>
                        <p><strong>Время истечения:</strong> {expiry}</p>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <h4>Как использовать токен:</h4>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 5px;">
                        <p><strong>Добавьте этот заголовок к вашим запросам:</strong></p>
                        <code>Authorization: Bearer {access_token}</code>
                    </div>
                </div>
                
                <div style="margin-top: 20px;">
                    <a href="/add">Перейти к защищенной форме</a> | 
                    <a href="/login-form">Получить новый токен</a> |
                    <a href="/">На главную</a>
                </div>
            </body>
        </html>
        """)
        
    except HTTPException as e:
        error_detail = e.detail
        return HTMLResponse(f"""
        <html>
            <body style="font-family: Arial; max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2>Ошибка авторизации</h2>
                
                <div style="background: #f8d7da; padding: 20px; margin: 20px 0; border-radius: 5px;">
                    <h3>{error_detail}</h3>
                    <p>Проверьте правильность введенных данных и попробуйте снова.</p>
                </div>
                
                <a href="/login-form">Попробовать снова</a> | 
                <a href="/">На главную</a>
            </body>
        </html>
        """)
    
@app.post("/login", response_model=TokenResponse)
async def login_jwt(user_data: UserLogin):
    username = user_data.username
    password = user_data.password
    
    # Проверяем учетные данные
    if username not in valid_users:
        raise HTTPException(status_code=401, detail="Invalid username")
    
    if valid_users[username]["password"] != password:  # Исправлено здесь
        raise HTTPException(status_code=401, detail="Invalid password")
    
    # Создаем JWT токен
    access_token = jwt_manager.create_access_token(
        username=username,
        user_id=valid_users[username]["user_id"]
    )
    
    # Получаем время истечения токена
    expiry = jwt_manager.get_token_expiry(access_token)
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=jwt_manager.access_token_expire_minutes * 60,
        expires_at=expiry
    )

@app.get("/verify-token")
async def verify_token(authorization: Optional[str] = Header(None)):
    if authorization is None or not authorization.startswith("Bearer "):
        return {"valid": False, "message": "No token provided"}
    
    token = authorization.replace("Bearer ", "")
    token_data = jwt_manager.verify_token(token)
    
    if token_data:
        return {
            "valid": True,
            "username": token_data.username,
            "user_id": token_data.user_id,
            "expires_at": token_data.exp
        }
    else:
        return {"valid": False, "message": "Invalid or expired token"}

@app.get("/profile")
async def get_profile(current_user: TokenData = Depends(get_current_user)):
    return {
        "username": current_user.username,
        "user_id": current_user.user_id,
        "expires_at": current_user.exp
    }