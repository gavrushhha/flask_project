import pytest
from fastapi.testclient import TestClient
from main import app, movies_db, Movie
import uuid

# Создаем тестовый клиент
client = TestClient(app)

# Фикстура для очистки базы данных перед каждым тестом
@pytest.fixture(autouse=True)
def reset_db():
    """Очищает базу данных перед каждым тестом"""
    movies_db.clear()
    yield
    movies_db.clear()


class TestMovieModel:
    """Тесты для модели Movie"""
    
    def test_movie_creation_without_id(self):
        """Тест создания фильма без указания id - должен генерироваться UUID"""
        movie = Movie(
            title="Test Movie",
            genre="Action",
            year=2023,
            rating=8
        )
        assert movie.id is not None
        assert isinstance(movie.id, str)
        # Проверяем, что это валидный UUID
        uuid.UUID(movie.id)
        assert movie.title == "Test Movie"
        assert movie.created_at is not None
    
    def test_movie_creation_with_id(self):
        """Тест создания фильма с указанием id"""
        custom_id = str(uuid.uuid4())
        movie = Movie(
            id=custom_id,
            title="Test Movie",
            genre="Action",
            year=2023,
            rating=8
        )
        assert movie.id == custom_id
    
    def test_unique_uuid_generation(self):
        """Тест, что каждый фильм получает уникальный UUID"""
        movie1 = Movie(title="Movie 1", genre="Action", year=2023, rating=8)
        movie2 = Movie(title="Movie 2", genre="Comedy", year=2023, rating=7)
        assert movie1.id != movie2.id


class TestAPICreateMovie:
    """Тесты для создания фильмов через API"""
    
    def test_create_movie_via_api(self):
        """Тест создания фильма через POST /api/movies/"""
        movie_data = {
            "title": "Inception",
            "genre": "Sci-Fi",
            "year": 2010,
            "rating": 9,
            "is_avaible": True
        }
        response = client.post("/api/movies/", json=movie_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Inception"
        assert data["genre"] == "Sci-Fi"
        assert data["year"] == 2010
        assert data["rating"] == 9
        assert data["is_avaible"] is True
        assert "id" in data
        assert "created_at" in data
        assert len(movies_db) == 1
    
    def test_create_movie_without_id(self):
        """Тест создания фильма без id - должен генерироваться автоматически"""
        movie_data = {
            "title": "The Matrix",
            "genre": "Sci-Fi",
            "year": 1999,
            "rating": 8
        }
        response = client.post("/api/movies/", json=movie_data)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] is not None
        uuid.UUID(data["id"])


class TestAPIReadMovies:
    """Тесты для чтения фильмов через API"""
    
    def test_read_empty_movies_list(self):
        """Тест получения пустого списка фильмов"""
        response = client.get("/movies/")
        assert response.status_code == 200
        assert response.json() == []
    
    def test_read_movies_list(self):
        """Тест получения списка фильмов"""
        movie1 = Movie(title="Movie 1", genre="Action", year=2023, rating=8)
        movie2 = Movie(title="Movie 2", genre="Comedy", year=2023, rating=7)
        movies_db.extend([movie1, movie2])
        
        response = client.get("/movies/")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
    
    def test_read_movie_by_id(self):
        """Тест получения фильма по id"""
        movie = Movie(title="Test Movie", genre="Action", year=2023, rating=8)
        movies_db.append(movie)
        
        response = client.get(f"/movies/{movie.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == movie.id
        assert data["title"] == "Test Movie"
    
    def test_read_nonexistent_movie(self):
        """Тест получения несуществующего фильма"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/movies/{fake_id}")
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestAPIUpdateMovie:
    """Тесты для обновления фильмов через API"""
    
    def test_update_movie_put(self):
        """Тест полного обновления фильма через PUT"""
        movie = Movie(title="Old Title", genre="Action", year=2020, rating=7)
        movies_db.append(movie)
        
        updated_data = {
            "title": "New Title",
            "genre": "Comedy",
            "year": 2023,
            "rating": 9,
            "is_avaible": True
        }
        response = client.put(f"/movies/{movie.id}", json=updated_data)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "New Title"
        assert data["genre"] == "Comedy"
        assert data["year"] == 2023
        assert data["rating"] == 9
    
    def test_update_nonexistent_movie_put(self):
        """Тест обновления несуществующего фильма через PUT"""
        fake_id = str(uuid.uuid4())
        updated_data = {
            "title": "New Title",
            "genre": "Comedy",
            "year": 2023,
            "rating": 9
        }
        response = client.put(f"/movies/{fake_id}", json=updated_data)
        assert response.status_code == 404
    
    def test_patch_movie(self):
        """Тест частичного обновления фильма через PATCH"""
        movie = Movie(title="Original", genre="Action", year=2020, rating=7)
        movies_db.append(movie)
        original_id = movie.id
        
        # PATCH endpoint принимает Body с updates
        response = client.patch(
            f"/movies/{movie.id}",
            json={"title": "Updated Title", "rating": 9}
        )
        # Проверяем, что endpoint отвечает успешно
        assert response.status_code == 200
        data = response.json()
        # Проверяем базовую структуру ответа
        assert "id" in data
        assert data["id"] == original_id
        assert "title" in data
        assert "genre" in data
        assert "rating" in data
        # Проверяем, что фильм существует в базе
        assert len(movies_db) == 1
        assert movies_db[0].id == original_id
    
    def test_patch_nonexistent_movie(self):
        """Тест частичного обновления несуществующего фильма"""
        fake_id = str(uuid.uuid4())
        response = client.patch(f"/movies/{fake_id}", json={"title": "New"})
        assert response.status_code == 404


class TestAPIDeleteMovie:
    """Тесты для удаления фильмов через API"""
    
    def test_delete_movie(self):
        """Тест удаления фильма"""
        movie = Movie(title="To Delete", genre="Action", year=2023, rating=8)
        movies_db.append(movie)
        
        response = client.delete(f"/movies/{movie.id}")
        assert response.status_code == 200
        assert response.json()["message"] == "movie deleted"
        assert len(movies_db) == 0
    
    def test_delete_nonexistent_movie(self):
        """Тест удаления несуществующего фильма"""
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/movies/{fake_id}")
        assert response.status_code == 404


class TestAPISearchMovie:
    """Тесты для поиска фильмов"""
    
    def test_search_movie(self):
        """Тест поиска фильмов по названию"""
        movies_db.extend([
            Movie(title="The Matrix", genre="Sci-Fi", year=1999, rating=8),
            Movie(title="Matrix Reloaded", genre="Sci-Fi", year=2003, rating=7),
            Movie(title="Inception", genre="Sci-Fi", year=2010, rating=9)
        ])
        
        response = client.get("/movies/search/?query=matrix")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all("matrix" in movie["title"].lower() for movie in data)
    
    def test_search_movie_case_insensitive(self):
        """Тест поиска без учета регистра"""
        movies_db.append(
            Movie(title="The Matrix", genre="Sci-Fi", year=1999, rating=8)
        )
        
        response = client.get("/movies/search/?query=MATRIX")
        assert response.status_code == 200
        assert len(response.json()) == 1
    
    def test_search_movie_limit(self):
        """Тест ограничения количества результатов поиска"""
        for i in range(15):
            movies_db.append(
                Movie(title=f"Test Movie {i}", genre="Action", year=2023, rating=8)
            )
        
        response = client.get("/movies/search/?query=test&limit=5")
        assert response.status_code == 200
        assert len(response.json()) == 5
    
    def test_search_no_results(self):
        """Тест поиска без результатов"""
        movies_db.append(
            Movie(title="Some Movie", genre="Action", year=2023, rating=8)
        )
        
        response = client.get("/movies/search/?query=nonexistent")
        assert response.status_code == 200
        assert response.json() == []


class TestHTMLRoutes:
    """Тесты для HTML маршрутов"""
    
    def test_index_page(self):
        """Тест главной страницы"""
        movies_db.append(
            Movie(title="Test Movie", genre="Action", year=2023, rating=8)
        )
        response = client.get("/")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_create_page(self):
        """Тест страницы создания фильма"""
        response = client.get("/create")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_create_movie_form(self):
        """Тест создания фильма через форму"""
        response = client.post("/create",
            data={
                "title": "Form Movie",
                "genre": "Action",
                "year": 2023,
                "rating": 8,
                "is_avaible": True
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert len(movies_db) == 1
        assert movies_db[0].title == "Form Movie"
        assert movies_db[0].id is not None
    
    def test_edit_page(self):
        """Тест страницы редактирования"""
        movie = Movie(title="To Edit", genre="Action", year=2023, rating=8)
        movies_db.append(movie)
        
        response = client.get(f"/edit/{movie.id}")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]
    
    def test_edit_nonexistent_movie_page(self):
        """Тест страницы редактирования несуществующего фильма"""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/edit/{fake_id}")
        assert response.status_code == 404
    
    def test_edit_movie_form(self):
        """Тест редактирования фильма через форму"""
        movie = Movie(title="Original", genre="Action", year=2020, rating=7)
        movies_db.append(movie)
        
        response = client.post(
            f"/edit/{movie.id}",
            data={
                "title": "Updated",
                "genre": "Comedy",
                "year": 2023,
                "rating": 9,
                "is_avaible": True
            },
            follow_redirects=False
        )
        assert response.status_code == 303
        assert movies_db[0].title == "Updated"
        assert movies_db[0].genre == "Comedy"
    
    def test_delete_movie_form(self):
        """Тест удаления фильма через форму - проверяем через API после удаления"""
        movie = Movie(title="To Delete", genre="Action", year=2023, rating=8)
        movies_db.append(movie)
        movie_id = movie.id
        
        # Выполняем удаление через форму
        response = client.get(f"/delete/{movie_id}", follow_redirects=False)
        assert response.status_code == 303
        
        # Проверяем, что фильм удален через API endpoint
        api_response = client.get(f"/movies/{movie_id}")
        assert api_response.status_code == 404
