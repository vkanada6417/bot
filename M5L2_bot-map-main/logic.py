import io
import sqlite3
from config import *
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature

class DB_Map():
    def __init__(self, database):
        self.database = database
    
    def create_user_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users_cities (
                                user_id INTEGER,
                                city_id TEXT,
                                FOREIGN KEY(city_id) REFERENCES cities(id)
                            )''')
            conn.commit()
    
    def get_cities_by_country(self, country):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT city 
                            FROM cities  
                            WHERE country = ?''', (country,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_cities_by_population_density(self, min_density, max_density=None):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            if max_density:
                cursor.execute('''SELECT city 
                                FROM cities  
                                WHERE population_density BETWEEN ? AND ?''', (min_density, max_density))
            else:
                cursor.execute('''SELECT city 
                                FROM cities  
                                WHERE population_density >= ?''', (min_density,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_cities_by_country_and_density(self, country, min_density, max_density=None):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            if max_density:
                cursor.execute('''SELECT city 
                                FROM cities  
                                WHERE country = ? AND population_density BETWEEN ? AND ?''',
                            (country, min_density, max_density))
            else:
                cursor.execute('''SELECT city 
                                FROM cities  
                                WHERE country = ? AND population_density >= ?''',
                            (country, min_density))
            cities = [row[0] for row in cursor.fetchall()]
            return cities
        


    def add_city(self, user_id, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM cities WHERE city=?", (city_name,))
            city_data = cursor.fetchone()
            if city_data:
                city_id = city_data[0]  
                conn.execute('INSERT INTO users_cities VALUES (?, ?)', (user_id, city_id))
                conn.commit()
                return 1
            else:
                return 0

    def select_cities(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT cities.city 
                            FROM users_cities  
                            JOIN cities ON users_cities.city_id = cities.id
                            WHERE users_cities.user_id = ?''', (user_id,))
            cities = [row[0] for row in cursor.fetchall()]
            return cities

    def get_coordinates(self, city_name):
        conn = sqlite3.connect(self.database)
        with conn:
            cursor = conn.cursor()
            cursor.execute('''SELECT lat, lng
                            FROM cities  
                            WHERE city = ?''', (city_name,))
            coordinates = cursor.fetchone()
            return coordinates

    def create_graph(self, cities, marker_color='blue'):
        """
        Создает карту с отметками городов и возвращает её как объект BytesIO.
        
        :param cities: Список названий городов для отображения на карте.
        :param marker_color: Цвет маркеров (по умолчанию синий).
        :return: Объект BytesIO с изображением карты.
        """
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Добавляем географические объекты
        ax.add_feature(cfeature.LAND, facecolor='#f5f5dc')  # Заливка континентов
        ax.add_feature(cfeature.OCEAN, facecolor='#add8e6')  # Заливка океанов
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.5)
        ax.add_feature(cfeature.RIVERS)

        # Устанавливаем границы карты
        ax.set_global()

        # Получаем координаты городов и добавляем их на карту
        for city in cities:
            coordinates = self.get_coordinates(city)
            if coordinates:
                lat, lng = coordinates
                ax.plot(lng, lat, 'o', color=marker_color, markersize=5, transform=ccrs.Geodetic())
                ax.text(lng + 0.5, lat + 0.5, city, fontsize=8, transform=ccrs.Geodetic())

        # Сохраняем карту в объект BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        plt.close()

        return buffer

    def create_map_with_features(self):
        """
        Создает карту с различными географическими объектами.
        
        :return: Объект BytesIO с изображением карты.
        """
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        # Добавляем географические объекты
        ax.add_feature(cfeature.LAND, facecolor='#f5f5dc')  # Заливка континентов
        ax.add_feature(cfeature.OCEAN, facecolor='#add8e6')  # Заливка океанов
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        ax.add_feature(cfeature.LAKES, alpha=0.5)
        ax.add_feature(cfeature.RIVERS)
        ax.add_feature(cfeature.STATES, edgecolor='gray')  # Границы штатов/регионов

        # Добавляем точки интереса (примеры)
        points_of_interest = {
            "Mount Everest": (27.9881, 86.9250),
            "Amazon River Mouth": (-0.6547, -50.1796),
            "Sahara Desert": (23.5, 13.0),
        }
        for name, (lat, lng) in points_of_interest.items():
            ax.plot(lng, lat, 'ro', markersize=5, transform=ccrs.Geodetic())
            ax.text(lng + 0.5, lat + 0.5, name, fontsize=8, transform=ccrs.Geodetic())

        # Сохраняем карту в объект BytesIO
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', bbox_inches='tight')
        buffer.seek(0)
        plt.close()

        return buffer

if __name__ == "__main__":
    m = DB_Map(DATABASE)
    m.create_user_table()