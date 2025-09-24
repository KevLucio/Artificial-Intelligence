"""
@author: Kevyn Alejandro Pérez Lucio
"""

import pygame
import sys
import math
from collections import deque
import pydot
import graphviz

# Inicializar Pygame
pygame.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laberinto")

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)

arbol_busqueda = None  # Inicialización

# Cargar el laberinto desde un archivo TXT
def cargar_laberinto(nombre_archivo):
    laberinto = []
    with open(nombre_archivo, 'r') as file:
        for line in file:
            row = [int(char) for char in line.strip().split(',')]
            laberinto.append(row)
    return laberinto

# Función para calcular la distancia euclidiana entre dos puntos
def calcular_distancia(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

# Clase para el ser X
class SerX:
    def __init__(self, x, y, avatar):
        self.x = x
        self.y = y
        self.avatar = avatar
        self.movimientos = 0
        self.costo_total = 0
        self.vision = 1
        self.visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
        self.eleccion = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]

    def mover(self, direccion):
        x_actual, y_actual = self.x, self.y

        if direccion == "W" and self.y > 0 and laberinto[self.y - 1][self.x] == 1:
            self.y -= 1
        elif direccion == "A" and self.x > 0 and laberinto[self.y][self.x - 1] == 1:
            self.x -= 1
        elif direccion == "S" and self.y < len(laberinto) - 1 and laberinto[self.y + 1][self.x] == 1:
            self.y += 1
        elif direccion == "D" and self.x < len(laberinto[0]) - 1 and laberinto[self.y][self.x + 1] == 1:
            self.x += 1

        self.visitado[self.y][self.x] = True
        self.movimientos += 1
        self.costo_total += calcular_distancia(x_actual, y_actual, self.x, self.y)

    def mover_con_prioridad(self, x_meta, y_meta, metodo_busqueda):
        # Definir las direcciones en el orden de prioridad deseado
        direcciones_prioritarias = ["W", "A", "S", "D"]

        for direccion in direcciones_prioritarias:
            x_nuevo, y_nuevo = self.x, self.y  # Copia temporal de la posición actual

            if direccion == "W" and self.y > 0:
                y_nuevo -= 1
            elif direccion == "A" and self.x > 0:
                x_nuevo -= 1
            elif direccion == "S" and self.y < len(laberinto) - 1:
                y_nuevo += 1
            elif direccion == "D" and self.x < len(laberinto[0]) - 1:
                x_nuevo += 1

            if (
                0 <= x_nuevo < len(laberinto[0])
                and 0 <= y_nuevo < len(laberinto)
                and laberinto[y_nuevo][x_nuevo] == 1
            ):
                # Puede moverse en esta dirección
                self.mover(direccion)
                return

    def dibujar(self, win):
        x_pos = self.x * CELDA_SIZE
        y_pos = self.y * CELDA_SIZE
        avatar_image = pygame.image.load(self.avatar)
        win.blit(avatar_image, (x_pos, y_pos))

    def mostrar_vision(self):
        for i in range(max(0, self.y - self.vision), min(len(laberinto), self.y + self.vision + 1)):
            for j in range(max(0, self.x - self.vision), min(len(laberinto[0]), self.x + self.vision + 1)):
                if self.visitado[i][j]:
                    if laberinto[i][j] == 0:
                        pygame.draw.rect(win, BLACK, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                    elif laberinto[i][j] == 1:
                        pygame.draw.rect(win, WHITE, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                elif self.eleccion[i][j]:
                    font = pygame.font.Font(None, 36)
                    letra_o = font.render("O", True, BLACK)
                    letra_v = font.render("V", True, BLUE)
                    win.blit(letra_o, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))
                    if laberinto[i][j] == 1:
                        win.blit(letra_v, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))

# Función para escribir el árbol de búsqueda en un archivo de texto
def escribir_arbol(arbol_busqueda):
    with open("arbol_busqueda.txt", "w") as archivo:
        for nodo, hijos in arbol_busqueda.items():
            archivo.write(f"Nodo: {nodo}, Hijos: {hijos}\n")

# Función para resolver el laberinto utilizando Búsqueda en Amplitud (BFS)
def resolver_bfs(laberinto, x_inicial, y_inicial, x_meta, y_meta):
    visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
    cola = deque()
    cola.append((x_inicial, y_inicial, []))
    arbol = {}  # Diccionario para almacenar el árbol de búsqueda

    while cola:
        x, y, camino = cola.popleft()
        if x == x_meta and y == y_meta:
            return camino, arbol  # Retorna el camino y el árbol de búsqueda

        if (
            0 <= x < len(laberinto[0])
            and 0 <= y < len(laberinto)
            and laberinto[y][x] == 1
            and not visitado[y][x]
        ):
            visitado[y][x] = True
            arbol[(x, y)] = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            cola.append((x + 1, y, camino + ["D"]))
            cola.append((x - 1, y, camino + ["A"]))
            cola.append((x, y + 1, camino + ["S"]))
            cola.append((x, y - 1, camino + ["W"]))

    return None, None

# Función para resolver el laberinto utilizando Búsqueda en Profundidad (DFS)
def resolver_dfs(laberinto, x_inicial, y_inicial, x_meta, y_meta):
    def dfs(x, y, camino, arbol):
        if x == x_meta and y == y_meta:
            return camino, arbol  # Retorna el camino y el árbol de búsqueda
        if (
            0 <= x < len(laberinto[0])
            and 0 <= y < len(laberinto)
            and laberinto[y][x] == 1
            and not visitado[y][x]
        ):
            visitado[y][x] = True
            arbol[(x, y)] = [(x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)]
            for dx, dy, direccion in [(1, 0, "D"), (-1, 0, "A"), (0, 1, "S"), (0, -1, "W")]:
                resultado, arbol = dfs(x + dx, y + dy, camino + [direccion], arbol)
                if resultado:
                    return resultado, arbol
        return None, arbol

    visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
    camino_dfs, arbol = dfs(x_inicial, y_inicial, [], {})
    return camino_dfs, arbol

# Función para mostrar el mapa real descubierto del laberinto
def mostrar_mapa_real():
    for i in range(len(laberinto)):
        for j in range(len(laberinto[i])):
            if serx.visitado[i][j]:
                if laberinto[i][j] == 0:
                    pygame.draw.rect(win, BLACK, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                elif laberinto[i][j] == 1:
                    pygame.draw.rect(win, WHITE, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))

# Función para imprimir el árbol de búsqueda
def imprimir_arbol(arbol):
    for nodo, hijos in arbol.items():
        print(f"Nodo: {nodo}, Hijos: {hijos}")
        
def crear_grafo_pydot(arbol):
    graph = pydot.Dot(graph_type='graph')

    for nodo, hijos in arbol.items():
        node = pydot.Node(str(nodo))
        graph.add_node(node)

        for hijo in hijos:
            edge = pydot.Edge(str(nodo), str(hijo))
            graph.add_edge(edge)

    return graph

# Tamaño de las celdas en píxeles
CELDA_SIZE = 40

# Cargar el laberinto y configurar la posición inicial
nombre_archivo = "laberinto.txt"
laberinto = cargar_laberinto(nombre_archivo)
x_inicial = int(input("Ingrese la coordenada x inicial: "))
y_inicial = int(input("Ingrese la coordenada y inicial: "))

# Lista de avatares disponibles
avatares = {
    "Humano": "humano.png",
    "Mono": "mono.png",
    "Pulpo": "pulpo.png",
    "Pie Grande": "pie_grande.png"
}

# Preguntar al usuario qué avatar desea utilizar
print("Avatares disponibles:")
for i, avatar in enumerate(avatares, start=1):
    print(f"{i}. {avatar}")
avatar_index = int(input("Seleccione un avatar (1-4): "))
avatar = avatares[list(avatares.keys())[avatar_index - 1]]

# Coordenadas de la meta
x_meta = int(input("Ingrese la coordenada x de la meta: "))
y_meta = int(input("Ingrese la coordenada y de la meta: "))

# Cargar la imagen de la meta
meta_image = pygame.image.load("meta.png")

# Crear una instancia de SerX
serx = SerX(x_inicial, y_inicial, avatar)

# Preguntar al usuario si quiere cambiar alguna parte del laberinto
cambio_lab = input("¿Desea cambiar alguna parte del laberinto? (Sí/No): ").lower()
while cambio_lab == "si" or cambio_lab == "sí":
    x_cambio = int(input("Ingrese la coordenada x a cambiar: "))
    y_cambio = int(input("Ingrese la coordenada y a cambiar: "))
    
    if x_cambio >= 0 and x_cambio < len(laberinto[0]) and y_cambio >= 0 and y_cambio < len(laberinto):
        nuevo_valor = int(input("¿Qué valor desea asignar? (0: Pared, 1: Camino): "))
        
        if nuevo_valor == 0 or nuevo_valor == 1:
            laberinto[y_cambio][x_cambio] = nuevo_valor
            print("Laberinto actualizado.")
        else:
            print("Valor no válido. Por favor, ingrese 0 para pared o 1 para camino.")
    else:
        print("Coordenadas fuera del rango del laberinto.")
    
    cambio_lab = input("¿Desea cambiar otra parte del laberinto? (Sí/No): ").lower()

# Preguntar al usuario si quiere conocer una zona del laberinto
quiero_conocer_zona = input("¿Desea conocer una zona del laberinto? (Sí/No): ").lower()
# Verificar si el usuario quiere conocer una zona del laberinto
while quiero_conocer_zona == "si" or quiero_conocer_zona == "sí":
    zona_x = int(input("Ingrese la coordenada x de la zona a conocer: "))
    zona_y = int(input("Ingrese la coordenada y de la zona a conocer: "))

    # Verificar si las coordenadas están dentro del rango del laberinto
    if 0 <= zona_x < len(laberinto[0]) and 0 <= zona_y < len(laberinto):
        if laberinto[zona_y][zona_x] == 0:
            print("La zona es una pared (0).")
        elif laberinto[zona_y][zona_x] == 1:
            print("La zona es un camino (1).")
    else:
        print("Coordenadas fuera del rango del laberinto.")

    quiero_conocer_zona = input("¿Desea conocer otra zona del laberinto? (Sí/No): ").lower()

# Preguntar al usuario si quiere resolver el laberinto con BFS o DFS
resolucion_elegida = input("¿Desea resolver el laberinto con BFS (Búsqueda en Amplitud) o DFS (Búsqueda en Profundidad)? ").lower()
while resolucion_elegida not in ["bfs", "dfs"]:
    resolucion_elegida = input("Por favor, elija 'bfs' o 'dfs': ").lower()

# Resolución utilizando BFS
if resolucion_elegida == "bfs":
    camino_resuelto, arbol_busqueda = resolver_bfs(laberinto, x_inicial, y_inicial, x_meta, y_meta)
    if camino_resuelto is not None:
        print("Resolución utilizando BFS:")
        print(camino_resuelto)
        imprimir_arbol(arbol_busqueda)  # Mostrar el árbol de búsqueda y contar los hijos
        escribir_arbol(arbol_busqueda)  # Guardar el árbol de búsqueda en un archivo
        # Crear y guardar el grafo Pydot
        grafo = crear_grafo_pydot(arbol_busqueda)
        grafo.write('arbol_grafico_bfs.dot')
        grafo.write_png('arbol_grafico_bfs.png')
    else:
        print("No se encontró una solución utilizando BFS.")

# Resolución utilizando DFS
if resolucion_elegida == "dfs":
    camino_resuelto, arbol_busqueda = resolver_dfs(laberinto, x_inicial, y_inicial, x_meta, y_meta)
    if camino_resuelto is not None:
        print("Resolución utilizando DFS:")
        print(camino_resuelto)
        imprimir_arbol(arbol_busqueda)  # Mostrar el árbol de búsqueda y contar los hijos
        escribir_arbol(arbol_busqueda)  # Guardar el árbol de búsqueda en un archivo
        # Crear y guardar el grafo Pydot
        grafo = crear_grafo_pydot(arbol_busqueda)
        grafo.write('arbol_grafico_dfs.dot')
        grafo.write_png('arbol_grafico_dfs.png')
    else:
        print("No se encontró una solución utilizando DFS.")

# Bucle principal del juego
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Lógica para el movimiento del SerX
    if serx.x != x_meta or serx.y != y_meta:
        if resolucion_elegida == "bfs":
            serx.mover(camino_resuelto[0])  # Moverse siguiendo el camino BFS
            camino_resuelto.pop(0)  # Eliminar el primer movimiento
        elif resolucion_elegida == "dfs":
            serx.mover(camino_resuelto[0])  # Moverse siguiendo el camino DFS
            camino_resuelto.pop(0)  # Eliminar el primer movimiento

    # Dibujar el laberinto en la ventana
    win.fill(BLACK)
    for i in range(len(laberinto)):
        for j in range(len(laberinto[i])):
            if (
                abs(i - serx.y) <= serx.vision
                and abs(j - serx.x) <= serx.vision
            ):
                if laberinto[i][j] == 0:
                    pygame.draw.rect(win, BLACK, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                elif laberinto[i][j] == 1:
                    pygame.draw.rect(win, WHITE, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
            elif serx.visitado[i][j]:
                if laberinto[i][j] == 0:
                    pygame.draw.rect(win, BLACK, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                elif laberinto[i][j] == 1:
                    pygame.draw.rect(win, WHITE, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                
                    # Agregar lógica para marcar las intersecciones con 'O'
                    if (
                        i > 0 and i < len(laberinto)-1 and j > 0 and j < len(laberinto[i])-1
                        and laberinto[i-1][j] == 1 and laberinto[i+1][j] == 1
                        and laberinto[i][j-1] == 1 and laberinto[i][j+1] == 1
                    ):
                        font = pygame.font.Font(None, 36)
                        letra_o = font.render("O", True, BLACK)
                        win.blit(letra_o, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))
                
                if laberinto[i][j] == 2:  # Marcar casillas donde se debe elegir ('O')
                    pygame.draw.rect(win, BLACK, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                    font = pygame.font.Font(None, 36)
                    letra_o = font.render("O", True, BLACK)
                    win.blit(letra_o, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))
            
    # Dibujar la imagen de la meta en las coordenadas de la meta
    x_meta_pos = x_meta * CELDA_SIZE
    y_meta_pos = y_meta * CELDA_SIZE
    win.blit(meta_image, (x_meta_pos, y_meta_pos))
    
    for i in range(len(serx.visitado)):
        for j in range(len(serx.visitado[i])):
            if serx.visitado[i][j] and laberinto[i][j] == 1:
                font = pygame.font.Font(None, 36)
                letra_v = font.render("V", True, BLUE)
                win.blit(letra_v, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))
    
    # Dibujar el SerX
    serx.dibujar(win)

    # Actualizar la pantalla
    pygame.display.update()

    pygame.time.delay(500)  # Pausa de 500 milisegundos

    # Verificar si el SerX llegó a la meta
    if serx.x == x_meta and serx.y == y_meta:
        # Mostrar el mensaje de victoria
        font = pygame.font.Font(None, 36)
        mensaje = font.render("¡Llegaste a la Meta, FELICIDADES!", True, WHITE)
        win.blit(mensaje, (200, 200))

        # Guardar el árbol de búsqueda en un archivo de texto
        if arbol_busqueda:
            escribir_arbol(arbol_busqueda)

        pygame.display.update()
        pygame.time.delay(3000)  # Pausa durante 3 segundos

        run = False  # Salir del bucle al final del juego

# Mostrar el número de movimientos y el costo total al final del juego
print(f"Número de movimientos: {serx.movimientos}")
print(f"Costo total: {serx.costo_total}")

pygame.quit()
sys.exit()
