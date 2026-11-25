"""
enemigos.py — Enemigos de LexCorp: Rexbots (LexBot1, LexBot10, LexBot20) y Misiles.
Implementa patrones de movimiento, disparo de láseres verdes y de sol rojo,
y la mecánica del brazo extensible con puño para LexBot20 en motocicleta.
"""

import os
import math
import random
import pygame
import config

class LaserEnemigo:
    def __init__(self, x, y, es_sol_rojo=False):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = -config.VELOCIDAD_LASER_ENEMIGO
        self.es_sol_rojo = es_sol_rojo
        self.radio = 7
        self.danio = 8 if es_sol_rojo else 5
        self.rect = pygame.Rect(int(self.x - self.radio), int(self.y - self.radio), self.radio * 2, self.radio * 2)
        self.activo = True

    def actualizar(self, dt):
        self.x += self.vel_x * (dt * 60)
        self.rect.x = int(self.x - self.radio)
        self.rect.y = int(self.y - self.radio)
        if self.x < -20:
            self.activo = False

    def dibujar(self, superficie):
        halo_color = config.COLOR_LASER_SOL_ROJO_HALO if self.es_sol_rojo else config.COLOR_LASER_KRIPTONITA_HALO
        # Núcleo blanco con halo de color
        pygame.draw.circle(superficie, halo_color, (int(self.x), int(self.y)), self.radio + 3)
        pygame.draw.circle(superficie, (255, 255, 255), (int(self.x), int(self.y)), self.radio - 2)


class Misil:
    """Misil teledirigido/recto de LexCorp. Se puede destruir o esquivar."""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vida = config.MISIL_VIDA
        self.vel_x = -config.MISIL_VELOCIDAD
        self.danio = config.MISIL_DANIO_CHOQUE
        self.ancho = config.MISIL_ANCHO
        self.sprites = []
        self.cargar_sprites()
        self.alto = self.sprites[0].get_height() if self.sprites else 21
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        self.activo = True
        self.frame_idx = 0.0

    def cargar_sprites(self):
        for i in range(3):
            p = os.path.join(config.DIR_SPRITES, f"misil_idle_{i}.png")
            if os.path.exists(p):
                self.sprites.append(pygame.image.load(p).convert_alpha())

    def recibir_danio(self, cantidad):
        self.vida -= cantidad
        if self.vida <= 0:
            self.activo = False
            return True
        return False

    def actualizar(self, dt):
        self.x += self.vel_x * (dt * 60)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        self.frame_idx = (self.frame_idx + 12.0 * dt) % len(self.sprites) if self.sprites else 0
        if self.x < -self.ancho - 50:
            self.activo = False  # Superado sin daño

    def dibujar(self, superficie):
        if self.sprites:
            idx = int(self.frame_idx) % len(self.sprites)
            superficie.blit(self.sprites[idx], (int(self.x), int(self.y)))


class LexBot1:
    """Rexbot nivel 1: Débil, cae de 1 solo disparo de láser."""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.y_base = float(y)
        self.vida = config.LEXBOT1_VIDA
        self.vel_x = -config.LEXBOT1_VELOCIDAD
        self.danio_choque = config.LEXBOT1_DANIO_CHOQUE
        self.ancho = config.LEXBOT1_ANCHO
        self.sprites_idle = []
        self.sprite_hurt = None
        self.cargar_sprites()
        self.alto = self.sprites_idle[0].get_height() if self.sprites_idle else 50
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        self.activo = True
        
        self.cooldown_disparo = random.uniform(1.0, config.LEXBOT1_CADENCIA)
        self.tiempo_hurt = 0.0
        self.tiempo_flotacion = random.uniform(0, math.pi * 2)

    def cargar_sprites(self):
        for i in range(2):
            p = os.path.join(config.DIR_SPRITES, f"lexbot1_idle_{i}.png")
            if os.path.exists(p):
                self.sprites_idle.append(pygame.image.load(p).convert_alpha())
        p_hurt = os.path.join(config.DIR_SPRITES, "lexbot1_hurt.png")
        if os.path.exists(p_hurt):
            self.sprite_hurt = pygame.image.load(p_hurt).convert_alpha()

    def recibir_danio(self, cantidad):
        self.vida -= cantidad
        self.tiempo_hurt = 0.12
        if self.vida <= 0:
            self.activo = False
            return True
        return False

    def empujar(self, distancia):
        self.x = min(config.ANCHO_PANTALLA - self.ancho, self.x + distancia)

    def actualizar(self, dt, target_superman, laseres_enemigos, sonido):
        self.tiempo_flotacion += dt * 3.0
        # Flotar suavemente arriba y abajo
        self.y = self.y_base + math.sin(self.tiempo_flotacion) * 25.0
        
        # Avanzar hasta el tercio derecho o quedarse flotando en pantalla
        if self.x > 820:
            self.x += self.vel_x * (dt * 60)
        else:
            # Oscilación suave de avance y retroceso
            self.x += math.cos(self.tiempo_flotacion * 0.5) * 0.5
            
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        if self.tiempo_hurt > 0:
            self.tiempo_hurt -= dt
            
        # Cadencia de disparo
        self.cooldown_disparo -= dt
        if self.cooldown_disparo <= 0:
            es_rojo = random.random() < 0.35
            laseres_enemigos.append(LaserEnemigo(self.x, self.y + self.alto * 0.5, es_rojo))
            sonido.reproducir_sfx("enemy_laser")
            self.cooldown_disparo = config.LEXBOT1_CADENCIA + random.uniform(-0.5, 0.5)

    def dibujar(self, superficie):
        if self.tiempo_hurt > 0 and self.sprite_hurt:
            superficie.blit(self.sprite_hurt, (int(self.x), int(self.y)))
        elif self.sprites_idle:
            idx = int(self.tiempo_flotacion * 4) % len(self.sprites_idle)
            superficie.blit(self.sprites_idle[idx], (int(self.x), int(self.y)))


class LexBot10:
    """Rexbot nivel 10: Medio, más resistente (3 láseres), rápido y ágil."""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.y_base = float(y)
        self.vida = config.LEXBOT10_VIDA
        self.vel_x = -config.LEXBOT10_VELOCIDAD
        self.danio_choque = config.LEXBOT10_DANIO_CHOQUE
        self.ancho = config.LEXBOT10_ANCHO
        self.sprites_idle = []
        self.sprite_hurt = None
        self.cargar_sprites()
        self.alto = self.sprites_idle[0].get_height() if self.sprites_idle else 101
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        self.activo = True
        
        self.cooldown_disparo = random.uniform(0.8, config.LEXBOT10_CADENCIA)
        self.tiempo_hurt = 0.0
        self.tiempo_flotacion = random.uniform(0, math.pi * 2)
        self.cambio_altura_timer = random.uniform(1.5, 3.0)

    def cargar_sprites(self):
        for i in range(2):
            p = os.path.join(config.DIR_SPRITES, f"lexbot10_idle_{i}.png")
            if os.path.exists(p):
                self.sprites_idle.append(pygame.image.load(p).convert_alpha())
        p_hurt = os.path.join(config.DIR_SPRITES, "lexbot10_hurt.png")
        if os.path.exists(p_hurt):
            self.sprite_hurt = pygame.image.load(p_hurt).convert_alpha()

    def recibir_danio(self, cantidad):
        self.vida -= cantidad
        self.tiempo_hurt = 0.12
        if self.vida <= 0:
            self.activo = False
            return True
        return False

    def empujar(self, distancia):
        self.x = min(config.ANCHO_PANTALLA - self.ancho, self.x + distancia)

    def actualizar(self, dt, target_superman, laseres_enemigos, sonido):
        self.tiempo_flotacion += dt * 4.0
        
        # Cambio periódico de altura objetivo
        self.cambio_altura_timer -= dt
        if self.cambio_altura_timer <= 0:
            self.y_base = random.randint(120, config.ALTO_PANTALLA - self.alto - 100)
            self.cambio_altura_timer = random.uniform(2.0, 4.0)
            
        # Seguir gradualmente la altura objetivo
        self.y += (self.y_base - self.y) * 0.05
        
        # Posicionamiento en pantalla
        if self.x > 750:
            self.x += self.vel_x * (dt * 60)
        else:
            self.x += math.sin(self.tiempo_flotacion * 0.8) * 1.2
            
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        if self.tiempo_hurt > 0:
            self.tiempo_hurt -= dt
            
        # Disparo con ráfagas
        self.cooldown_disparo -= dt
        if self.cooldown_disparo <= 0:
            es_rojo = random.random() < 0.5
            laseres_enemigos.append(LaserEnemigo(self.x, self.y + 25, es_rojo))
            laseres_enemigos.append(LaserEnemigo(self.x, self.y + self.alto - 25, es_rojo))
            sonido.reproducir_sfx("enemy_laser")
            self.cooldown_disparo = config.LEXBOT10_CADENCIA + random.uniform(-0.3, 0.4)

    def dibujar(self, superficie):
        if self.tiempo_hurt > 0 and self.sprite_hurt:
            superficie.blit(self.sprite_hurt, (int(self.x), int(self.y)))
        elif self.sprites_idle:
            idx = int(self.tiempo_flotacion * 5) % len(self.sprites_idle)
            superficie.blit(self.sprites_idle[idx], (int(self.x), int(self.y)))


class LexBot20:
    """Rexbot nivel 20: Robot en motocicleta con brazo mecánico extensible (puñetazo potente)."""
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vida = config.LEXBOT20_VIDA
        self.vel_x = -config.LEXBOT20_VELOCIDAD
        self.danio_choque = config.LEXBOT20_DANIO_CHOQUE
        self.ancho = config.LEXBOT20_ANCHO
        self.sprites_idle = []
        self.sprite_fist = None
        self.sprite_hurt = None
        self.cargar_sprites()
        self.alto = self.sprites_idle[0].get_height() if self.sprites_idle else 85
        self.rect = pygame.Rect(int(self.x), int(self.y), self.ancho, self.alto)
        self.activo = True
        
        self.cooldown_disparo = 1.2
        self.cooldown_punio = config.LEXBOT20_CADENCIA_PUNIO
        self.tiempo_hurt = 0.0
        self.tiempo_anim = 0.0
        
        # Mecánica de brazo extensible
        self.estirando_brazo = False
        self.alcance_actual_brazo = 0.0
        self.alcance_max_brazo = 380.0
        self.velocidad_brazo = 650.0
        self.brazo_regresando = False
        self.rect_punio = None

    def cargar_sprites(self):
        for i in range(2):
            p = os.path.join(config.DIR_SPRITES, f"lexbot20_idle_{i}.png")
            if os.path.exists(p):
                self.sprites_idle.append(pygame.image.load(p).convert_alpha())
        p_fist = os.path.join(config.DIR_SPRITES, "lexbot20_fist.png")
        if os.path.exists(p_fist):
            self.sprite_fist = pygame.image.load(p_fist).convert_alpha()
        p_hurt = os.path.join(config.DIR_SPRITES, "lexbot20_hurt.png")
        if os.path.exists(p_hurt):
            self.sprite_hurt = pygame.image.load(p_hurt).convert_alpha()

    def recibir_danio(self, cantidad):
        self.vida -= cantidad
        self.tiempo_hurt = 0.12
        if self.vida <= 0:
            self.activo = False
            return True
        return False

    def empujar(self, distancia):
        self.x = min(config.ANCHO_PANTALLA - self.ancho, self.x + distancia)

    def actualizar(self, dt, target_superman, laseres_enemigos, sonido):
        self.tiempo_anim += dt * 6.0
        
        # Posición de la motocicleta
        if self.x > 680:
            self.x += self.vel_x * (dt * 60)
        else:
            # Acomodarse verticalmente hacia la altura de Superman para apuntar el puñetazo
            diff_y = target_superman.rect.centery - (self.y + self.alto * 0.5)
            self.y += diff_y * 0.03
            
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        if self.tiempo_hurt > 0:
            self.tiempo_hurt -= dt
            
        # 1. Disparo de láser de regreso
        self.cooldown_disparo -= dt
        if self.cooldown_disparo <= 0 and not self.estirando_brazo:
            es_rojo = True  # Láseres de sol rojo potentes
            laseres_enemigos.append(LaserEnemigo(self.x, self.y + 20, es_rojo))
            laseres_enemigos.append(LaserEnemigo(self.x, self.y + self.alto - 15, es_rojo))
            sonido.reproducir_sfx("enemy_laser")
            self.cooldown_disparo = config.LEXBOT20_CADENCIA
            
        # 2. Mecánica de lanzar y estirar puño mecánico
        self.cooldown_punio -= dt
        if self.cooldown_punio <= 0 and not self.estirando_brazo:
            self.estirando_brazo = True
            self.brazo_regresando = False
            self.alcance_actual_brazo = 0.0
            sonido.reproducir_sfx("rocket_punch")
            
        if self.estirando_brazo:
            if not self.brazo_regresando:
                self.alcance_actual_brazo += self.velocidad_brazo * dt
                if self.alcance_actual_brazo >= self.alcance_max_brazo:
                    self.brazo_regresando = True
            else:
                self.alcance_actual_brazo -= self.velocidad_brazo * dt * 1.2
                if self.alcance_actual_brazo <= 0:
                    self.alcance_actual_brazo = 0.0
                    self.estirando_brazo = False
                    self.cooldown_punio = config.LEXBOT20_CADENCIA_PUNIO
                    self.rect_punio = None

            # Actualizar caja de colisión del puño
            if self.estirando_brazo and self.alcance_actual_brazo > 10:
                punio_x = int(self.x - self.alcance_actual_brazo)
                punio_y = int(self.y + self.alto * 0.35)
                self.rect_punio = pygame.Rect(punio_x, punio_y, 36, 26)
            else:
                self.rect_punio = None

    def dibujar(self, superficie):
        # Dibujar brazo mecánico extensible si está activo
        if self.estirando_brazo and self.alcance_actual_brazo > 5:
            origen_x = int(self.x + 10)
            origen_y = int(self.y + self.alto * 0.45)
            punio_x = int(self.x - self.alcance_actual_brazo)
            
            # Segmentos del pistón hidráulico
            puntos = 10
            for i in range(puntos):
                sx1 = origen_x - int((self.alcance_actual_brazo / puntos) * i)
                sx2 = origen_x - int((self.alcance_actual_brazo / puntos) * (i + 1))
                pygame.draw.line(superficie, config.COLOR_GRIS_METAL, (sx1, origen_y), (sx2, origen_y), 6)
                pygame.draw.circle(superficie, config.COLOR_MORADO_BRILLANTE, (sx1, origen_y), 4)
                
            # Sprite del puño en la punta
            if self.sprite_fist:
                superficie.blit(self.sprite_fist, (punio_x, origen_y - 13))

        # Dibujar cuerpo de la motocicleta y robot
        if self.tiempo_hurt > 0 and self.sprite_hurt:
            superficie.blit(self.sprite_hurt, (int(self.x), int(self.y)))
        elif self.sprites_idle:
            idx = int(self.tiempo_anim) % len(self.sprites_idle)
            superficie.blit(self.sprites_idle[idx], (int(self.x), int(self.y)))
