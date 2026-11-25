"""
pantallas.py — Interfaz de usuario (HUD), Menú de inicio, Pausa, Game Over y Victoria.
Diseñado con fuentes retro estilo arcade y siguiendo las especificaciones de GUIA_ESTILO.md.
"""

import math
import pygame
import config

class AdministradorPantallas:
    def __init__(self):
        self.fuente_grande = None
        self.fuente_media = None
        self.fuente_chica = None
        self.inicializar_fuentes()
        self.anim_pulso = 0.0

    def inicializar_fuentes(self):
        try:
            # Buscar fuentes tipo arcade o estándar en Windows
            nombres = ["Press Start 2P", "Consolas", "Courier New", "Arial"]
            for nombre in nombres:
                try:
                    self.fuente_grande = pygame.font.SysFont(nombre, 36, bold=True)
                    self.fuente_media = pygame.font.SysFont(nombre, 20, bold=True)
                    self.fuente_chica = pygame.font.SysFont(nombre, 14, bold=True)
                    if self.fuente_grande:
                        break
                except Exception:
                    continue
        except Exception:
            pass
            
        if not self.fuente_grande:
            self.fuente_grande = pygame.font.Font(None, 48)
            self.fuente_media = pygame.font.Font(None, 28)
            self.fuente_chica = pygame.font.Font(None, 20)

    def actualizar(self, dt):
        self.anim_pulso += dt * 4.0

    def render_texto_borde(self, superficie, texto, fuente, x, y, color_texto, color_borde=(0, 0, 0), centro=False):
        """Dibuja texto con contorno negro de 2px para máxima legibilidad."""
        surf_texto = fuente.render(texto, True, color_texto)
        rect = surf_texto.get_rect()
        if centro:
            rect.center = (int(x), int(y))
        else:
            rect.topleft = (int(x), int(y))
            
        # Dibujar contorno en 8 direcciones
        for dx, dy in ((-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)):
            surf_borde = fuente.render(texto, True, color_borde)
            superficie.blit(surf_borde, (rect.x + dx, rect.y + dy))
            
        superficie.blit(surf_texto, rect)
        return rect

    def dibujar_hud(self, superficie, superman, gestor_oleadas, fondo):
        # 1. Barra de Vida de Superman (arriba a la izquierda)
        barra_x, barra_y = 25, 30
        barra_ancho, barra_alto = 280, 20
        
        # Etiqueta "SUPERMAN"
        self.render_texto_borde(superficie, "SUPERMAN", self.fuente_chica, barra_x, barra_y - 20, config.COLOR_AMARILLO_EMBLEMA)
        
        # Marco exterior negro
        marco_rect = pygame.Rect(barra_x - 3, barra_y - 3, barra_ancho + 6, barra_alto + 6)
        pygame.draw.rect(superficie, config.COLOR_MARCO_HUD, marco_rect, border_radius=4)
        
        # Fondo oscuro de barra
        fondo_barra = pygame.Rect(barra_x, barra_y, barra_ancho, barra_alto)
        pygame.draw.rect(superficie, (40, 40, 45), fondo_barra, border_radius=2)
        
        # Ancho actual según vida (0 a 100)
        pct_vida = max(0.0, min(1.0, superman.vida / superman.vida_max))
        ancho_actual = int(barra_ancho * pct_vida)
        
        # Color dinámico de la vida: Verde -> Amarillo -> Rojo parpadeante
        if superman.vida > 50:
            color_barra = config.COLOR_VIDA_ALTA
        elif superman.vida > 25:
            color_barra = config.COLOR_VIDA_MEDIA
        else:
            # Parpadea en rojo crítico
            brillo = int(math.sin(self.anim_pulso * 2) * 50)
            color_barra = (min(255, config.COLOR_VIDA_BAJA[0] + brillo), config.COLOR_VIDA_BAJA[1], config.COLOR_VIDA_BAJA[2])
            
        if ancho_actual > 0:
            rect_relleno = pygame.Rect(barra_x, barra_y, ancho_actual, barra_alto)
            pygame.draw.rect(superficie, color_barra, rect_relleno, border_radius=2)
            # Brillo superior
            pygame.draw.line(superficie, (255, 255, 255, 180), (barra_x, barra_y + 2), (barra_x + ancho_actual, barra_y + 2), 2)

        # Texto numérico de vida
        texto_hp = f"{int(superman.vida)} / {superman.vida_max} HP"
        self.render_texto_borde(superficie, texto_hp, self.fuente_chica, barra_x + barra_ancho + 12, barra_y + 2, (255, 255, 255))

        # Indicador de recarga solar activa
        if fondo.zona_sol_activa:
            if fondo.esta_en_zona_sol(superman.rect):
                texto_sol = "☀️ ABSORBIENDO RADIACIÓN SOLAR (+HP)"
                col_sol = config.COLOR_AMARILLO_EMBLEMA
            else:
                texto_sol = "☀️ ZONA DE SOL ACTIVA: VUELA ARRIBA PARA CURARTE"
                col_sol = config.COLOR_SOL_CIRCULO
            self.render_texto_borde(superficie, texto_sol, self.fuente_chica, barra_x, barra_y + 28, col_sol)

        # 2. Barra de Vida del Jefe Final (arriba centrado/derecha)
        if gestor_oleadas.jefe_final and gestor_oleadas.jefe_final.activo:
            jefe = gestor_oleadas.jefe_final
            jb_x, jb_y = 650, 30
            jb_w, jb_h = 450, 18
            self.render_texto_borde(superficie, f"JEFE FINAL: ROBOT GIGANTE (FASE {jefe.fase_actual})", self.fuente_chica, jb_x, jb_y - 20, config.COLOR_OJOS_ROJOS)
            
            # Marco y relleno
            pygame.draw.rect(superficie, config.COLOR_MARCO_HUD, (jb_x - 3, jb_y - 3, jb_w + 6, jb_h + 6), border_radius=4)
            pygame.draw.rect(superficie, (35, 30, 40), (jb_x, jb_y, jb_w, jb_h), border_radius=2)
            pct_jefe = max(0.0, min(1.0, jefe.vida / jefe.vida_max))
            cur_w = int(jb_w * pct_jefe)
            if cur_w > 0:
                pygame.draw.rect(superficie, config.COLOR_VERDE_BRILLANTE, (jb_x, jb_y, cur_w, jb_h), border_radius=2)

        # 3. Banner de Oleada (grande en el centro superior)
        if gestor_oleadas.tiempo_mensaje_oleada > 0:
            self.render_texto_borde(superficie, gestor_oleadas.mensaje_oleada, self.fuente_grande, config.ANCHO_PANTALLA // 2, 90, config.COLOR_AMARILLO_EMBLEMA, centro=True)

        # 4. Mensajes de Tutorial / Consejos (abajo centrado)
        if gestor_oleadas.tiempo_mensaje_tutorial > 0:
            rect_tut = pygame.Rect(config.ANCHO_PANTALLA // 2 - 420, config.ALTO_PANTALLA - 65, 840, 45)
            # Fondo semitransparente con borde dorado
            surf_caja = pygame.Surface((rect_tut.width, rect_tut.height), pygame.SRCALPHA)
            surf_caja.fill((20, 24, 38, 220))
            superficie.blit(surf_caja, rect_tut.topleft)
            pygame.draw.rect(superficie, config.COLOR_AMARILLO_EMBLEMA, rect_tut, width=2, border_radius=6)
            self.render_texto_borde(superficie, gestor_oleadas.mensaje_tutorial, self.fuente_media, rect_tut.centerx, rect_tut.centery, (255, 255, 255), centro=True)

    def dibujar_titulo(self, superficie, fondo):
        fondo.dibujar(superficie)
        
        # Filtro semitransparente
        filtro = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA), pygame.SRCALPHA)
        filtro.fill((10, 20, 45, 140))
        superficie.blit(filtro, (0, 0))
        
        cx = config.ANCHO_PANTALLA // 2
        self.render_texto_borde(superficie, "SUPERMAN", self.fuente_grande, cx, 180, config.COLOR_ROJO_LUZ, centro=True)
        self.render_texto_borde(superficie, "NIVEL 1: METRÓPOLIS", self.fuente_media, cx, 235, config.COLOR_AMARILLO_EMBLEMA, centro=True)
        self.render_texto_borde(superficie, "TUTORIAL DE VUELO, LÁSER Y COMBATE", self.fuente_chica, cx, 275, (230, 240, 255), centro=True)
        
        # Cuadro de controles
        caja = pygame.Rect(cx - 300, 325, 600, 180)
        caja_s = pygame.Surface((caja.width, caja.height), pygame.SRCALPHA)
        caja_s.fill((20, 25, 40, 210))
        superficie.blit(caja_s, caja.topleft)
        pygame.draw.rect(superficie, config.COLOR_AZUL_LUZ, caja, width=2, border_radius=8)
        
        self.render_texto_borde(superficie, "CONTROLES DE JUEGO:", self.fuente_chica, cx, 350, config.COLOR_AMARILLO_EMBLEMA, centro=True)
        self.render_texto_borde(superficie, "FLECHAS  -> Volar libremente por Metrópolis", self.fuente_chica, cx - 240, 385, (255, 255, 255))
        self.render_texto_borde(superficie, "ESPACIO  -> Rayos láser (visión térmica)", self.fuente_chica, cx - 240, 415, (255, 255, 255))
        self.render_texto_borde(superficie, "TECLA X  -> Golpe físico (destruye misiles al instante)", self.fuente_chica, cx - 240, 445, (255, 255, 255))
        self.render_texto_borde(superficie, "SOL ☀️   -> Vuela hacia el sol para recuperar energía", self.fuente_chica, cx - 240, 475, config.COLOR_SOL_CIRCULO)

        # Mensaje de inicio parpadeante
        if int(self.anim_pulso * 1.5) % 2 == 0:
            self.render_texto_borde(superficie, ">> PRESIONA ENTER PARA COMENZAR <<", self.fuente_media, cx, 560, config.COLOR_AMARILLO_EMBLEMA, centro=True)

    def dibujar_pausa(self, superficie):
        filtro = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA), pygame.SRCALPHA)
        filtro.fill((10, 15, 30, 180))
        superficie.blit(filtro, (0, 0))
        
        cx = config.ANCHO_PANTALLA // 2
        self.render_texto_borde(superficie, "JUEGO EN PAUSA", self.fuente_grande, cx, 300, config.COLOR_AMARILLO_EMBLEMA, centro=True)
        self.render_texto_borde(superficie, "Presiona P o ESC para continuar volando", self.fuente_media, cx, 360, (255, 255, 255), centro=True)

    def dibujar_game_over(self, superficie):
        filtro = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA), pygame.SRCALPHA)
        filtro.fill((50, 10, 15, 210))
        superficie.blit(filtro, (0, 0))
        
        cx = config.ANCHO_PANTALLA // 2
        self.render_texto_borde(superficie, "GAME OVER", self.fuente_grande, cx, 280, config.COLOR_VIDA_BAJA, centro=True)
        self.render_texto_borde(superficie, "Superman ha agotado su energía solar.", self.fuente_media, cx, 340, (255, 255, 255), centro=True)
        self.render_texto_borde(superficie, "Recuerda acercarte al sol para recargarte cuando estés herido.", self.fuente_chica, cx, 385, config.COLOR_AMARILLO_EMBLEMA, centro=True)
        
        if int(self.anim_pulso * 1.5) % 2 == 0:
            self.render_texto_borde(superficie, ">> Presiona ENTER para reintentar el Nivel 1 <<", self.fuente_media, cx, 470, (255, 255, 255), centro=True)

    def dibujar_victoria(self, superficie):
        filtro = pygame.Surface((config.ANCHO_PANTALLA, config.ALTO_PANTALLA), pygame.SRCALPHA)
        filtro.fill((15, 35, 60, 200))
        superficie.blit(filtro, (0, 0))
        
        cx = config.ANCHO_PANTALLA // 2
        self.render_texto_borde(superficie, "¡VICTORIA HEROICA!", self.fuente_grande, cx, 210, config.COLOR_AMARILLO_EMBLEMA, centro=True)
        self.render_texto_borde(superficie, "¡El robot gigante de LexCorp ha sido destruido!", self.fuente_media, cx, 270, (255, 255, 255), centro=True)
        self.render_texto_borde(superficie, "Has protegido la ciudad de Metrópolis y completado el tutorial.", self.fuente_media, cx, 310, (220, 240, 255), centro=True)
        self.render_texto_borde(superficie, "Próximamente: Nivel 2", self.fuente_chica, cx, 360, config.COLOR_AZUL_LUZ, centro=True)
        
        if int(self.anim_pulso * 1.5) % 2 == 0:
            self.render_texto_borde(superficie, ">> Presiona ENTER para volver a la pantalla de título <<", self.fuente_media, cx, 480, config.COLOR_AMARILLO_EMBLEMA, centro=True)
