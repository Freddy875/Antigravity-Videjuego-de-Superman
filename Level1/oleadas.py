"""
oleadas.py — Gestor de Oleadas, Mensajes de Tutorial y Transiciones de Nivel 1.
Controla el flujo de las 6 oleadas, el spawn de enemigos y las Zonas de Sol intermedias.
"""

import random
import config
from enemigos import Misil, LexBot1, LexBot10, LexBot20
from jefe import FinalBoss

class GestorOleadas:
    def __init__(self, fondo, efectos, sonido):
        self.fondo = fondo
        self.efectos = efectos
        self.sonido = sonido
        
        self.oleada_actual = 1
        self.total_oleadas = 6
        self.estado = "EN_COMBATE"  # 'EN_COMBATE', 'ZONA_SOL', 'VICTORIA'
        
        # Listas activas de entidades
        self.enemigos = []
        self.misiles = []
        self.laseres_enemigos = []
        self.jefe_final = None
        
        # Colas de spawn diferido para oleadas grandes
        self.cola_spawn = []
        self.temporizador_spawn = 0.0
        
        # Temporizador de la zona de sol entre oleadas
        self.temporizador_sol = 0.0
        
        # Banners y mensajes de interfaz
        self.mensaje_oleada = ""
        self.tiempo_mensaje_oleada = 0.0
        self.mensaje_tutorial = ""
        self.tiempo_mensaje_tutorial = 0.0
        
        # Iniciar primera oleada
        self.iniciar_oleada(1)

    def iniciar_oleada(self, num):
        self.oleada_actual = num
        self.estado = "EN_COMBATE"
        self.cola_spawn.clear()
        self.fondo.desactivar_zona_sol()
        
        if num == 1:
            # Tutorial: 1 LexBot1
            self.mensaje_oleada = "OLEADA 1: TUTORIAL"
            self.tiempo_mensaje_oleada = 3.0
            self.mensaje_tutorial = "FLECHAS = Volar  |  ESPACIO = Láser  |  X = Golpe"
            self.tiempo_mensaje_tutorial = 6.0
            self.enemigos.append(LexBot1(config.ANCHO_PANTALLA + 40, 300))
            
        elif num == 2:
            # Grupo: 5 LexBot1
            self.mensaje_oleada = "OLEADA 2: ESCUADRÓN LEXBOT"
            self.tiempo_mensaje_oleada = 2.5
            self.mensaje_tutorial = "¡Destrúyelos con tu visión térmica!"
            self.tiempo_mensaje_tutorial = 4.0
            alturas = [160, 260, 360, 460, 540]
            for i, y in enumerate(alturas):
                self.cola_spawn.append({
                    "tiempo": i * 0.7,
                    "crear": lambda y=y: self.enemigos.append(LexBot1(config.ANCHO_PANTALLA + 40, y))
                })
                
        elif num == 3:
            # Lluvia de misiles: 12 misiles en 4 grupos de 3
            self.mensaje_oleada = "OLEADA 3: ¡LLUVIA DE MISILES!"
            self.tiempo_mensaje_oleada = 2.5
            self.mensaje_tutorial = "Usa X para golpear misiles o esquívalos libremente"
            self.tiempo_mensaje_tutorial = 5.0
            for g in range(4):
                alturas_g = random.sample([180, 280, 380, 480, 560], 3)
                for i, y in enumerate(alturas_g):
                    self.cola_spawn.append({
                        "tiempo": g * 1.8 + i * 0.2,
                        "crear": lambda y=y: self.misiles.append(Misil(config.ANCHO_PANTALLA + 40, y))
                    })
                    
        elif num == 4:
            # Élite: 3 LexBot10
            self.mensaje_oleada = "OLEADA 4: LEXBOTS ÉLITE"
            self.tiempo_mensaje_oleada = 2.5
            self.mensaje_tutorial = "¡Cuidado con los láseres verdes y de sol rojo!"
            self.tiempo_mensaje_tutorial = 5.0
            for i, y in enumerate([200, 340, 480]):
                self.cola_spawn.append({
                    "tiempo": i * 1.0,
                    "crear": lambda y=y: self.enemigos.append(LexBot10(config.ANCHO_PANTALLA + 40, y))
                })
                
        elif num == 5:
            # Pesado: 1 LexBot20 en moto + 2 LexBot1
            self.mensaje_oleada = "OLEADA 5: MOTO-BOT PESADO"
            self.tiempo_mensaje_oleada = 2.5
            self.mensaje_tutorial = "¡El LexBot20 estira sus puños mecánicos!"
            self.tiempo_mensaje_tutorial = 5.0
            self.enemigos.append(LexBot20(config.ANCHO_PANTALLA + 40, 320))
            self.cola_spawn.append({
                "tiempo": 1.2,
                "crear": lambda: self.enemigos.append(LexBot1(config.ANCHO_PANTALLA + 40, 180))
            })
            self.cola_spawn.append({
                "tiempo": 1.6,
                "crear": lambda: self.enemigos.append(LexBot1(config.ANCHO_PANTALLA + 40, 480))
            })
            
        elif num == 6:
            # Jefe Final: Robot Gigante
            self.mensaje_oleada = "¡ALERTA: JEFE FINAL ROBOT GIGANTE!"
            self.tiempo_mensaje_oleada = 4.0
            self.mensaje_tutorial = "¡Láser sin recarga! Acércate al sol para recargar vida constante"
            self.tiempo_mensaje_tutorial = 7.0
            self.sonido.reproducir_sfx("boss_alert")
            self.efectos.sacudir_pantalla(duracion=1.0, fuerza=8.0)
            self.jefe_final = FinalBoss()
            # El sol está permanentemente activo durante el combate contra el jefe final
            self.fondo.activar_zona_sol(permanente=True)

    def actualizar(self, dt, superman):
        # Actualizar mensajes de texto
        if self.tiempo_mensaje_oleada > 0:
            self.tiempo_mensaje_oleada -= dt
        if self.tiempo_mensaje_tutorial > 0:
            self.tiempo_mensaje_tutorial -= dt

        # Spawn diferido
        if self.cola_spawn:
            for item in list(self.cola_spawn):
                item["tiempo"] -= dt
                if item["tiempo"] <= 0:
                    item["crear"]()
                    self.cola_spawn.remove(item)

        # Actualizar enemigos normales
        for e in self.enemigos:
            e.actualizar(dt, superman, self.laseres_enemigos, self.sonido)
        self.enemigos = [e for e in self.enemigos if e.activo]

        # Actualizar misiles
        for m in self.misiles:
            m.actualizar(dt)
        self.misiles = [m for m in self.misiles if m.activo]

        # Actualizar láseres enemigos
        for l in self.laseres_enemigos:
            l.actualizar(dt)
        self.laseres_enemigos = [l for l in self.laseres_enemigos if l.activo]

        # Actualizar Jefe Final si existe
        if self.jefe_final and self.jefe_final.activo:
            self.jefe_final.actualizar(dt, superman, self.misiles, self.laseres_enemigos, self.efectos, self.sonido)
            if self.jefe_final.derrotado:
                self.estado = "VICTORIA"
                self.mensaje_oleada = "¡METRÓPOLIS ESTÁ A SALVO!"
                self.tiempo_mensaje_oleada = 999.0

        # Comprobar finalización de oleada normal
        if self.estado == "EN_COMBATE" and self.oleada_actual < 6:
            if not self.enemigos and not self.misiles and not self.cola_spawn:
                # Oleada superada -> activar Zona Solar de 6 segundos
                self.estado = "ZONA_SOL"
                self.temporizador_sol = config.TIEMPO_ZONA_SOL_OLEADA
                self.fondo.activar_zona_sol(permanente=False)
                self.mensaje_oleada = "¡OLEADA COMPLETADA!"
                self.tiempo_mensaje_oleada = 2.0
                self.mensaje_tutorial = "☀️ ¡VUELA HACIA EL SOL PARA RECARGAR TU ENERGÍA! ☀️"
                self.tiempo_mensaje_tutorial = 5.5

        # Temporizador de la zona de sol
        if self.estado == "ZONA_SOL":
            self.temporizador_sol -= dt
            if self.temporizador_sol <= 0:
                self.fondo.desactivar_zona_sol()
                if self.oleada_actual < self.total_oleadas:
                    self.iniciar_oleada(self.oleada_actual + 1)

    def dibujar(self, superficie):
        # Dibujar misiles
        for m in self.misiles:
            m.dibujar(superficie)
            
        # Dibujar enemigos normales
        for e in self.enemigos:
            e.dibujar(superficie)
            
        # Dibujar jefe final
        if self.jefe_final and self.jefe_final.activo:
            self.jefe_final.dibujar(superficie)
            
        # Dibujar láseres enemigos
        for l in self.laseres_enemigos:
            l.dibujar(superficie)
