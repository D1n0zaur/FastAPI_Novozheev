from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import shutil
import os

from models import Movie

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