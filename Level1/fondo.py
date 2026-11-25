"""
fondo.py — Fondo dinámico en capas (Parallax) de la ciudad de Metrópolis en pixel art.
Incluye el sol radiante de día, nubes en movimiento, edificios dorados y art deco,
y la zona de recarga solar de Superman.
"""

import os
import math
import pygame
import config

class FondoMetropolis:
    def __init__(self):
        self.cielo = None
        self.lejanos = None
        self.edificios = None
        self.nubes = []
        
        self.cargar_fondos()
        
        # Desplazamientos parallax
        self.pos_lejanos = 0.0
        self.pos_edificios = 0.0
        self.vel_lejanos = 0.8
        self.vel_edificios = 2.4
        
        # Estado de la zona solar
        self.zona_sol_activa = False
        self.tiempo_zona_sol = 0.0
        self.temporizador_sol = 0.0
        self.anim_pulso = 0.0
        
        # Generar nubes pixeladas flotantes
        self.crear_nubes()

    def cargar_fondos(self):
        ruta_cielo = os.path.join(config.DIR_SPRITES, "fondo_cielo_sol.png")
        ruta_lejanos = os.path.join(config.DIR_SPRITES, "fondo_lejanos.png")
        ruta_edificios = os.path.join(config.DIR_SPRITES, "fondo_edificios.png")
        
        if os.path.exists(ruta_cielo):
            self.cielo = pygame.image.load(ruta_cielo).convert_alpha()
        else:
            self.cielo = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
            self.cielo.fill(config.COLOR_CIELO_TOP)
            
        if os.path.exists(ruta_lejanos):
            self.lejanos = pygame.image.load(ruta_lejanos).convert_alpha()
        else:
            self.lejanos = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA), pygame.SRCALPHA)
            
        if os.path.exists(ruta_edificios):
            self.edificios = pygame.image.load(ruta_edificios).convert_alpha()
        else:
            self.edificios = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA), pygame.SRCALPHA)

    def crear_nubes(self):
        """Crea varias nubes estilo pixel art a distintas alturas."""
        self.nubes = [
            {"x": 100.0, "y": 80, "vel": 0.5, "ancho": 110, "alto": 35},
            {"x": 480.0, "y": 140, "vel": 0.7, "ancho": 140, "alto": 45},
            {"x": 920.0, "y": 60, "vel": 0.4, "ancho": 90, "alto": 30},
            {"x": 1280.0, "y": 110, "vel": 0.6, "ancho": 130, "alto": 40}
        ]

    def activar_zona_sol(self, permanente=False):
        """Activa la zona de recarga solar."""
        self.zona_sol_activa = True
        self.sol_permanente = permanente
        self.temporizador_sol = config.TIEMPO_ZONA_SOL_OLEADA

    def desactivar_zona_sol(self):
        if not getattr(self, "sol_permanente", False):
            self.zona_sol_activa = False

    def esta_en_zona_sol(self, rect_superman):
        """Comprueba si Superman está en la parte superior recibiendo luz solar directa."""
        if not self.zona_sol_activa:
            return False
        # Superman se acerca al sol en la parte superior de la pantalla
        return rect_superman.top <= 160 and rect_superman.right >= 400

    def actualizar(self, dt):
        self.anim_pulso += dt * 3.0
        
        # Mover capas de edificios hacia la izquierda
        self.pos_lejanos = (self.pos_lejanos + self.vel_lejanos) % config.ANCHO_PANTALLA
        self.pos_edificios = (self.pos_edificios + self.vel_edificios) % config.ANCHO_PANTALLA
        
        # Mover nubes
        for n in self.nubes:
            n["x"] -= n["vel"]
            if n["x"] + n["ancho"] < 0:
                n["x"] = config.ANCHO_PANTALLA + 20
                
        # Temporizador de zona solar temporal
        if self.zona_sol_activa and not getattr(self, "sol_permanente", False):
            self.temporizador_sol -= dt
            if self.temporizador_sol <= 0:
                self.zona_sol_activa = False

    def dibujar(self, superficie):
        # 1. Cielo y Sol
        if self.cielo:
            superficie.blit(self.cielo, (0, 0))
            
        # 2. Resplandor pulsante del Sol si la zona está activa
        if self.zona_sol_activa:
            sol_centro_x, sol_centro_y = 850, 90
            pulso = 10 + int(math.sin(self.anim_pulso) * 8)
            surf_halo = pygame.Surface((340, 340), pygame.SRCALPHA)
            pygame.draw.circle(surf_halo, (255, 230, 128, 55 + pulso * 2), (170, 170), 120 + pulso)
            pygame.draw.circle(surf_halo, (255, 244, 194, 90), (170, 170), 80 + pulso // 2)
            superficie.blit(surf_halo, (sol_centro_x - 170, sol_centro_y - 170), special_flags=pygame.BLEND_RGBA_ADD)
            
            # Indicador visual pixel art: rayos de sol descendiendo
            for offset_x in range(450, 1200, 140):
                line_surf = pygame.Surface((4, 180), pygame.SRCALPHA)
                line_surf.fill((255, 244, 194, 40 + int(math.sin(self.anim_pulso + offset_x) * 20)))
                superficie.blit(line_surf, (offset_x, 0))
                
        # 3. Nubes pixeladas
        for n in self.nubes:
            nx, ny = int(n["x"]), int(n["y"])
            nw, nh = n["ancho"], n["alto"]
            # Estructura pixelada de nube
            pygame.draw.rect(superficie, (255, 255, 255, 210), (nx, ny + 8, nw, nh - 8), border_radius=6)
            pygame.draw.rect(superficie, (255, 255, 255, 230), (nx + 15, ny, nw - 30, nh), border_radius=8)
            pygame.draw.rect(superficie, (240, 245, 255, 250), (nx + 30, ny - 6, nw - 60, nh - 6), border_radius=10)

        # 4. Edificios lejanos con scroll infinito (seamless loop)
        if self.lejanos:
            x1 = -int(self.pos_lejanos)
            superficie.blit(self.lejanos, (x1, 0))
            superficie.blit(self.lejanos, (x1 + config.ANCHO_PANTALLA, 0))

        # 5. Edificios medios y cercanos con Daily Planet
        if self.edificios:
            x2 = -int(self.pos_edificios)
            superficie.blit(self.edificios, (x2, 0))
            superficie.blit(self.edificios, (x2 + config.ANCHO_PANTALLA, 0))
