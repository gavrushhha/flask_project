from fastapi import FastAPI, HTTPException, Request, Form, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uuid
import os

app=FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates=Jinja2Templates(directory="templates")
class Movie(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    genre: str
    year: int
    rating: int
    is_avaible: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now())
movies_db:List[Movie]=[]
@app.get("/",response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "movies":movies_db})
@app.post("/api/movies/",response_model=Movie)
async def api_create_movie(movie:Movie):
    movies_db.append(movie)
    return movie
@app.get("/create",response_class=HTMLResponse)
async def create_page(request: Request):
    return templates.TemplateResponse("create.html", {"request": request})
@app.post("/create")
async def create_movie_form(
    request: Request,
    title: str = Form(...),
    genre: str = Form(...),
    year: int = Form(...),
    rating: int = Form(...),
    is_avaible: Optional[bool] = Form(False)
):
    movie=Movie(title=title,genre=genre, year=year, rating=rating, is_avaible=is_avaible)
    movies_db.append(movie)
    return RedirectResponse(url="/",status_code=303)
@app.get("/edit/{movie_id}", response_class=HTMLResponse)
async def edit_page(request: Request, movie_id: str):
    movie=next((m for m in movies_db if m.id == movie_id), None)
    if not movie:
        raise HTTPException(status_code=404, detail="Фильм не найден")
    return templates.TemplateResponse("edit.html", {"request": request, "movie":movie})
@app.post("/edit/{movie_id}")
async def edit_movie_form(
    movie_id:str,
    title:str=Form(...),
    genre:str=Form(...),
    year:int=Form(...),
    rating:int=Form(...),
    is_avaible:Optional[bool]=Form(False)
):
    for idx, movie in enumerate(movies_db):
        if movie.id == movie_id:
            movies_db[idx].title=title
            movies_db[idx].genre=genre
            movies_db[idx].year=year
            movies_db[idx].rating=rating
            movies_db[idx].is_avaible=is_avaible
            return RedirectResponse(url="/",status_code=303)
    raise HTTPException(status_code=404,detail="Фильм не найден")
@app.get("/delete/{movie_id}")
async def delete_movie_form(movie_id:str):
    global movies_db
    movies_db=[m for m in movies_db if m.id !=movie_id]
    return RedirectResponse(url="/",status_code=303)
@app.get("/movies/",response_model=List[Movie])
async def read_movies():
    return movies_db
@app.get("/movies/{movie_id}",response_model=Movie)
async def read_movies_id(movie_id:str):
    for movie in movies_db:
        if movie.id==movie_id:
            return movie
    raise HTTPException(status_code=404,detail="Movie not found")
@app.put("/movies/{movie_id}",response_model=Movie)
async def update_movie(movie_id:str,updated_movie:Movie):
    for idx, movie in enumerate(movies_db):
        if movie.id==movie_id:
            movies_db[idx]=updated_movie
            return updated_movie
    raise HTTPException(status_code=404,detail="Movie not found")
@app.patch("/movies/{movie_id}",response_model=Movie)
async def patch_movie(
    movie_id: str,
    title: Optional[str] = None,
    genre: Optional[str] = None,
    year: Optional[int] = None,
    rating: Optional[int] = None,
    is_avaible: Optional[bool] = None
):
    movie=next((t for t in movies_db if t.id==movie_id), None)
    if not movie:
        raise HTTPException(status_code=404,detail="Movie not found")
    if title is not None:
        movie.title=title
    if genre is not None:
        movie.genre=genre
    if year is not None:
        movie.year=year
    if rating is not None:
        movie.rating=rating
    if is_avaible is not None:

        movie.is_avaible=is_avaible
    return movie
@app.delete("/movies/{movie_id}")
async def delete_movie(movie_id:str):
    for idx, movie in enumerate(movies_db):
        if movie.id==movie_id:
            del movies_db[idx]
            return {"message": "movie deleted"}
    raise HTTPException(status_code=404,detail="Movie not found")
@app.get("/movies/search/",response_model=List[Movie])
async def search_movie(query: str, limit: int=10):
    results=[t for t in movies_db if query.lower() in t.title.lower()]
    return results[:limit]
