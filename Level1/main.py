"""
main.py — Punto de entrada del videojuego Superman: Nivel 1 (Metrópolis).
Bucle principal a 60 FPS, máquina de estados, gestión de colisiones completas,
integración de audio, efectos visuales y renderizado en pantalla.
"""

import sys
import os
import pygame
import config
from sonidos import AdministradorSonido
from fondo import FondoMetropolis
from efectos import SistemaEfectos
from jugador import Superman
from enemigos import LexBot20
from oleadas import GestorOleadas
from pantallas import AdministradorPantallas

class JuegoSuperman:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(config.TITULO_JUEGO)
        self.pantalla = pygame.display.set_mode((config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        self.reloj = pygame.time.Clock()
        self.ejecutando = True
        
        # Superficie de renderizado para permitir sacudidas de pantalla
        self.lienzo = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA))
        
        # Módulos del juego
        self.sonido = AdministradorSonido()
        self.fondo = FondoMetropolis()
        self.efectos = SistemaEfectos()
        self.pantallas = AdministradorPantallas()
        
        # Estado del juego: 'TITULO', 'JUGANDO', 'PAUSA', 'GAME_OVER', 'VICTORIA'
        self.estado = "TITULO"
        
        # Instancias de juego
        self.superman = None
        self.gestor_oleadas = None
        
        # Iniciar música en bucle
        self.sonido.reproducir_musica(bucle=-1)

    def reiniciar_partida(self):
        self.superman = Superman(x=120, y=300)
        self.gestor_oleadas = GestorOleadas(self.fondo, self.efectos, self.sonido)
        self.efectos.particulas.clear()
        self.efectos.textos.clear()
        self.fondo.desactivar_zona_sol()

    def procesar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.ejecutando = False
                
            elif evento.type == pygame.KEYDOWN:
                if self.estado == "TITULO":
                    if evento.key in config.TECLAS_CONFIRMAR:
                        self.reiniciar_partida()
                        self.estado = "JUGANDO"
                        
                elif self.estado == "JUGANDO":
                    if evento.key in config.TECLAS_PAUSA:
                        self.estado = "PAUSA"
                        self.sonido.pausar_musica()
                        
                elif self.estado == "PAUSA":
                    if evento.key in config.TECLAS_PAUSA:
                        self.estado = "JUGANDO"
                        self.sonido.reanudar_musica()
                        
                elif self.estado in ("GAME_OVER", "VICTORIA"):
                    if evento.key in config.TECLAS_CONFIRMAR:
                        self.reiniciar_partida()
                        self.estado = "JUGANDO"

    def verificar_colisiones(self, dt):
        superman = self.superman
        oleadas = self.gestor_oleadas
        efectos = self.efectos
        sonido = self.sonido

        # 1. Láseres de Superman vs Enemigos y Misiles
        for laser in superman.laseres:
            if not laser.activo:
                continue
                
            # Contra enemigos normales
            for e in oleadas.enemigos:
                if e.activo and laser.rect.colliderect(e.rect):
                    laser.activo = False
                    murio = e.recibir_danio(laser.danio)
                    efectos.crear_chispas_impacto(laser.rect.right, laser.rect.centery, color=config.COLOR_LASER_SUPERMAN_HALO, cantidad=8)
                    if murio:
                        efectos.crear_explosion(e.rect.centerx, e.rect.centery)
                        sonido.reproducir_sfx("explosion")
                    break

            # Contra misiles
            if laser.activo:
                for m in oleadas.misiles:
                    if m.activo and laser.rect.colliderect(m.rect):
                        laser.activo = False
                        m.recibir_danio(laser.danio)
                        efectos.crear_explosion(m.rect.centerx, m.rect.centery)
                        sonido.reproducir_sfx("explosion")
                        break

            # Contra Jefe Final
            if laser.activo and oleadas.jefe_final and oleadas.jefe_final.activo:
                if laser.rect.colliderect(oleadas.jefe_final.rect):
                    laser.activo = False
                    oleadas.jefe_final.recibir_danio(laser.danio, efectos)
                    break

        # 2. Golpe de Superman (fuerza destructiva con puños)
        if superman.golpe_activo and superman.rect_golpe:
            # Contra enemigos normales
            for e in oleadas.enemigos:
                if e.activo and superman.rect_golpe.colliderect(e.rect):
                    murio = e.recibir_danio(config.SUPERMAN_DANIO_GOLPE)
                    e.empujar(config.SUPERMAN_EMPUJE_GOLPE)
                    efectos.crear_chispas_impacto(e.rect.centerx, e.rect.centery, color=(255, 255, 255), cantidad=14)
                    efectos.agregar_texto(e.rect.centerx, e.rect.top - 15, "¡GOLPE!", config.COLOR_AMARILLO_EMBLEMA)
                    if murio:
                        efectos.crear_explosion(e.rect.centerx, e.rect.centery)
                        sonido.reproducir_sfx("explosion")

            # Contra misiles: ¡los destruye al instante sin recibir daño!
            for m in oleadas.misiles:
                if m.activo and superman.rect_golpe.colliderect(m.rect):
                    m.recibir_danio(999)
                    efectos.crear_explosion(m.rect.centerx, m.rect.centery)
                    efectos.agregar_texto(m.rect.centerx, m.rect.top - 10, "¡DESTRUIDO!", config.COLOR_AMARILLO_EMBLEMA)
                    sonido.reproducir_sfx("explosion")

            # Contra Jefe Final
            if oleadas.jefe_final and oleadas.jefe_final.activo:
                if superman.rect_golpe.colliderect(oleadas.jefe_final.rect):
                    oleadas.jefe_final.recibir_danio(config.SUPERMAN_DANIO_GOLPE, efectos)
                    efectos.crear_chispas_impacto(superman.rect_golpe.right, superman.rect_golpe.centery, color=(255, 255, 255), cantidad=10)

        # 3. Láseres enemigos vs Superman
        for l in oleadas.laseres_enemigos:
            if l.activo and l.rect.colliderect(superman.rect):
                l.activo = False
                superman.recibir_danio(l.danio, efectos, sonido)

        # 4. Misiles vs Superman (choque)
        for m in oleadas.misiles:
            if m.activo and m.rect.colliderect(superman.rect):
                m.recibir_danio(999)
                efectos.crear_explosion(m.rect.centerx, m.rect.centery)
                sonido.reproducir_sfx("explosion")
                superman.recibir_danio(m.danio, efectos, sonido)

        # 5. Choque directo de enemigos vs Superman
        for e in oleadas.enemigos:
            if e.activo and e.rect.colliderect(superman.rect):
                superman.recibir_danio(e.danio_choque, efectos, sonido)
                e.empujar(80)

        # 6. Puño extensible de LexBot20 vs Superman
        for e in oleadas.enemigos:
            if isinstance(e, LexBot20) and e.rect_punio:
                if e.rect_punio.colliderect(superman.rect):
                    superman.recibir_danio(config.LEXBOT20_DANIO_PUNIO, efectos, sonido)
                    efectos.sacudir_pantalla(duracion=0.35, fuerza=6.0)

        # 7. Ataques del Jefe Final vs Superman
        if oleadas.jefe_final and oleadas.jefe_final.activo:
            jefe = oleadas.jefe_final
            # Puño cohete gigante
            if jefe.rect_punio and jefe.rect_punio.colliderect(superman.rect):
                superman.recibir_danio(config.JEFE_DANIO_PUNIO, efectos, sonido)
                efectos.sacudir_pantalla(duracion=0.45, fuerza=8.0)
            # Mega Rayo Láser horizontal
            if jefe.rayo_activo and jefe.rayo_activo.rect.colliderect(superman.rect):
                superman.recibir_danio(config.JEFE_DANIO_RAYO * dt, efectos, sonido)
            # Choque con cuerpo del jefe
            if jefe.rect.colliderect(superman.rect):
                superman.recibir_danio(config.JEFE_DANIO_CHOQUE, efectos, sonido)

        # 8. Recarga Solar si Superman está en la zona del sol
        if self.fondo.esta_en_zona_sol(superman.rect):
            superman.recargar_energia_solar(dt, efectos, sonido)

        # 9. Comprobar derrota de Superman (Game Over)
        if superman.vida <= 0:
            self.estado = "GAME_OVER"
            efectos.sacudir_pantalla(duracion=0.8, fuerza=10.0)

        # 10. Comprobar Victoria del nivel
        if oleadas.estado == "VICTORIA":
            self.estado = "VICTORIA"

    def actualizar(self, dt):
        self.pantallas.actualizar(dt)
        
        if self.estado == "TITULO":
            self.fondo.actualizar(dt)
            
        elif self.estado == "JUGANDO":
            teclas = pygame.key.get_pressed()
            jefe_activo = (self.gestor_oleadas.jefe_final is not None and self.gestor_oleadas.jefe_final.activo)
            
            # Superman procesa entrada y actualiza
            self.superman.procesar_entrada(teclas, jefe_activo, self.sonido)
            self.superman.actualizar(dt)
            
            # Fondo, oleadas y efectos
            self.fondo.actualizar(dt)
            self.gestor_oleadas.actualizar(dt, self.superman)
            self.efectos.actualizar(dt)
            
            # Colisiones y mecánicas
            self.verificar_colisiones(dt)

    def renderizar(self):
        # 1. Dibujar el mundo del juego en el lienzo
        if self.estado in ("JUGANDO", "PAUSA", "GAME_OVER", "VICTORIA"):
            self.fondo.dibujar(self.lienzo)
            self.gestor_oleadas.dibujar(self.lienzo)
            self.superman.dibujar(self.lienzo)
            self.efectos.dibujar(self.lienzo)
            
            # Blit del lienzo a la pantalla con sacudida
            dx, dy = self.efectos.obtener_desplazamiento_sacudida()
            self.pantalla.fill((0, 0, 0))
            self.pantalla.blit(self.lienzo, (dx, dy))
            
            # 2. Dibujar HUD sobre la pantalla fija
            self.pantallas.dibujar_hud(self.pantalla, self.superman, self.gestor_oleadas, self.fondo)
            
            # Pantallas superpuestas
            if self.estado == "PAUSA":
                self.pantallas.dibujar_pausa(self.pantalla)
            elif self.estado == "GAME_OVER":
                self.pantallas.dibujar_game_over(self.pantalla)
            elif self.estado == "VICTORIA":
                self.pantallas.dibujar_victoria(self.pantalla)

        elif self.estado == "TITULO":
            self.pantallas.dibujar_titulo(self.pantalla, self.fondo)

        pygame.display.flip()

    def ejecutar(self):
        while self.ejecutando:
            dt = self.reloj.tick(config.FPS) / 1000.0
            # Evitar saltos de física tras pausas largas
            dt = min(0.05, dt)
            
            self.procesar_eventos()
            self.actualizar(dt)
            self.renderizar()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    juego = JuegoSuperman()
    juego.ejecutar()
