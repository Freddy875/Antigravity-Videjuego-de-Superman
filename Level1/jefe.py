"""
jefe.py — Jefe Final: Robot Gigante de LexCorp (Final Boss).
Implementa 3 fases visuales y de daño, ataque de estirar puño gigante (Rocket Punch),
lluvia de misiles desde silos de hombro, y mega rayo láser continuo desde el núcleo.
"""

import os
import math
import random
import pygame
import config
from enemigos import Misil, LaserEnemigo

class MegaRayoBoss:
    """Rayo láser gigante horizontal que barre la pantalla."""
    def __init__(self, origen_x, origen_y, duracion=1.2, es_sol_rojo=False):
        self.origen_x = origen_x
        self.origen_y = origen_y
        self.duracion = duracion
        self.vida = duracion
        self.es_sol_rojo = es_sol_rojo
        self.grosor = 28
        self.rect = pygame.Rect(0, int(origen_y - self.grosor // 2), int(origen_x), self.grosor)
        self.activo = True

    def actualizar(self, dt):
        self.vida -= dt
        if self.vida <= 0:
            self.activo = False

    def dibujar(self, superficie):
        if not self.activo:
            return
        halo = config.COLOR_LASER_SOL_ROJO_HALO if self.es_sol_rojo else config.COLOR_LASER_KRIPTONITA_HALO
        # Halo exterior brillante
        pygame.draw.rect(superficie, halo, self.rect)
        # Núcleo blanco intenso
        core_rect = pygame.Rect(0, self.rect.y + 6, self.rect.width, self.rect.height - 12)
        pygame.draw.rect(superficie, (255, 255, 255), core_rect)


class FinalBoss:
    def __init__(self, x=820, y=140):
        self.x = float(x)
        self.y = float(y)
        self.vida_max = config.JEFE_VIDA_MAX
        self.vida = self.vida_max
        self.ancho = 340
        self.alto = config.JEFE_ALTO
        self.activo = True
        self.derrotado = False
        
        # Sprites por fase
        self.sprite_fase1 = None
        self.sprite_fase2 = None
        self.sprite_fase3 = None
        self.sprite_fist = None
        self.sprite_hurt = None
        self.cargar_sprites()
        
        self.rect = pygame.Rect(int(self.x + 30), int(self.y + 20), self.ancho - 50, self.alto - 40)
        
        # Fases (1, 2, 3)
        self.fase_actual = 1
        self.tiempo_hurt = 0.0
        self.anim_tiempo = 0.0
        
        # Ataques y temporizadores
        self.temporizador_ataque = 2.0
        self.tipo_ataque_activo = None  # 'punio', 'misiles', 'mega_rayo'
        
        # 1. Mecánica de estirar puño gigante (Rocket Punch)
        self.punio_estirando = False
        self.punio_regresando = False
        self.distancia_punio = 0.0
        self.distancia_max_punio = 780.0
        self.vel_punio = 750.0
        self.rect_punio = None
        self.punio_y = 0.0
        
        # 2. Mecánica de Mega Rayo
        self.cargando_rayo = False
        self.tiempo_carga_rayo = 0.0
        self.rayo_activo = None
        
        # 3. Misiles generados por el jefe
        self.misiles_pendientes = 0
        self.cooldown_misil_boss = 0.0

    def cargar_sprites(self):
        p1 = os.path.join(config.DIR_SPRITES, "boss_fase1.png")
        if os.path.exists(p1):
            self.sprite_fase1 = pygame.image.load(p1).convert_alpha()
            self.ancho = self.sprite_fase1.get_width()
            self.alto = self.sprite_fase1.get_height()
            
        p2 = os.path.join(config.DIR_SPRITES, "boss_fase2.png")
        if os.path.exists(p2):
            self.sprite_fase2 = pygame.image.load(p2).convert_alpha()
            
        p3 = os.path.join(config.DIR_SPRITES, "boss_fase3.png")
        if os.path.exists(p3):
            self.sprite_fase3 = pygame.image.load(p3).convert_alpha()
            
        pf = os.path.join(config.DIR_SPRITES, "boss_fist.png")
        if os.path.exists(pf):
            self.sprite_fist = pygame.image.load(pf).convert_alpha()
            
        ph = os.path.join(config.DIR_SPRITES, "boss_hurt.png")
        if os.path.exists(ph):
            self.sprite_hurt = pygame.image.load(ph).convert_alpha()

    def recibir_danio(self, cantidad, efectos):
        self.vida = max(0, self.vida - cantidad)
        self.tiempo_hurt = 0.08
        efectos.crear_chispas_impacto(self.x + 80, self.y + 180, color=(255, 230, 128), cantidad=6)
        
        # Transición de fases
        pct = self.vida / self.vida_max
        if pct <= 0.33 and self.fase_actual < 3:
            self.fase_actual = 3
            efectos.sacudir_pantalla(duracion=0.6, fuerza=10.0)
            efectos.crear_explosion(self.x + 100, self.y + 200, grande=True)
            efectos.agregar_texto(self.x - 40, self.y + 60, "¡ARMADURA DESTRUIDA!", config.COLOR_VIDA_BAJA)
        elif pct <= 0.66 and self.fase_actual < 2:
            self.fase_actual = 2
            efectos.sacudir_pantalla(duracion=0.4, fuerza=7.0)
            efectos.crear_explosion(self.x + 100, self.y + 160, grande=True)
            efectos.agregar_texto(self.x - 30, self.y + 60, "¡DAÑO CRÍTICO!", config.COLOR_AMARILLO_EMBLEMA)

        if self.vida <= 0:
            self.derrotado = True
            self.activo = False
            return True
        return False

    def actualizar(self, dt, target_superman, misiles_lista, laseres_enemigos, efectos, sonido):
        self.anim_tiempo += dt * 3.0
        # Flotación pesada del robot gigante
        self.y = 140 + math.sin(self.anim_tiempo) * 18.0
        self.rect.x = int(self.x + 30)
        self.rect.y = int(self.y + 20)
        
        if self.tiempo_hurt > 0:
            self.tiempo_hurt -= dt
            
        # Actualizar Mega Rayo activo si lo hay
        if self.rayo_activo:
            self.rayo_activo.actualizar(dt)
            if not self.rayo_activo.activo:
                self.rayo_activo = None

        # Si está cargando el mega rayo (aviso de 0.8 s)
        if self.cargando_rayo:
            self.tiempo_carga_rayo -= dt
            # Partículas de energía convergente en el visor/pecho
            core_x = self.x + 50
            core_y = self.y + 140
            efectos.crear_chispas_impacto(core_x, core_y, color=config.COLOR_VERDE_BRILLANTE, cantidad=4)
            if self.tiempo_carga_rayo <= 0:
                self.cargando_rayo = False
                es_rojo = self.fase_actual == 3
                self.rayo_activo = MegaRayoBoss(core_x, core_y, duracion=1.1, es_sol_rojo=es_rojo)
                sonido.reproducir_sfx("boss_alert")
                efectos.sacudir_pantalla(duracion=0.8, fuerza=8.0)

        # Si está lanzando ráfaga de misiles
        if self.misiles_pendientes > 0:
            self.cooldown_misil_boss -= dt
            if self.cooldown_misil_boss <= 0:
                # Lanzar misil desde los silos del hombro
                mx = self.x + 40
                my = self.y + 50 + (self.misiles_pendientes * 35)
                misiles_lista.append(Misil(mx, my))
                sonido.reproducir_sfx("enemy_laser")
                self.misiles_pendientes -= 1
                self.cooldown_misil_boss = 0.22

        # Mecánica de estirar puño cohete
        if self.punio_estirando:
            if not self.punio_regresando:
                self.distancia_punio += self.vel_punio * dt
                if self.distancia_punio >= self.distancia_max_punio:
                    self.punio_regresando = True
            else:
                self.distancia_punio -= self.vel_punio * dt * 1.3
                if self.distancia_punio <= 0:
                    self.distancia_punio = 0.0
                    self.punio_estirando = False
                    self.rect_punio = None
                    
            if self.punio_estirando and self.distancia_punio > 20:
                px = int(self.x - self.distancia_punio)
                py = int(self.punio_y)
                self.rect_punio = pygame.Rect(px, py - 30, 90, 60)
            else:
                self.rect_punio = None

        # Selección periódica de ataque
        self.temporizador_ataque -= dt
        cadencia = 2.8 if self.fase_actual == 1 else (2.1 if self.fase_actual == 2 else 1.5)
        
        if self.temporizador_ataque <= 0 and not self.punio_estirando and not self.cargando_rayo and not self.rayo_activo:
            self.temporizador_ataque = cadencia
            
            # Elegir mecánica: puño, misiles o mega rayo
            opciones = ['punio', 'misiles', 'mega_rayo']
            eleccion = random.choice(opciones)
            
            if eleccion == 'punio':
                self.punio_estirando = True
                self.punio_regresando = False
                self.distancia_punio = 0.0
                # Apuntar a la altura actual de Superman
                self.punio_y = target_superman.rect.centery
                sonido.reproducir_sfx("rocket_punch")
                efectos.sacudir_pantalla(duracion=0.3, fuerza=5.0)
                
            elif eleccion == 'misiles':
                self.misiles_pendientes = 3 if self.fase_actual < 3 else 5
                self.cooldown_misil_boss = 0.0
                
            elif eleccion == 'mega_rayo':
                self.cargando_rayo = True
                self.tiempo_carga_rayo = 0.8
                sonido.reproducir_sfx("boss_alert")

    def dibujar(self, superficie):
        # 1. Dibujar rayo gigante activo
        if self.rayo_activo:
            self.rayo_activo.dibujar(superficie)

        # 2. Dibujar brazo mecánico estirable y puño gigante
        if self.punio_estirando and self.distancia_punio > 10:
            origen_x = int(self.x + 60)
            origen_y = int(self.punio_y)
            punio_x = int(self.x - self.distancia_punio)
            
            # Segmentos reforzados del brazo
            num_seg = 14
            for s in range(num_seg):
                sx = origen_x - int((self.distancia_punio / num_seg) * s)
                pygame.draw.circle(superficie, config.COLOR_GRIS_METAL, (sx, origen_y), 10)
                pygame.draw.circle(superficie, config.COLOR_VERDE_BRILLANTE, (sx, origen_y), 5)
            pygame.draw.line(superficie, config.COLOR_GRIS_CLARO, (origen_x, origen_y), (punio_x + 50, origen_y), 14)
            
            # Sprite del puño gigante
            if self.sprite_fist:
                superficie.blit(self.sprite_fist, (punio_x, origen_y - 35))

        # 3. Dibujar cuerpo del robot gigante según fase
        if self.tiempo_hurt > 0 and self.sprite_hurt:
            superficie.blit(self.sprite_hurt, (int(self.x), int(self.y)))
        elif self.fase_actual == 1 and self.sprite_fase1:
            superficie.blit(self.sprite_fase1, (int(self.x), int(self.y)))
        elif self.fase_actual == 2 and self.sprite_fase2:
            superficie.blit(self.sprite_fase2, (int(self.x), int(self.y)))
        elif self.fase_actual == 3 and self.sprite_fase3:
            superficie.blit(self.sprite_fase3, (int(self.x), int(self.y)))
        elif self.sprite_fase1:
            superficie.blit(self.sprite_fase1, (int(self.x), int(self.y)))
