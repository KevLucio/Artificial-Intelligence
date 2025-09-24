"""
@author: Kevyn Alejandro P�rez Lucio
"""

import pygame
import sys

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

# Cargar el laberinto desde un archivo TXT
def cargar_laberinto(nombre_archivo):
    laberinto = []
    with open(nombre_archivo, 'r') as file:
        for line in file:
            row = [int(char) for char in line.strip().split(',')]
            laberinto.append(row)
    return laberinto

# Clase para el ser X
class SerX:
    def __init__(self, x, y, avatar):
        self.x = x
        self.y = y
        self.avatar = avatar
        self.movimientos = 0
        self.costo_total = 0
        self.vision = 1  # Radio de visión (una casilla alrededor del ser X)
        self.visitado = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]
        self.eleccion = [[False for _ in range(len(laberinto[0]))] for _ in range(len(laberinto))]

    # Modificar el método mover del ser X
    def mover(self, direccion):
        # Coordenadas actuales
        x_actual, y_actual = self.x, self.y
    
        if direccion == "W" and self.y > 0 and laberinto[self.y - 1][self.x] == 1:
            self.y -= 1
        elif direccion == "A" and self.x > 0 and laberinto[self.y][self.x - 1] == 1:
            self.x -= 1
        elif direccion == "S" and self.y < len(laberinto) - 1 and laberinto[self.y + 1][self.x] == 1:
            self.y += 1
        elif direccion == "D" and self.x < len(laberinto[0]) - 1 and laberinto[self.y][self.x + 1] == 1:
            self.x += 1
    
        # Marcar la casilla como visitada
        self.visitado[self.y][self.x] = True
    
        # Actualizar el costo total
        if (self.x, self.y) != (x_actual, y_actual):
            self.movimientos += 1
            self.costo_total += 1  # Puedes ajustar la métrica de costo según tus necesidades

    def dibujar(self, win):
        # Dibujar el ser X en la ventana
        x_pos = self.x * CELDA_SIZE
        y_pos = self.y * CELDA_SIZE
        avatar_image = pygame.image.load(self.avatar)
        win.blit(avatar_image, (x_pos, y_pos))

    def mostrar_vision(self):
        # Mostrar la visión alrededor del ser X
        for i in range(max(0, self.y - self.vision), min(len(laberinto), self.y + self.vision + 1)):
            for j in range(max(0, self.x - self.vision), min(len(laberinto[0]), self.x + self.vision + 1)):
                if self.visitado[i][j]:
                    if laberinto[i][j] == 0:
                        pygame.draw.rect(win, BLACK, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                    elif laberinto[i][j] == 1:
                        pygame.draw.rect(win, WHITE, (j * CELDA_SIZE, i * CELDA_SIZE, CELDA_SIZE, CELDA_SIZE))
                    if self.eleccion[i][j]:
                        font = pygame.font.Font(None, 36)
                        letra_o = font.render("O", True, BLACK)
                        letra_v = font.render("V", True, BLUE)
                        win.blit(letra_o, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))
                        if laberinto[i][j] == 1:  # Dibuja "V" solo en casillas de camino
                            win.blit(letra_v, (j * CELDA_SIZE + 15, i * CELDA_SIZE + 15))

# Tamaño de las celdas en píxeles
CELDA_SIZE = 40

# Nombres de los avatares y sus imágenes (debes tener archivos de imagen para los avatares)
avatares = {
    "humano": "humano.png",
    "mono": "mono.png",
    "pulpo": "pulpo.png",
    "pie grande": "pie_grande.png"
}

# Cargar el laberinto y configurar la posición inicial
nombre_archivo = "laberinto.txt"
laberinto = cargar_laberinto(nombre_archivo)
x_inicial = int(input("Ingrese la coordenada x inicial: "))
y_inicial = int(input("Ingrese la coordenada y inicial: "))
avatar = avatares[input("Elija el avatar (humano/mono/pulpo/pie grande): ")]
serx = SerX(x_inicial, y_inicial, avatar)

# Coordenadas de la meta
x_meta = int(input("Ingrese la coordenada x de la meta: "))
y_meta = int(input("Ingrese la coordenada y de la meta: "))

# Cargar la imagen de la meta
meta_image = pygame.image.load("meta.png")

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



# Bucle principal del juego
run = True
while run:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                run = False
            elif event.key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                direccion = ""
                if event.key == pygame.K_w:
                    direccion = "W"
                elif event.key == pygame.K_a:
                    direccion = "A"
                elif event.key == pygame.K_s:
                    direccion = "S"
                elif event.key == pygame.K_d:
                    direccion = "D"
                serx.mover(direccion)

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

    # Dibujar el ser X
    serx.dibujar(win)

    # Actualizar la pantalla
    pygame.display.update()

    # Verificar si el ser X llegó a la meta
    if serx.x == x_meta and serx.y == y_meta:
        # Mostrar el mensaje de victoria
        font = pygame.font.Font(None, 36)
        mensaje = font.render("¡Llegaste a la Meta, FELICIDADES!", True, WHITE)
        win.blit(mensaje, (200, 200))

        pygame.display.update()
        pygame.time.delay(3000)  # Mostrar el mensaje durante 3 segundos
        break

# Mostrar el número de movimientos y el costo total al final del juego
print(f"Número de movimientos: {serx.movimientos}")
print(f"Costo total: {serx.costo_total}")

pygame.quit()
sys.exit()