# 🦸 Superman: Nivel 1 — Metrópolis (Tutorial)

Videojuego arcade *shooter* de desplazamiento horizontal (*side-scroller*) en **pixel art estilo 16 bits**, desarrollado en **Python 3 y Pygame**. En este nivel tutorial, Superman sobrevuela la resplandeciente ciudad de Metrópolis bajo la radiante luz del sol diurno, enfrentando al ejército de robots de LexCorp (**Rexbots**) hasta derrotar al colosal **Jefe Final** (Robot Gigante).

---

## 🎮 Mecánicas de Juego y Poderes

| Poder / Mecánica | Tecla | Efecto / Comportamiento |
|---|---|---|
| **Vuelo y Esquiva** | Flechas ↑ ↓ ← → (o W A S D) | Vuelo libre por toda la pantalla en 4 direcciones (60 FPS sin gravedad). |
| **Visión Térmica (Láser)** | **Espacio** | Dispara un potente rayo láser rojo desde los ojos (daño: 2). En oleadas normales tiene una cadencia moderada (0.25 s); **contra el Jefe Final no tiene tiempo de recarga** (ráfaga continua). |
| **Super Golpe (Fuerza)** | **X** (o J) | Ataque físico frontal a corta distancia (daño: 1). **Destruye misiles al instante sin recibir daño**, repele y empuja hacia atrás a los enemigos. |
| **Recarga Solar ☀️** | Volar hacia el Sol | Superman funciona como una batería solar fotovoltaica. Al volar hacia la zona superior iluminada por el sol, **recupera +15 HP por segundo** con destellos dorados y zumbido celestial. La zona de sol se activa tras cada oleada y está **100% activa de forma permanente durante la batalla contra el Jefe Final**. |
| **Pausa** | **P** o **ESC** | Congela la acción y la música de fondo. |
| **Iniciar / Confirmar** | **Enter** | Comienza la partida, reanuda o reintenta el nivel tras Game Over o Victoria. |

---

## 🤖 Galería de Enemigos

1. **Rexbot Nivel 1 (`LexBot1`)**:
   - Dron de patrulla básico.
   - **Resistencia:** Se destruye de **1 solo disparo láser** (o 2 golpes).
   - **Comportamiento:** Flota suavemente arriba y abajo; dispara láseres de kriptonita verde o sol rojo cada 3 segundos.
   - Si llega al lado izquierdo, no sale de la pantalla: permanece flotando hasta ser derrotado.

2. **Misil de LexCorp (`Misil`)**:
   - Proyectil balístico que avanza en línea recta a alta velocidad.
   - **Resistencia:** Se destruye de 1 disparo láser o de **1 solo golpe de Superman con la tecla X**.
   - **Esquivable:** Si sale por el borde izquierdo de la pantalla, **no pasa nada** (desaparece sin penalización).

3. **Rexbot Nivel 10 (`LexBot10`)**:
   - Droide de combate blindado y ágil.
   - **Resistencia:** Requiere **3 disparos láser** (o 6 golpes).
   - **Comportamiento:** Cambia de altitud constantemente, realiza maniobras evasivas y dispara ráfagas dobles de láser verde y rojo sol.

4. **Rexbot Nivel 20 (`LexBot20`)**:
   - Droide pesado montado en una **motocicleta voladora**.
   - **Resistencia:** Requiere **6 disparos láser** (o 12 golpes).
   - **Habilidad Especial:** Posee un **brazo mecánico telescópico con puño de acero** que estira velozmente hacia Superman para golpearlo, regresando después a la moto. Además, responde al fuego disparando láseres de sol rojo.

5. **Jefe Final: Robot Gigante (`FinalBoss`)**:
   - Colosal titán mecánico de LexCorp con armadura pesada y núcleo reactivo.
   - **Resistencia:** 70 puntos de vida (requiere más de 35 impactos de rayo láser).
   - **Tres Fases de Combate:**
     - *Fase 1 (100% – 66% de vida):* Armadura completa exterior.
     - *Fase 2 (66% – 33% de vida):* Blindaje quebrado con cables expuestos, chispas y sacudida de pantalla.
     - *Fase 3 (33% – 0% de vida):* Esqueleto metálico expuesto, ataques feroces y núcleo brillante.
   - **Ataques Devastadores:**
     - **Puño Cohete (Rocket Punch):** Lanza su descomunal puño de acero propulsado por cadena hidráulica barriendo la pantalla a la altura de Superman.
     - **Silos de Misiles:** Dispara ráfagas de 3 a 5 misiles balísticos desde sus hombros.
     - **Mega Rayo Láser:** Carga energía en su visor/núcleo (aviso de 0.8 s) y desata un rayo masivo horizontal que arrasa toda la pantalla.
   - **Ventajas de Superman contra el Jefe:**
     - Visión térmica **sin tiempo de recarga** (disparo ultrarrápido continuo).
     - **Sol 100% activo** en la parte superior para recargarse libremente durante todo el combate.

---

## 🎵 Música y Efectos de Sonido (SFX)

- **Música:** Pista original en bucle continuo *"Soaring above the metropolis"*, convertida a formato Vorbis OGG (`assets/audio/musica_nivel1.ogg`), sincronizada con la progresión del nivel y el combate final.
- **Efectos de Sonido (SFX 16 bits):**
  - `laser.wav`: Disparo agudo de visión térmica.
  - `golpe.wav`: Impacto contundente con crujido supersónico.
  - `enemy_laser.wav`: Pulso alienígena sintetizado de kriptonita/sol rojo.
  - `explosion.wav`: Explosión de 16 bits con graves profundos.
  - `sun_recharge.wav`: Arpegio armónico y zumbido celestial al recargar con el sol.
  - `rocket_punch.wav`: Ruido hidráulico y silbido metálico del puño extensible.
  - `boss_alert.wav`: Sirena de advertencia ante el ataque de energía del Jefe Final.

---

## 🌆 Escenario de Metrópolis en Pixel Art

El fondo del nivel cuenta con renderizado multicapa en *parallax*:
1. **Cielo y Sol:** Degradado azul brillante con un sol dorado radiante, corona de rayos y zona interactiva de recarga de vida.
2. **Nubes:** Nubes esponjosas en pixel art que avanzan a velocidad lenta.
3. **Horizonte Lejano:** Silueta de rascacielos y agujas en tonos dorados y azul acero.
4. **Metrópolis Vanguardista:** Edificios art deco de estilo 16 bits, ventanas iluminadas por la luz del día y el emblemático edificio del **Daily Planet** con su globo dorado.

---

## 📁 Estructura del Código

```text
VideoJuegoSuperman/Level1/
├── assets/
│   ├── audio/
│   │   └── musica_nivel1.ogg       # Música de fondo en bucle
│   ├── sfx/                        # Efectos de sonido sintetizados en 16 bits
│   │   ├── boss_alert.wav
│   │   ├── enemy_laser.wav
│   │   ├── explosion.wav
│   │   ├── golpe.wav
│   │   ├── laser.wav
│   │   ├── rocket_punch.wav
│   │   └── sun_recharge.wav
│   └── sprites/                    # Sprites recortados con alfa y animaciones
│       ├── superman_idle_*.png
│       ├── superman_laser.png
│       ├── superman_punch.png
│       ├── lexbot1_*.png
│       ├── lexbot10_*.png
│       ├── lexbot20_*.png, lexbot20_fist.png
│       ├── misil_*.png
│       ├── boss_fase1.png, boss_fase2.png, boss_fase3.png, boss_fist.png
│       ├── fondo_cielo_sol.png
│       ├── fondo_lejanos.png
│       └── fondo_edificios.png
├── config.py                       # Constantes, colores, balance y controles
├── efectos.py                      # Partículas cuadradas, chispas, textos y sacudida
├── enemigos.py                     # Rexbots 1, 10, 20 en moto y misiles
├── fondo.py                        # Sistema parallax y detección de zona solar
├── jefe.py                         # Jefe Final (robot gigante, 3 fases, puño, rayo, misiles)
├── jugador.py                      # Superman (vuelo, vida, láser, golpe, curación)
├── oleadas.py                      # Secuencia de 6 oleadas y zonas de sol
├── pantallas.py                    # HUD (barra de vida dinámica, mensajes, menús)
├── preparar_assets.py              # Script automatizado de extracción y generación de arte
├── sonidos.py                      # Administrador de audio y música
├── main.py                         # Bucle principal a 60 FPS y máquina de estados
└── requirements.txt                # Dependencias (pygame, pillow, numpy, imageio-ffmpeg)
```

---

## 🚀 Requisitos e Instalación

### Requisitos:
- Python 3.10 o superior (disponible en Windows, macOS o Linux).

### 🌐 Cómo jugar en el Navegador Web (En Línea / Local):
Puedes jugar directamente en Google Chrome, Microsoft Edge, Firefox o en el celular:

**Opción A — Doble clic (Windows):**
- Haz doble clic en el archivo `jugar_en_navegador.bat`. Se abrirá tu navegador predeterminado automáticamente.

**Opción B — Desde la terminal:**
```powershell
cd "c:\Users\fer87\Documents\MisProyectos\Antigravity\VideoJuegoSuperman\Level1"
python servidor_web.py
```
Abre en tu navegador la dirección: [http://localhost:8000/index.html](http://localhost:8000/index.html)

*(También incluye soporte táctil con controles virtuales en pantalla para celulares y tabletas, y puede subirse directamente a GitHub Pages, itch.io o Netlify sin modificar nada).*

---

### 💻 Cómo jugar en PC (Versión Pygame nativa):
1. Abre tu terminal o PowerShell en la carpeta `Level1`:
   ```powershell
   cd "c:\Users\fer87\Documents\MisProyectos\Antigravity\VideoJuegoSuperman\Level1"
   ```
2. Instala las dependencias:
   ```powershell
   python -m pip install -r requirements.txt
   ```
3. Ejecuta el juego:
   ```powershell
   python main.py
   ```
*(Nota: Si deseas regenerar o modificar los sprites y audios desde las imágenes fuente, puedes ejecutar `python preparar_assets.py`).*
