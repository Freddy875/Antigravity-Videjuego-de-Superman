"""
jugador.py — Protagonista: Superman (vuelo, rayo láser, golpe y recarga solar).
Gestiona movimiento por teclado, animaciones de vuelo y ataques, proyectiles láser,
caja de golpe físico, vida e invulnerabilidad.
"""

import os
import math
import pygame
import config

class LaserSuperman:
    def __init__(self, x, y):
        self.x = float(x)
        self.y = float(y)
        self.vel_x = config.SUPERMAN_VELOCIDAD_LASER
        self.danio = config.SUPERMAN_DANIO_LASER
        self.longitud = 36
        self.alto = 6
        self.rect = pygame.Rect(int(self.x), int(self.y), self.longitud, self.alto)
        self.activo = True

    def actualizar(self, dt):
        self.x += self.vel_x * (dt * 60)
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        if self.x > config.ANCHO_PANTALLA:
            self.activo = False

    def dibujar(self, superficie):
        # Núcleo blanco y halo rojo
        halo_rect = pygame.Rect(self.rect.x - 2, self.rect.y - 2, self.longitud + 4, self.alto + 4)
        pygame.draw.rect(superficie, config.COLOR_LASER_SUPERMAN_HALO, halo_rect, border_radius=3)
        pygame.draw.rect(superficie, config.COLOR_LASER_SUPERMAN_NUCLEO, self.rect, border_radius=2)


class Superman:
    def __init__(self, x=150, y=320):
        self.x = float(x)
        self.y = float(y)
        self.vida = config.SUPERMAN_VIDA_MAX
        self.vida_max = config.SUPERMAN_VIDA_MAX
        
        # Sprites y animaciones
        self.sprites_idle = []
        self.sprite_laser = None
        self.sprite_punch = None
        self.sprite_hurt = None
        self.cargar_sprites()
        
        # Dimensiones y caja de colisión
        self.ancho = config.SUPERMAN_ANCHO
        self.alto = self.sprites_idle[0].get_height() if self.sprites_idle else 157
        self.rect = pygame.Rect(int(self.x), int(self.y), int(self.ancho * 0.75), int(self.alto * 0.8))
        
        # Estados y temporizadores
        self.tiempo_invulnerable = 0.0
        self.cooldown_laser = 0.0
        self.cooldown_golpe = 0.0
        self.tiempo_anim_punch = 0.0
        self.tiempo_anim_laser = 0.0
        self.tiempo_recarga_sonido = 0.0
        
        # Animación de vuelo
        self.frame_idx = 0.0
        self.anim_vel = 6.0
        
        # Colección de proyectiles activos
        self.laseres = []
        
        # Caja de golpe activa durante la animación de golpe
        self.rect_golpe = None
        self.golpe_activo = False

    def cargar_sprites(self):
        for i in range(4):
            p = os.path.join(config.DIR_SPRITES, f"superman_idle_{i}.png")
            if os.path.exists(p):
                self.sprites_idle.append(pygame.image.load(p).convert_alpha())
                
        p_laser = os.path.join(config.DIR_SPRITES, "superman_laser.png")
        if os.path.exists(p_laser):
            self.sprite_laser = pygame.image.load(p_laser).convert_alpha()
            
        p_punch = os.path.join(config.DIR_SPRITES, "superman_punch.png")
        if os.path.exists(p_punch):
            self.sprite_punch = pygame.image.load(p_punch).convert_alpha()
            
        p_hurt = os.path.join(config.DIR_SPRITES, "superman_hurt.png")
        if os.path.exists(p_hurt):
            self.sprite_hurt = pygame.image.load(p_hurt).convert_alpha()

    def procesar_entrada(self, teclas, jefe_activo, sistema_sonido):
        # 1. Movimiento en 4 direcciones
        dx, dy = 0.0, 0.0
        if any(teclas[k] for k in config.TECLAS_ARRIBA if k < len(teclas)):
            dy -= config.SUPERMAN_VELOCIDAD
        if any(teclas[k] for k in config.TECLAS_ABAJO if k < len(teclas)):
            dy += config.SUPERMAN_VELOCIDAD
        if any(teclas[k] for k in config.TECLAS_IZQUIERDA if k < len(teclas)):
            dx -= config.SUPERMAN_VELOCIDAD
        if any(teclas[k] for k in config.TECLAS_DERECHA if k < len(teclas)):
            dx += config.SUPERMAN_VELOCIDAD
            
        # Normalizar si se mueve en diagonal
        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071
            
        self.x += dx
        self.y += dy
        
        # Restricción a los bordes de la pantalla
        self.x = max(10, min(config.ANCHO_PANTALLA - self.ancho - 10, self.x))
        self.y = max(10, min(config.ALTO_PANTALLA - self.alto - 10, self.y))
        
        # Sincronizar rect de colisión (centrado en el cuerpo)
        self.rect.x = int(self.x + 15)
        self.rect.y = int(self.y + 10)

        # 2. Habilidad: Disparo láser con tecla Espacio
        # En el jefe final no tiene tiempo de recarga (disparo continuo o rapidísimo)
        cd_max = config.SUPERMAN_COOLDOWN_LASER_JEFE if jefe_activo else config.SUPERMAN_COOLDOWN_LASER
        if any(teclas[k] for k in config.TECLAS_LASER if k < len(teclas)):
            if self.cooldown_laser <= 0:
                self.disparar_laser(sistema_sonido)
                self.cooldown_laser = cd_max

        # 3. Habilidad: Golpe cuerpo a cuerpo con tecla X
        if any(teclas[k] for k in config.TECLAS_GOLPE if k < len(teclas)):
            if self.cooldown_golpe <= 0:
                self.ejecutar_golpe(sistema_sonido)
                self.cooldown_golpe = config.SUPERMAN_COOLDOWN_GOLPE

    def disparar_laser(self, sistema_sonido):
        """Lanza dos rayos láser desde los ojos de Superman."""
        ojo_x = self.x + self.ancho * 0.75
        ojo_y1 = self.y + self.alto * 0.22
        ojo_y2 = self.y + self.alto * 0.26
        
        self.laseres.append(LaserSuperman(ojo_x, ojo_y1))
        self.laseres.append(LaserSuperman(ojo_x, ojo_y2))
        self.tiempo_anim_laser = 0.18
        sistema_sonido.reproducir_sfx("laser")

    def ejecutar_golpe(self, sistema_sonido):
        """Superman estira el brazo con fuerza destructiva hacia adelante."""
        self.tiempo_anim_punch = 0.24
        self.golpe_activo = True
        
        # Caja de golpe frente a Superman
        alcance = config.SUPERMAN_ALCANCE_GOLPE
        self.rect_golpe = pygame.Rect(
            int(self.x + self.ancho * 0.7),
            int(self.y + self.alto * 0.2),
            alcance,
            int(self.alto * 0.6)
        )
        sistema_sonido.reproducir_sfx("golpe")

    def recibir_danio(self, cantidad, efectos, sonido):
        """Aplica daño y activa el parpadeo de invulnerabilidad de 1 segundo."""
        if self.tiempo_invulnerable > 0:
            return False
            
        self.vida = max(0, self.vida - cantidad)
        self.tiempo_invulnerable = config.SUPERMAN_TIEMPO_INVULNERABLE
        efectos.sacudir_pantalla(duracion=0.25, fuerza=4.0)
        efectos.crear_chispas_impacto(self.rect.centerx, self.rect.centery, color=config.COLOR_ROJO_LUZ, cantidad=14)
        efectos.agregar_texto(self.rect.centerx, self.rect.top - 10, f"-{cantidad} HP", config.COLOR_VIDA_BAJA)
        return True

    def recargar_energia_solar(self, dt, efectos, sonido):
        """Recupera energía cuando Superman está expuesto a la radiación solar."""
        if self.vida < self.vida_max:
            incremento = config.SUPERMAN_TASA_CURACION_SOL * dt
            self.vida = min(self.vida_max, self.vida + incremento)
            
            # Efectos visuales y de sonido de curación solar
            efectos.crear_particulas_curacion_solar(self.rect)
            self.tiempo_recarga_sonido -= dt
            if self.tiempo_recarga_sonido <= 0:
                sonido.reproducir_sfx("sun_recharge")
                self.tiempo_recarga_sonido = 0.4
                efectos.agregar_texto(self.rect.centerx, self.rect.top - 12, "+SOLAR", config.COLOR_AMARILLO_EMBLEMA)

    def actualizar(self, dt):
        # Actualizar temporizadores
        if self.tiempo_invulnerable > 0:
            self.tiempo_invulnerable -= dt
        if self.cooldown_laser > 0:
            self.cooldown_laser -= dt
        if self.cooldown_golpe > 0:
            self.cooldown_golpe -= dt
        if self.tiempo_anim_laser > 0:
            self.tiempo_anim_laser -= dt
            
        # Desactivar golpe al terminar su tiempo de animación
        if self.tiempo_anim_punch > 0:
            self.tiempo_anim_punch -= dt
            if self.tiempo_anim_punch <= 0:
                self.golpe_activo = False
                self.rect_golpe = None
                
        # Animación de vuelo continuo
        self.frame_idx = (self.frame_idx + self.anim_vel * dt) % len(self.sprites_idle) if self.sprites_idle else 0
        
        # Actualizar proyectiles láser
        for l in self.laseres:
            l.actualizar(dt)
        self.laseres = [l for l in self.laseres if l.activo]

    def dibujar(self, superficie):
        # Efecto de parpadeo si está invulnerable
        if self.tiempo_invulnerable > 0:
            if int(self.tiempo_invulnerable * 16) % 2 == 0:
                # Ocultar temporalmente para dar efecto de parpadeo
                pass
            elif self.sprite_hurt:
                superficie.blit(self.sprite_hurt, (int(self.x), int(self.y)))
                # Dibujar láseres aunque parpadee
                for l in self.laseres:
                    l.dibujar(superficie)
                return

        # Selección de sprite según acción activa
        if self.tiempo_anim_punch > 0 and self.sprite_punch:
            superficie.blit(self.sprite_punch, (int(self.x), int(self.y)))
        elif self.tiempo_anim_laser > 0 and self.sprite_laser:
            superficie.blit(self.sprite_laser, (int(self.x), int(self.y)))
        elif self.sprites_idle:
            idx = int(self.frame_idx) % len(self.sprites_idle)
            superficie.blit(self.sprites_idle[idx], (int(self.x), int(self.y)))
            
        # Dibujar láseres de Superman
        for l in self.laseres:
            l.dibujar(superficie)
