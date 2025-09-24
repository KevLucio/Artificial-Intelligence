import math
from collections import deque

def calcular_prioridad(x, y, x_meta, y_meta):
    # Calcula la distancia euclidiana entre (x, y) y (x_meta, y_meta)
    return math.sqrt((x - x_meta) ** 2 + (y - y_meta) ** 2)

# Luego, en el método mover de la clase SerX, puedes usar esta función para determinar la dirección:
def mover_con_prioridad(self, x_meta, y_meta):
    # Calcular la prioridad para las 4 direcciones posibles
    prioridades = {
        "W": calcular_prioridad(self.x, self.y - 1, x_meta, y_meta),
        "A": calcular_prioridad(self.x - 1, self.y, x_meta, y_meta),
        "S": calcular_prioridad(self.x, self.y + 1, x_meta, y_meta),
        "D": calcular_prioridad(self.x + 1, self.y, x_meta, y_meta),
    }
    # Elegir la dirección con la menor prioridad
    direccion = min(prioridades, key=prioridades.get)
    self.mover(direccion)
    
# Búsqueda en amplitud (BFS)
def resolver_bfs(laberinto, x_inicial, y_inicial, x_meta, y_meta):
    visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
    cola = deque()
    cola.append((x_inicial, y_inicial, []))  # Cola de nodos con coordenadas (x, y) y camino

    while cola:
        x, y, camino = cola.popleft()
        if x == x_meta and y == y_meta:
            return camino

        if 0 <= x < len(laberinto[0]) and 0 <= y < len(laberinto) and laberinto[y][x] == 1 and not visitado[y][x]:
            visitado[y][x] = True
            # Agregar nodos adyacentes a la cola
            cola.append((x + 1, y, camino + ["D"]))  # Derecha
            cola.append((x - 1, y, camino + ["A"]))  # Izquierda
            cola.append((x, y + 1, camino + ["S"]))  # Abajo
            cola.append((x, y - 1, camino + ["W"]))  # Arriba

    return None  # No se encontró un camino

# Luego, puedes llamar a esta función para obtener el camino:
camino_bfs = resolver_bfs(laberinto, x_inicial, y_inicial, x_meta, y_meta)
print("Camino encontrado por BFS:", camino_bfs)

# Búsqueda en Profundidad (DFS)
def resolver_dfs(laberinto, x_inicial, y_inicial, x_meta, y_meta):
    def dfs(x, y, camino):
        if x == x_meta and y == y_meta:
            return camino
        if (
            0 <= x < len(laberinto[0])
            and 0 <= y < len(laberinto)
            and laberinto[y][x] == 1
            and not visitado[y][x]
        ):
            visitado[y][x] = True
            for dx, dy, direccion in [(1, 0, "D"), (-1, 0, "A"), (0, 1, "S"), (0, -1, "W")]:
                resultado = dfs(x + dx, y + dy, camino + [direccion])
                if resultado:
                    return resultado
        return None

    visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
    camino_dfs = dfs(x_inicial, y_inicial, [])
    return camino_dfs

# Luego, puedes llamar a esta función para obtener el camino:
camino_dfs = resolver_dfs(laberinto, x_inicial, y_inicial, x_meta, y_meta)
print("Camino encontrado por DFS:", camino_dfs)

# Arbol real generado:
def imprimir_arbol(arbol):
    for nodo, hijos in arbol.items():
        print(f"Nodo: {nodo}, Hijos: {hijos}")

