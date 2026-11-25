"""
sonidos.py — Administrador de audio y efectos de sonido para Superman: Nivel 1.
Gestiona la música de Metrópolis en bucle continuo y la reproducción de efectos retro.
"""

import os
import pygame
import config

class AdministradorSonido:
    def __init__(self):
        self.audio_disponible = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self.audio_disponible = True
        except Exception as e:
            print(f"[Audio] No se pudo inicializar mixer: {e}")
            self.audio_disponible = False
            
        self.sonidos = {}
        self.musica_cargada = False
        self.cargar_recursos()

    def cargar_recursos(self):
        if not self.audio_disponible:
            return
            
        archivos_sfx = {
            "laser": "laser.wav",
            "golpe": "golpe.wav",
            "enemy_laser": "enemy_laser.wav",
            "explosion": "explosion.wav",
            "sun_recharge": "sun_recharge.wav",
            "rocket_punch": "rocket_punch.wav",
            "boss_alert": "boss_alert.wav"
        }
        
        for clave, archivo in archivos_sfx.items():
            ruta = os.path.join(config.DIR_SFX, archivo)
            if os.path.exists(ruta):
                try:
                    s = pygame.mixer.Sound(ruta)
                    s.set_volume(0.45)
                    self.sonidos[clave] = s
                except Exception as e:
                    print(f"[Audio] Error al cargar {archivo}: {e}")
                    
        # Música de fondo
        ruta_musica = os.path.join(config.DIR_AUDIO, "musica_nivel1.ogg")
        if os.path.exists(ruta_musica):
            try:
                pygame.mixer.music.load(ruta_musica)
                pygame.mixer.music.set_volume(0.55)
                self.musica_cargada = True
            except Exception as e:
                print(f"[Audio] Error al cargar música: {e}")

    def reproducir_musica(self, bucle=-1):
        """Reproduce la canción de Metrópolis en bucle infinito si se alarga."""
        if self.audio_disponible and self.musica_cargada:
            try:
                if not pygame.mixer.music.get_busy():
                    pygame.mixer.music.play(loops=bucle)
            except Exception as e:
                print(f"[Audio] Error al reproducir música: {e}")

    def pausar_musica(self):
        if self.audio_disponible and self.musica_cargada:
            pygame.mixer.music.pause()

    def reanudar_musica(self):
        if self.audio_disponible and self.musica_cargada:
            pygame.mixer.music.unpause()

    def detener_musica(self):
        if self.audio_disponible and self.musica_cargada:
            pygame.mixer.music.stop()

    def reproducir_sfx(self, nombre):
        """Reproduce un efecto de sonido retro."""
        if self.audio_disponible and nombre in self.sonidos:
            try:
                self.sonidos[nombre].play()
            except Exception:
                pass
