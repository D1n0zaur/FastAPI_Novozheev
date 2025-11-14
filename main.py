from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse

from models import Movie, AddMovie

app = FastAPI()
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
            <h3>Это моё решение курса FastAPI. Чтобы перейти на Задания, введите следующие комманды в поиск после "/"</h3>
            <ul>
                <li><strong>Модуль А:</strong> study, movietop, movietop/название фильма</li>
                <li><strong>Модуль Б:</strong></li>
                <li><strong>Модуль :</strong></li>
            </ul>
            <a href="/study">Модуль А задание 1</a>
        </body>
    </html>
    """)

# А
# Задание 2
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
        </body>
    </html>
    """

@app.get("/study", response_class=HTMLResponse)
async def get_study_page():
    return HTMLResponse(html_data)

# Задание 3
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