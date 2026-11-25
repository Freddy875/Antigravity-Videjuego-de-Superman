"""
config.py — Constantes y configuración global del videojuego Superman: Nivel 1.
Define dimensiones, colores (extraídos de GUIA_ESTILO.md), parámetros de jugabilidad,
controles y temporizadores de oleadas.
"""

import os
import pygame

# ==============================================================================
# 1. DIRECTORIOS Y RUTAS
# ==============================================================================
DIR_BASE = os.path.dirname(os.path.abspath(__file__))
DIR_ASSETS = os.path.join(DIR_BASE, "assets")
DIR_SPRITES = os.path.join(DIR_ASSETS, "sprites")
DIR_AUDIO = os.path.join(DIR_ASSETS, "audio")
DIR_SFX = os.path.join(DIR_ASSETS, "sfx")

# ==============================================================================
# 2. PANTALLA Y RENDIMIENTO
# ==============================================================================
ANCHO_PANTALLA = 1280
ALTO_PANTALLA = 720
FPS = 60
TITULO_JUEGO = "SUPERMAN: Nivel 1 — Metrópolis"

# ==============================================================================
# 3. PALETA DE COLORES (GUIA_ESTILO.md)
# ==============================================================================
# Héroe (Superman)
COLOR_ROJO_CAPA = (165, 14, 13)
COLOR_ROJO_LUZ = (199, 30, 23)
COLOR_ROJO_SOMBRA = (114, 7, 7)
COLOR_AZUL_TRAJE = (49, 88, 146)
COLOR_AZUL_LUZ = (94, 144, 191)
COLOR_AZUL_SOMBRA = (2, 41, 103)
COLOR_AMARILLO_EMBLEMA = (245, 197, 24)
COLOR_PIEL = (239, 181, 118)

# Enemigos (LexBots de LexCorp)
COLOR_VERDE_BRILLANTE = (56, 215, 23)
COLOR_VERDE_LIMA = (128, 204, 53)
COLOR_VERDE_SOMBRA = (46, 107, 27)
COLOR_MORADO = (90, 41, 93)
COLOR_MORADO_BRILLANTE = (125, 31, 115)
COLOR_MORADO_SOMBRA = (42, 18, 55)
COLOR_GRIS_METAL = (66, 74, 78)
COLOR_GRIS_CLARO = (122, 107, 113)
COLOR_OJOS_ROJOS = (211, 75, 84)

# Proyectiles y Efectos
COLOR_LASER_SUPERMAN_NUCLEO = (255, 255, 255)
COLOR_LASER_SUPERMAN_HALO = (255, 42, 42)
COLOR_LASER_KRIPTONITA_NUCLEO = (255, 255, 255)
COLOR_LASER_KRIPTONITA_HALO = (57, 255, 20)
COLOR_LASER_SOL_ROJO_NUCLEO = (255, 255, 255)
COLOR_LASER_SOL_ROJO_HALO = (194, 24, 91)     # Rojo-magenta distintivo

# Zona Solar ☀️
COLOR_SOL_CIRCULO = (255, 244, 194)
COLOR_SOL_RAYOS = (255, 230, 128)
COLOR_SOL_DESTELLO = (255, 210, 63)

# Ciudad de Metrópolis
COLOR_CIELO_TOP = (1, 119, 250)
COLOR_CIELO_BOT = (130, 183, 232)
COLOR_EDIFICIOS_DORADOS = (221, 174, 93)
COLOR_VENTANAS_CREMA = (242, 230, 179)
COLOR_EDIFICIOS_LEJANOS = (75, 97, 150)

# HUD e Interfaz
COLOR_TEXTO_BLANCO = (255, 255, 255)
COLOR_TEXTO_SOMBRA = (0, 0, 0)
COLOR_MARCO_HUD = (27, 24, 37)
COLOR_VIDA_ALTA = (61, 220, 90)     # 100 - 51
COLOR_VIDA_MEDIA = (255, 201, 60)   # 50 - 26
COLOR_VIDA_BAJA = (230, 57, 70)     # 25 - 0

# ==============================================================================
# 4. PARÁMETROS DEL HÉROE (SUPERMAN)
# ==============================================================================
SUPERMAN_VIDA_MAX = 100
SUPERMAN_VELOCIDAD = 7.0
SUPERMAN_ANCHO = 120

# Habilidades
SUPERMAN_COOLDOWN_LASER = 0.25      # Segundos entre disparos normales
SUPERMAN_COOLDOWN_LASER_JEFE = 0.08 # Disparo rápido sin recarga contra el jefe
SUPERMAN_DANIO_LASER = 2
SUPERMAN_VELOCIDAD_LASER = 22.0

SUPERMAN_COOLDOWN_GOLPE = 0.35      # Segundos entre golpes cuerpo a cuerpo
SUPERMAN_DANIO_GOLPE = 1
SUPERMAN_ALCANCE_GOLPE = 90         # Píxeles de alcance frente a Superman
SUPERMAN_EMPUJE_GOLPE = 60          # Píxeles de empuje al enemigo

SUPERMAN_TIEMPO_INVULNERABLE = 1.0  # Segundos tras recibir daño
SUPERMAN_TASA_CURACION_SOL = 15.0   # Puntos de vida recuperados por segundo en el sol

# ==============================================================================
# 5. PARÁMETROS DE ENEMIGOS
# ==============================================================================
# Misil
MISIL_VIDA = 1
MISIL_VELOCIDAD = 9.0
MISIL_DANIO_CHOQUE = 10
MISIL_ANCHO = 60

# LexBot1 (Rexbot débil)
LEXBOT1_VIDA = 2
LEXBOT1_VELOCIDAD = 2.5
LEXBOT1_DANIO_LASER = 5
LEXBOT1_DANIO_CHOQUE = 5
LEXBOT1_CADENCIA = 2.8              # Disparo cada ~3 s
LEXBOT1_ANCHO = 80

# LexBot10 (Rexbot medio)
LEXBOT10_VIDA = 6
LEXBOT10_VELOCIDAD = 3.8
LEXBOT10_DANIO_LASER = 8
LEXBOT10_DANIO_CHOQUE = 10
LEXBOT10_CADENCIA = 1.9             # Disparo cada ~2 s
LEXBOT10_ANCHO = 110

# LexBot20 (Rexbot pesado en moto)
LEXBOT20_VIDA = 12
LEXBOT20_VELOCIDAD = 4.2
LEXBOT20_DANIO_LASER = 12
LEXBOT20_DANIO_CHOQUE = 15
LEXBOT20_DANIO_PUNIO = 18
LEXBOT20_CADENCIA = 1.8
LEXBOT20_CADENCIA_PUNIO = 3.5       # Estira brazo mecánico cada 3.5 s
LEXBOT20_ANCHO = 150

# Láseres enemigos
VELOCIDAD_LASER_ENEMIGO = 11.0

# ==============================================================================
# 6. PARÁMETROS DEL JEFE FINAL (ROBOT GIGANTE)
# ==============================================================================
JEFE_VIDA_MAX = 70                  # Vida total (requiere muchos disparos)
JEFE_ALTO = 450
JEFE_DANIO_PUNIO = 20
JEFE_DANIO_MISIL = 12
JEFE_DANIO_RAYO = 25
JEFE_DANIO_CHOQUE = 20
JEFE_CADENCIA_ATAQUE = 2.6          # Tiempo entre mecánicas de ataque

# ==============================================================================
# 7. ZONA SOLAR ☀️
# ==============================================================================
# Zona de recarga solar en la parte superior (Y <= 150)
RECT_ZONA_SOL = pygame.Rect(400, 0, 750, 160)
TIEMPO_ZONA_SOL_OLEADA = 6.0        # Duración de la zona de sol entre oleadas

# ==============================================================================
# 8. CONTROLES (Mapeo a acciones)
# ==============================================================================
TECLAS_ARRIBA = [pygame.K_UP, pygame.K_w]
TECLAS_ABAJO = [pygame.K_DOWN, pygame.K_s]
TECLAS_IZQUIERDA = [pygame.K_LEFT, pygame.K_a]
TECLAS_DERECHA = [pygame.K_RIGHT, pygame.K_d]
TECLAS_LASER = [pygame.K_SPACE]
TECLAS_GOLPE = [pygame.K_x, pygame.K_j]
TECLAS_PAUSA = [pygame.K_p, pygame.K_ESCAPE]
TECLAS_CONFIRMAR = [pygame.K_RETURN, pygame.K_SPACE]
