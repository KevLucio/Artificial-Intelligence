"""
@author: Kevyn Alejandro Pérez Lucio
"""

import pygame
import sys
import math
import heapq
import pydot
import graphviz
import random

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

arbol_busqueda = {}

# Cargar imágenes de texturas
texturas = {
    0: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\muro.png"),
    1: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\piso.png"),
    2: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\mountain.jpg"),
    3: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\tierra.jpg"),
    4: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\bosque.jpg"),
    5: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\arena.jpg"),
    6: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Texturas\\agua.jpg")
}

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

# Clase para el nodo en el algoritmo A*
class NodoAStar:
    def __init__(self, x, y, padre=None):
        self.x = x
        self.y = y
        self.padre = padre
        self.g = 0
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f

def resolver_a_star(laberinto, x_inicial, y_inicial, x_meta, y_meta):
    inicio = NodoAStar(x_inicial, y_inicial)
    inicio.g = inicio.h = inicio.f = 0
    meta = NodoAStar(x_meta, y_meta)
    abiertos = []
    cerrados = []
    arbol_busqueda = {inicio: []}  # Inicializamos el árbol con el nodo inicial

    heapq.heappush(abiertos, inicio)

    while abiertos:
        actual = heapq.heappop(abiertos)

        if actual.x == meta.x and actual.y == meta.y:
            camino = []
            nodo = actual
            while nodo is not None:
                camino.append((nodo.x, nodo.y))
                nodo = nodo.padre
            camino.reverse()
            return camino, arbol_busqueda

        sucesores = []
        for dx, dy, direccion in [(1, 0, "D"), (-1, 0, "A"), (0, 1, "S"), (0, -1, "W")]:
            x_nuevo, y_nuevo = actual.x + dx, actual.y + dy
            if 0 <= x_nuevo < len(laberinto[0]) and 0 <= y_nuevo < len(laberinto):
                if laberinto[y_nuevo][x_nuevo] != 0:
                    sucesor = NodoAStar(x_nuevo, y_nuevo, actual)
                    sucesor.g = actual.g + 1
                    sucesor.h = calcular_distancia(sucesor.x, sucesor.y, x_meta, y_meta)
                    sucesor.f = sucesor.g + sucesor.h
                    sucesores.append(sucesor)
                    arbol_busqueda[sucesor] = []  # Agregamos el sucesor al árbol

        for sucesor in sucesores:
            if any(nodo.x == sucesor.x and nodo.y == sucesor.y for nodo in cerrados):
                continue

            if any(nodo.x == sucesor.x and nodo.y == sucesor.y and sucesor.g >= nodo.g for nodo in abiertos):
                continue

            # Agregamos el sucesor al árbol como hijo del nodo actual
            for nodo, hijos in arbol_busqueda.items():
                if nodo.x == actual.x and nodo.y == actual.y:
                    hijos.append(sucesor)
                    break

            heapq.heappush(abiertos, sucesor)

        cerrados.append(actual)

    return None, arbol_busqueda

# Clase para el ser X
class SerX:
    def __init__(self, x, y, avatar):
        self.x = x
        self.y = y
        self.avatar = avatar
        self.movimientos = 0
        self.costo_total = 0
        self.vision = 15
        self.visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
        self.costo_casilla = 1
        
    def mover(self, direccion):
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
            and laberinto[y_nuevo][x_nuevo] != 0
        ):
            # Puede moverse en esta dirección
            self.x = x_nuevo
            self.y = y_nuevo
            tipo_casilla = laberinto[y_nuevo][x_nuevo]
            # Calcula el costo de la casilla según el avatar
            costo_casilla = self.costo_casilla.get(tipo_casilla, 1)
            self.movimientos += 1
            self.costo_total += costo_casilla  # Considera el costo de la casilla

    def mover_con_prioridad(self, x_meta, y_meta):
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
                and laberinto[y_nuevo][x_nuevo] != 0
                and not self.visitado[y_nuevo][x_nuevo]
            ):
                # Puede moverse en esta dirección
                self.mover(direccion)
                return

    def dibujar(self, win):
        x_pos = self.x * CELDA_SIZE
        y_pos = self.y * CELDA_SIZE
        avatar_image = pygame.image.load(self.avatar)
        win.blit(avatar_image, (x_pos, y_pos))

class Humano(SerX):
    def __init__(self, x, y, avatar):
        super().__init__(x, y, avatar)
        self.costo_casilla = {
            1: 1,  # Piso
            2: 3,  # Montaña
            3: 2,  # Tierra
            4: 2,  # Bosque
            5: 3,  # Arena
            6: 3,  # Agua
        }

class Mono(SerX):
    def __init__(self, x, y, avatar):
        super().__init__(x, y, avatar)
        # Define los costos de las casillas para el avatar Mono
        self.costo_casilla = {
            1: 1,  # Piso
            2: 2,  # Montaña
            3: 2,  # Tierra
            4: 1,  # Bosque
            5: 3,  # Arena
            6: 4,  # Agua
        }
        
class Pulpo(SerX):
    def __init__(self, x, y, avatar):
        super().__init__(x, y, avatar)
        # Define los costos de las casillas para el avatar Mono
        self.costo_casilla = {
            1: 3,  # Piso
            2: 4,  # Montaña
            3: 3,  # Tierra
            4: 4,  # Bosque
            5: 2,  # Arena
            6: 1,  # Agua
        }
        
class Pie_Grande(SerX):
    def __init__(self, x, y, avatar):
        avatar_name = avatar.replace(" ", "_")
        super().__init__(x, y, avatar)
        # Define los costos de las casillas para el avatar Mono
        self.costo_casilla = {
            1: 2,  # Piso
            2: 1,  # Montaña
            3: 2,  # Tierra
            4: 1,  # Bosque
            5: 3,  # Arena
            6: 4,  # Agua
        }

# Función para escribir el árbol de búsqueda en un archivo de texto
def escribir_arbol(arbol_busqueda):
    if arbol_busqueda is not None:
        with open("arbol_busqueda.txt", "w") as archivo:
            for nodo, hijos in arbol_busqueda.items():
                hijos_str = ", ".join([f"({nodo.x}, {nodo.y})" for nodo in hijos])
                archivo.write(f"Nodo: ({nodo.x}, {nodo.y}), Hijos: [{hijos_str}]\n")
    else:
        print("El árbol de búsqueda está vacío o no ha sido inicializado.")
        
def crear_grafo_pydot(arbol):
    graph = pydot.Dot(graph_type='graph')

    for nodo, hijos in arbol.items():
        node = pydot.Node(f"({nodo.x}, {nodo.y})")
        graph.add_node(node)

        for hijo in hijos:
            edge = pydot.Edge(f"({nodo.x}, {nodo.y})", f"({hijo.x}, {hijo.y})")
            graph.add_edge(edge)

    return graph

# Tamaño de las celdas en píxeles
CELDA_SIZE = 40

# Cargar el laberinto y configurar la posición inicial
nombre_archivo = "mapa2.txt"
laberinto = cargar_laberinto(nombre_archivo)

avatares = {
    "Humano": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Avatar\\humano.png",
    "Mono": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Avatar\\mono.png",
    "Pulpo": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Avatar\\pulpo.png",
    "Pie_Grande": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Practica3\\Avatar\\pie_grande.png"
}

# Preguntar al usuario qué avatar desea utilizar
print("Avatares disponibles:")
for i, avatar in enumerate(avatares, start=1):
    print(f"{i}. {avatar}")
avatar_index = int(input("Seleccione un avatar (1-4): "))
avatar_name = list(avatares.keys())[avatar_index - 1]
avatar_image_path = avatares[avatar_name]
# Reemplaza los espacios en blanco en el nombre del avatar con guiones bajos
avatar_name = avatar_name.replace(" ", "_")

x_inicial = int(input("Ingrese la coordenada x inicial: "))
y_inicial = int(input("Ingrese la coordenada y inicial: "))

if avatar_name == "Humano":
    serx = Humano(x_inicial, y_inicial, avatar_image_path)
elif avatar_name == "Mono":
    serx = Mono(x_inicial, y_inicial, avatar_image_path)
elif avatar_name == "Pulpo":
    serx = Pulpo(x_inicial, y_inicial, avatar_image_path)
elif avatar_name == "Pie_Grande":
    serx = Pie_Grande(x_inicial, y_inicial, avatar_image_path)

# Coordenadas de la meta
x_meta = int(input("Ingrese la coordenada x de la meta: "))
y_meta = int(input("Ingrese la coordenada y de la meta: "))

# Cargar la imagen de la meta
meta_image = pygame.image.load("meta.png")

camino_resuelto, arbol_busqueda = resolver_a_star(laberinto, serx.x, serx.y, x_meta, y_meta)
if camino_resuelto is not None:
    print("Resolución utilizando A*:")
    print(camino_resuelto)
    # Crear y guardar el árbol de búsqueda solo cuando se ha encontrado un camino
    escribir_arbol(arbol_busqueda)  # Guardar el árbol de búsqueda en un archivo
    # Crear y guardar el grafo Pydot
    grafo = crear_grafo_pydot(arbol_busqueda)
    grafo.write('arbol_grafico_a_star.dot')
    grafo.write_png('arbol_grafico_a_star.png')

else:
    print("No se encontró una solución utilizando A*.")

# Bucle principal del juego
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Verificar si el SerX llegó a la meta
    if serx.x == x_meta and serx.y == y_meta:
        # Mostrar el mensaje de victoria
        font = pygame.font.Font(None, 36)
        mensaje = font.render("¡Llegaste a la Meta, FELICIDADES!", True, WHITE)
        win.blit(mensaje, (200, 200))

        pygame.display.update()
        pygame.time.delay(3000)  # Pausa durante 3 segundos

        run = False  # Salir del bucle al final del juego
    else:
        # Lógica para el movimiento del SerX
        if camino_resuelto:
            if len(camino_resuelto) > 0:
                x_destino, y_destino = camino_resuelto[0]
                if serx.x < x_destino:
                    serx.mover("D")
                elif serx.x > x_destino:
                    serx.mover("A")
                elif serx.y < y_destino:
                    serx.mover("S")
                elif serx.y > y_destino:
                    serx.mover("W")
                camino_resuelto.pop(0)
        else:
            # Si no hay un camino disponible, mueve al azar
            direccion_aleatoria = random.choice(["W", "A", "S", "D"])
            serx.mover(direccion_aleatoria)

    # Dibujar el laberinto en la ventana con texturas
    for i in range(len(laberinto)):
        for j in range(len(laberinto[i])):
            if (
                abs(i - serx.y) <= serx.vision
                and abs(j - serx.x) <= serx.vision
            ):
                textura = texturas[laberinto[i][j]]
                x_pos = j * CELDA_SIZE
                y_pos = i * CELDA_SIZE
                win.blit(textura, (x_pos, y_pos))

    # Dibujar la imagen de la meta en las coordenadas de la meta
    x_meta_pos = x_meta * CELDA_SIZE
    y_meta_pos = y_meta * CELDA_SIZE
    win.blit(meta_image, (x_meta_pos, y_meta_pos))

    # Dibujar el SerX
    serx.dibujar(win)

    # Actualizar la pantalla
    pygame.display.update()

    pygame.time.delay(500)  # Pausa de 500 milisegundos

# Mostrar el número de movimientos y el costo total al final del juego
print(f"Número de movimientos: {serx.movimientos}")
print(f"Costo total: {serx.costo_total}")

pygame.quit()
sys.exit()
