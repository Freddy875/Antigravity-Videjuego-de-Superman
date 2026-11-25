"""
efectos.py — Sistema de partículas, explosiones, chispas y sacudida de pantalla.
Cumple con las especificaciones de GUIA_ESTILO.md (partículas cuadradas de 4-8 px,
halos brillantes, chispas de impacto y fragmentos metálicos).
"""

import math
import random
import pygame
import config

class Particula:
    def __init__(self, x, y, vx, vy, color, vida, tamano=6, desaceleracion=0.96):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.color = color
        self.vida = vida
        self.vida_max = vida
        self.tamano = tamano
        self.desaceleracion = desaceleracion

    def actualizar(self, dt):
        self.x += self.vx * (dt * 60)
        self.y += self.vy * (dt * 60)
        self.vx *= self.desaceleracion
        self.vy *= self.desaceleracion
        self.vida -= dt
        return self.vida > 0

    def dibujar(self, superficie):
        if self.vida <= 0:
            return
        ratio = self.vida / self.vida_max
        tam = max(2, int(self.tamano * ratio))
        # Partículas cuadradas estilo pixel art 16 bits
        rect = pygame.Rect(int(self.x - tam // 2), int(self.y - tam // 2), tam, tam)
        pygame.draw.rect(superficie, self.color, rect)


class TextoFlotante:
    def __init__(self, x, y, texto, color=(255, 255, 255), duracion=0.8):
        self.x = x
        self.y = y
        self.texto = texto
        self.color = color
        self.duracion = duracion
        self.vida = duracion

    def actualizar(self, dt):
        self.y -= 35 * dt
        self.vida -= dt
        return self.vida > 0

    def dibujar(self, superficie, fuente):
        if self.vida <= 0:
            return
        surf = fuente.render(self.texto, True, self.color)
        superficie.blit(surf, (int(self.x), int(self.y)))


class SistemaEfectos:
    def __init__(self):
        self.particulas = []
        self.textos = []
        self.tiempo_sacudida = 0.0
        self.fuerza_sacudida = 0.0
        self.fuente_retro = None
        self.cargar_fuente()

    def cargar_fuente(self):
        try:
            self.fuente_retro = pygame.font.SysFont("Press Start 2P, Consolas, Courier New", 14, bold=True)
        except Exception:
            self.fuente_retro = pygame.font.Font(None, 18)

    def sacudir_pantalla(self, duracion=0.3, fuerza=6.0):
        self.tiempo_sacudida = duracion
        self.fuerza_sacudida = fuerza

    def obtener_desplazamiento_sacudida(self):
        if self.tiempo_sacudida > 0:
            dx = random.uniform(-self.fuerza_sacudida, self.fuerza_sacudida)
            dy = random.uniform(-self.fuerza_sacudida, self.fuerza_sacudida)
            return int(dx), int(dy)
        return 0, 0

    def crear_chispas_impacto(self, x, y, color=(255, 210, 63), cantidad=12):
        """Chispas cuadradas por impacto de golpe o láser."""
        for _ in range(cantidad):
            ang = random.uniform(0, 2 * math.pi)
            vel = random.uniform(3.0, 8.0)
            vx = math.cos(ang) * vel
            vy = math.sin(ang) * vel
            vida = random.uniform(0.15, 0.35)
            tam = random.choice([4, 6, 8])
            self.particulas.append(Particula(x, y, vx, vy, color, vida, tam))

    def crear_explosion(self, x, y, grande=False):
        """Explosión pixel art de 16-bit: blanco -> amarillo -> naranja -> humo."""
        colores = [
            (255, 255, 255),  # Destello blanco central
            (255, 210, 63),   # Amarillo fuego
            (255, 159, 28),   # Naranja propulsión
            (230, 57, 70),    # Rojo fuego
            (90, 90, 90)      # Humo gris
        ]
        cant = 45 if grande else 25
        for _ in range(cant):
            ang = random.uniform(0, 2 * math.pi)
            vel = random.uniform(2.0, 10.0 if grande else 6.0)
            col = random.choice(colores)
            vida = random.uniform(0.3, 0.7)
            tam = random.choice([6, 8, 10 if grande else 8])
            self.particulas.append(Particula(x, y, math.cos(ang) * vel, math.sin(ang) * vel, col, vida, tam, 0.94))

    def crear_particulas_curacion_solar(self, rect_superman):
        """Partículas doradas que ascienden hacia Superman cuando se recarga en el sol."""
        for _ in range(2):
            px = random.randint(rect_superman.left, rect_superman.right)
            py = random.randint(rect_superman.top + 20, rect_superman.bottom)
            vy = random.uniform(-2.5, -4.5)
            vx = random.uniform(-0.5, 0.5)
            vida = random.uniform(0.3, 0.5)
            col = random.choice([(255, 244, 194), (255, 210, 63), (255, 255, 255)])
            self.particulas.append(Particula(px, py, vx, vy, col, vida, tamano=5, desaceleracion=0.99))

    def agregar_texto(self, x, y, texto, color=(255, 255, 255)):
        self.textos.append(TextoFlotante(x, y, texto, color))

    def actualizar(self, dt):
        if self.tiempo_sacudida > 0:
            self.tiempo_sacudida -= dt
            if self.tiempo_sacudida <= 0:
                self.fuerza_sacudida = 0.0

        self.particulas = [p for p in self.particulas if p.actualizar(dt)]
        self.textos = [t for t in self.textos if t.actualizar(dt)]

    def dibujar(self, superficie):
        for p in self.particulas:
            p.dibujar(superficie)
        if self.fuente_retro:
            for t in self.textos:
                t.dibujar(superficie, self.fuente_retro)
