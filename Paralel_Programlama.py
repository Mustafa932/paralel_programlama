import multiprocessing
from concurrent.futures import ProcessPoolExecutor
import time
import random
from functools import partial 

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

def is_point_in_polygon(point, polygon_vertices):

    n = len(polygon_vertices)
    if n < 3:
        return False

    inside = False

    for i in range(n):
        j = (i + 1) % n
        p1 = polygon_vertices[i]
        p2 = polygon_vertices[j]

        if ((p1.y > point.y) != (p2.y > point.y)):
            if p2.y - p1.y == 0:
                continue

            intersect_x = p1.x + (point.y - p1.y) * (p2.x - p1.x) / (p2.y - p1.y)

            if intersect_x > point.x:
                inside = not inside
    
    return inside

u_shape_polygon = [
    Point(0, 0),
    Point(10, 0),
    Point(10, 10),
    Point(7, 10),
    Point(7, 3),
    Point(3, 3),
    Point(3, 10),
    Point(0, 10)
]

def generate_random_points(count, x_min, x_max, y_min, y_max):
    points = []
    for _ in range(count):
        x = random.uniform(x_min, x_max)
        y = random.uniform(y_min, y_max)
        points.append(Point(x, y))
    return points

num_test_points = 100000
test_points = generate_random_points(num_test_points, -5, 15, -5, 15)


def paralel(points, polygon_vertices):

    results = []
    
    with ProcessPoolExecutor(max_workers=multiprocessing.cpu_count()) as executor:

        func_with_polygon = partial(is_point_in_polygon, polygon_vertices=polygon_vertices)
        results = list(executor.map(func_with_polygon, points))

    return results

# Ana Program
if __name__ == "__main__":
    print(f"Kullanılan CPU çekirdeği sayısı: {multiprocessing.cpu_count()}")
    print(f"Toplam kontrol edilecek nokta sayısı: {len(test_points)}")

    print("\n--- Paralel Kontrol Başlıyor ---")
    start_time_paralel = time.perf_counter()
    
    # Paralel fonksiyonu çağır
    paralel_results = check_points_paralel(test_points, u_shape_polygon)
    end_time_paralel = time.perf_counter()
    print(f"Paralel kontrol süresi: {end_time_paralel - start_time_paralel:.4f} saniye")

    # Sonuçları gösterme 
    print("\nParalel Sonuçlardan Örnekler:")
    for i in range(min(5, len(test_points))):
        print(f"Nokta {test_points[i]}: {'İçinde' if paralel_results[i] else 'Dışında'}")
    if len(test_points) > 10:
        print("...")
        for i in range(max(0, len(test_points) - 5), len(test_points)):
            print(f"Nokta {test_points[i]}: {'İçinde' if paralel_results[i] else 'Dışında'}")

    # Tek iş parçacıklı (seri) performansı karşılaştırmak için:
    print("\n--- Seri Kontrol Başlıyor (Karşılaştırma İçin) ---")
    start_time_serial = time.perf_counter()
    serial_results = [is_point_in_polygon(p, u_shape_polygon) for p in test_points]
    end_time_serial = time.perf_counter()
    print(f"Seri kontrol süresi: {end_time_serial - start_time_serial:.4f} saniye")

    # Sonuçların doğruluğunu kontrol et (basit bir doğrulama)
    print(f"\nSonuçlar aynı mı? {paralel_results == serial_results}")