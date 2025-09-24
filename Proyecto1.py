"""
@author: Kevyn Alejandro Perez Lucio
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
WIDTH, HEIGHT = 900, 700
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Laberinto")

# Definir colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

arbol_busqueda = {}

# Cargar imagenes de texturas
texturas = {
    0: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\muro.png"),
    1: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\piso.png"),
    2: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\mountain.jpg"),
    3: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\tierra.jpg"),
    4: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\bosque.jpg"),
    5: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\arena.jpg"),
    6: pygame.image.load("C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Texturas\\agua.jpg")
}

# Diccionario para mapear las letras a las descripciones y colores
letra_a_descripcion_color = {
    'k': ("Key", (255, 255, 0)),  # Key: Amarillo
    'd': ("Dark Temple", (0, 0, 0)),  # Dark Temple: Negro
    'p': ("Portal", (255, 0, 0))  # Portal: Rojo
}

# Cargar el laberinto desde un archivo TXT
def cargar_laberinto(nombre_archivo):
    laberinto = []
    with open(nombre_archivo, 'r') as file:
        for line in file:
            row = [char for char in line.strip().split(',')]
            laberinto.append(row)
    return laberinto

# Funcion para calcular la distancia euclidiana entre dos puntos
def calcular_distancia(x1, y1, x2, y2):
    return math.hypot(x2 - x1, y2 - y1)

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
    arbol_busqueda = {inicio: []}  # Inicializamos el Ã¡rbol con el nodo inicial

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
                    arbol_busqueda[sucesor] = []  # Agregamos el sucesor al Ã¡rbol

        for sucesor in sucesores:
            if any(nodo.x == sucesor.x and nodo.y == sucesor.y for nodo in cerrados):
                continue

            if any(nodo.x == sucesor.x and nodo.y == sucesor.y and sucesor.g >= nodo.g for nodo in abiertos):
                continue

            # Agregamos el sucesor al Ã¡rbol como hijo del nodo actual
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
            costo_casilla = self.costo_casilla.get(tipo_casilla, 1)  # Utiliza get
            self.movimientos += 1
            self.costo_total += costo_casilla  # Considera el costo de la casilla

    def mover_con_prioridad(self, x_meta, y_meta):
        if not self.caminos_resueltos:
            return
    
        # Obtener el camino resuelto actual
        camino_actual = self.caminos_resueltos[0]
    
        if camino_actual:
            # Obtener la próxima casilla en el camino
            x_destino, y_destino = camino_actual[0]
    
            if (x_destino, y_destino) == (self.x, self.y):
                # La próxima casilla es la casilla actual, por lo que la hemos alcanzado
                # Eliminamos esta casilla del camino
                camino_actual.pop(0)
    
            if camino_actual:
                # Todavía hay casillas en el camino, así que movámonos hacia la próxima
                x_destino, y_destino = camino_actual[0]
    
                if self.x < x_destino:
                    self.mover("D")
                elif self.x > x_destino:
                    self.mover("A")
                elif self.y < y_destino:
                    self.mover("S")
                elif self.y > y_destino:
                    self.mover("W")
            else:
                # Hemos llegado al final del camino
                # Eliminamos este camino de la lista de caminos resueltos
                self.caminos_resueltos.pop(0)
    
                if not self.caminos_resueltos:
                    # No quedan más caminos
                    self.caminos_resueltos = None

    def dibujar(self, win):
        x_pos = self.x * CELDA_SIZE
        y_pos = self.y * CELDA_SIZE
        avatar_image = pygame.image.load(self.avatar)
        win.blit(avatar_image, (x_pos, y_pos))

class Humano(SerX):
    def __init__(self, x, y, avatar):
        super().__init__(x, y, avatar)
        self.nombre = "Humano"
        self.costo_casilla = {
            1: 1,  # Piso
            2: 3,  # Montana
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
            2: 2,  # Montana
            3: 2,  # Tierra
            4: 2,  # Bosque
            5: 3,  # Arena
            6: 4,  # Agua
        }
        
class Pulpo(SerX):
    def __init__(self, x, y, avatar):
        super().__init__(x, y, avatar)
        self.nombre = "Pulpo"
        # Define los costos de las casillas para el avatar Mono
        self.costo_casilla = {
            1: 3,  # Piso
            2: 4,  # Montana
            3: 3,  # Tierra
            4: 4,  # Bosque
            5: 2,  # Arena
            6: 1,  # Agua
        }
        
class Pie_Grande(SerX):
    def __init__(self, x, y, avatar):
        super().__init__(x, y, avatar)
        # Define los costos de las casillas para el avatar Mono
        self.costo_casilla = {
            1: 2,  # Piso
            2: 1,  # Montana
            3: 2,  # Tierra
            4: 1,  # Bosque
            5: 3,  # Arena
            6: 4,  # Agua
        }

# Funcion para escribir el arbol de busqueda en un archivo de texto
def escribir_arbol(arbol_busqueda):
    if arbol_busqueda is not None:
        with open("arbol_busqueda.txt", "w") as archivo:
            for nodo, hijos in arbol_busqueda.items():
                hijos_str = ", ".join([f"({nodo.x}, {nodo.y})" for nodo in hijos])
                archivo.write(f"Nodo: ({nodo.x}, {nodo.y}), Hijos: [{hijos_str}]\n")
    else:
        print("El Arbol de busqueda esta¡ vaci­o o no ha sido inicializado.")
        
def crear_grafo_pydot(arbol):
    graph = pydot.Dot(graph_type='graph')

    for nodo, hijos in arbol.items():
        node = pydot.Node(f"({nodo.x}, {nodo.y})")
        graph.add_node(node)

        for hijo in hijos:
            edge = pydot.Edge(f"({nodo.x}, {nodo.y})", f"({hijo.x}, {hijo.y})")
            graph.add_edge(edge)

    return graph

# Tamano de las celdas en pi­xeles
CELDA_SIZE = 40

# Cargar el laberinto y configurar la posicion inicial
nombre_archivo = "mapa_proyecto.txt"
laberinto = cargar_laberinto(nombre_archivo)

avatares = {
    "Humano": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Avatar\\humano.png",
    "Mono": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Avatar\\mono.png",
    "Pulpo": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Avatar\\pulpo.png",
    "Pie_Grande": "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Avatar\\pie_grande.png"
}

avatares_activos = []

numero_avatares = 2

# Crear un Humano de forma predeterminada
x_inicial_humano =  8
y_inicial_humano =  7
humano = Humano(x_inicial_humano, y_inicial_humano, "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Avatar\\humano.png")
avatares_activos.append(humano)

# Crear un Pulpo de forma predeterminada
x_inicial_pulpo = 14
y_inicial_pulpo = 12
pulpo = Pulpo(x_inicial_pulpo, y_inicial_pulpo, "C:\\Users\\kev_a\\OneDrive\\Documentos\\DOC POLI\\ESCOM\\4to Semestre\\FIA\\1erParcial\\Proyecto 1\\Avatar\\pulpo.png")
avatares_activos.append(pulpo)

# Definir las coordenadas de la casilla del portal
x_portal = 11
y_portal = 10

# Coordenadas de la meta
x_meta = x_portal
y_meta = y_portal

# Cargar la imagen de la meta
meta_image = pygame.image.load("meta.png")

x_dark_temple = 11  # Columna donde se encuentra el Dark Temple (casilla "d")
y_dark_temple = 3   # Fila donde se encuentra el Dark Temple (casilla "d")

x_llave = 14       # Columna donde se encuentra la llave (casilla "k")
y_llave = 15      # Fila donde se encuentra la llave (casilla "k")

# Definir los destinos para el Avatar 1 y el Avatar 2
destino_avatar1 = (x_dark_temple, y_dark_temple)
destino_avatar2 = (x_llave, y_llave)

# Calcular caminos y árboles de búsqueda para cada avatar activo
caminos_resueltos = {}
arboles_busqueda = {}

# Calcular caminos y árboles de búsqueda para el Humano y el Pulpo
caminos_resueltos_humano, arbol_busqueda_humano = resolver_a_star(laberinto, x_inicial_humano, y_inicial_humano, x_dark_temple, y_dark_temple)
caminos_resueltos_pulpo, arbol_busqueda_pulpo = resolver_a_star(laberinto, x_inicial_pulpo, y_inicial_pulpo, x_llave, y_llave)

# Verificar si se encontró un camino para al menos uno de los avatares
algun_camino_encontrado_humano = caminos_resueltos_humano is not None
algun_camino_encontrado_pulpo = caminos_resueltos_pulpo is not None

if algun_camino_encontrado_humano and algun_camino_encontrado_pulpo:
    print("Caminos resueltos para el Humano y el Pulpo para su respectivo destino.")

    # Imprime y guarda los caminos y árboles de búsqueda del Humano
    print("Resolución utilizando A* para el Humano:")
    print(caminos_resueltos_humano)
    # Crear y guardar el árbol de búsqueda solo cuando se ha encontrado un camino
    escribir_arbol(arbol_busqueda_humano)  # Guardar el árbol de búsqueda en un archivo
    # Crear y guardar el grafo Pydot
    grafo_humano = crear_grafo_pydot(arbol_busqueda_humano)
    grafo_humano.write('arbol_grafico_a_star_humano.dot')
    grafo_humano.write_png('arbol_grafico_a_star_humano.png')

    # Imprime y guarda los caminos y árboles de búsqueda del Pulpo
    print("Resolución utilizando A* para el Pulpo:")
    print(caminos_resueltos_pulpo)
    # Crear y guardar el árbol de búsqueda solo cuando se ha encontrado un camino
    escribir_arbol(arbol_busqueda_pulpo)  # Guardar el árbol de búsqueda en un archivo
    # Crear y guardar el grafo Pydot
    grafo_pulpo = crear_grafo_pydot(arbol_busqueda_pulpo)
    grafo_pulpo.write('arbol_grafico_a_star_pulpo.dot')
    grafo_pulpo.write_png('arbol_grafico_a_star_pulpo.png')

for serx in avatares_activos:
    camino_resuelto, arbol_busqueda = resolver_a_star(laberinto, serx.x, serx.y, x_meta, y_meta)
    caminos_resueltos[serx] = camino_resuelto
    arboles_busqueda[serx] = arbol_busqueda

# Resolver el camino desde el subdestino del Humano hasta el portal
camino_resuelto_humano_portal, arbol_busqueda_humano_portal = resolver_a_star(laberinto, x_dark_temple, y_dark_temple, x_portal, y_portal)

# Resolver el camino desde el subdestino del Pulpo hasta el portal
camino_resuelto_pulpo_portal, arbol_busqueda_pulpo_portal = resolver_a_star(laberinto, x_llave, y_llave, x_portal, y_portal)

# Verificar si se encontró un camino para ambos avatares
if camino_resuelto_humano_portal is not None and camino_resuelto_pulpo_portal is not None:
    print("Caminos resueltos para el Humano y el Pulpo desde sus subdestinos hasta el portal.")

    # Imprimir y guardar el camino del Humano
    print("Resolución utilizando A* para el Humano hacia el portal:")
    print(camino_resuelto_humano_portal)
    escribir_arbol(arbol_busqueda_humano_portal)
    grafo_humano_portal = crear_grafo_pydot(arbol_busqueda_humano_portal)
    grafo_humano_portal.write('arbol_grafico_a_star_humano_portal.dot')
    grafo_humano_portal.write_png('arbol_grafico_a_star_humano_portal.png')

    # Imprimir y guardar el camino del Pulpo
    print("Resolución utilizando A* para el Pulpo hacia el portal:")
    print(camino_resuelto_pulpo_portal)
    escribir_arbol(arbol_busqueda_pulpo_portal)
    grafo_pulpo_portal = crear_grafo_pydot(arbol_busqueda_pulpo_portal)
    grafo_pulpo_portal.write('arbol_grafico_a_star_pulpo_portal.dot')
    grafo_pulpo_portal.write_png('arbol_grafico_a_star_pulpo_portal.png')

else:
    print("No se encontró una solución utilizando A* para ambos avatares hacia el portal.")

# Variable para rastrear si todos los avatares llegaron a sus destinos
llegada_destinos = False

# Variable para rastrear si ambos avatares llegaron a sus subdestinos
llegada_subdestinos = {"Humano": False, "Pulpo": False}

# Variables para rastrear si el humano llegó al Dark Temple y el pulpo llegó a la llave
humano_llego_al_dark_temple = False
pulpo_llego_a_la_llave = False

# Variable para controlar cuál avatar se mueve primero
primer_avatar = humano

# Bucle principal del juego
run = True

while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False

    # Verificar si ambos avatares llegaron a sus subdestinos
    if not llegada_destinos:
        for serx in avatares_activos:
            if (serx.x, serx.y) != (x_meta, y_meta):
                if caminos_resueltos[serx]:
                    if len(caminos_resueltos[serx]) > 0:
                        # Comprobar el destino del avatar
                        if serx == humano:
                            x_destino, y_destino = (x_dark_temple, y_dark_temple) if not humano_llego_al_dark_temple else (x_portal, y_portal)
                        else:
                            x_destino, y_destino = (x_llave, y_llave) if not pulpo_llego_a_la_llave else (x_portal, y_portal)
    
                        if serx.x < x_destino:
                            serx.mover("D")
                        elif serx.x > x_destino:
                            serx.mover("A")
                        elif serx.y < y_destino:
                            serx.mover("S")
                        elif serx.y > y_destino:
                            serx.mover("W")
                        caminos_resueltos[serx].pop(0)
                    else:
                        if not llegada_subdestinos["Humano"] and serx == humano:
                            llegada_subdestinos["Humano"] = True
                        elif not llegada_subdestinos["Pulpo"] and serx == pulpo:
                            llegada_subdestinos["Pulpo"] = True
                        if not llegada_subdestinos["Humano"] or not llegada_subdestinos["Pulpo"]:
                            # Avatar llegó a su destino intermedio, ahora se mueve hacia el portal
                            if serx == humano:
                                destino_avatar1 = (x_portal, y_portal)
                            else:
                                destino_avatar2 = (x_portal, y_portal)
                else:
                    # Si no hay un camino disponible, mueve hacia el portal
                    x_destino, y_destino = (x_portal, y_portal)
                    if serx.x < x_destino:
                        serx.mover("D")
                    elif serx.x > x_destino:
                        serx.mover("A")
                    elif serx.y < y_destino:
                        serx.mover("S")
                    elif serx.y > y_destino:
                        serx.mover("W")
                serx.costo_total += serx.costo_casilla.get(laberinto[serx.y][serx.x], 1)  # Actualiza el costo total
            else:
                # El avatar llegó a su destino final, no es necesario moverlo más
                caminos_resueltos[serx] = []
        if llegada_subdestinos["Humano"] and llegada_subdestinos["Pulpo"]:
            llegada_destinos = True

    # Cambiar el avatar que se mueve en la próxima iteración
    primer_avatar = humano if not llegada_subdestinos["Pulpo"] else pulpo

    # Dibujar el laberinto en la ventana con texturas y colores según las letras
    for i in range(len(laberinto)):
        for j in range(len(laberinto[i])):
            if (
                abs(i - primer_avatar.y) <= primer_avatar.vision
                and abs(j - primer_avatar.x) <= primer_avatar.vision
            ):
                letra = laberinto[i][j]
                if letra in letra_a_descripcion_color:
                    descripcion, color = letra_a_descripcion_color[letra]
                    pygame.draw.rect(win, color, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                else:
                    textura = texturas[int(letra)]
                    x_pos = j * CELDA_SIZE
                    y_pos = i * CELDA_SIZE
                    win.blit(textura, (x_pos, y_pos))

    # Dibujar la imagen de la meta en las coordenadas de la meta
    x_meta_pos = x_meta * CELDA_SIZE
    y_meta_pos = y_meta * CELDA_SIZE
    win.blit(meta_image, (x_meta_pos, y_meta_pos))

    # Dibujar los avatares
    for serx in avatares_activos:
        serx.dibujar(win)

    # Actualizar la pantalla
    pygame.display.update()

    # Agregar un pequeño retraso para ver el movimiento
    pygame.time.delay(800)  

    # Verificar si cada avatar llegó a su destino respectivo
    for serx in avatares_activos:
        if (serx.x, serx.y) == (destino_avatar1 if serx == humano else destino_avatar2):
            # Mostrar un mensaje de victoria para cada avatar
            font = pygame.font.Font(None, 36)
            texto_victoria = font.render(f"¡{serx.nombre} llegó a su destino!", True, (255, 255, 255))
            win.blit(texto_victoria, (50, 50))
            pygame.display.update()
    
    # Verificar si ambos avatares llegaron al portal
    if (humano.x, humano.y) == (x_portal, y_portal) and (pulpo.x, pulpo.y) == (x_portal, y_portal):
        # Mostrar el mensaje cuando ambos avatares estén en el portal
        font = pygame.font.Font(None, 36)
        texto_portal = font.render("¡Llegaste al Portal, Hasta Luego!", True, (255, 255, 255))
        win.blit(texto_portal, (50, 100))
        pygame.display.update()
        pygame.time.delay(2000)  # Esperar 2 segundos antes de cerrar la ventana
        run = False
        
    # Manejar eventos y actualizar la pantalla
    pygame.event.pump()

# Mostrar el número de movimientos y el costo total al final del juego para cada avatar
for serx in avatares_activos:
    print(f"{serx.__class__.__name__} (Avatar {avatares_activos.index(serx) + 1}):")
    print(f"Número de movimientos: {serx.movimientos}")
    print(f"Costo total: {serx.costo_total}")
    print()

pygame.quit()
sys.exit()
