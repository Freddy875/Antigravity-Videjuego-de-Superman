# 🦸 Superman — Videojuego en Python

Videojuego *shooter* de desplazamiento horizontal en **pixel art**, inspirado en clásicos arcade como *Metal Slug*, hecho en **Python + Pygame**. Este repositorio contiene el **Nivel 1: Metrópolis**, que funciona como tutorial.

> ⚖️ **Aviso:** Superman y todos los personajes y elementos relacionados son ™ y © de DC Comics, propiedad de Warner Bros. Todos los derechos reservados. Este es un proyecto **sin fines comerciales**, creado únicamente como proyecto de aprendizaje, para portafolio y como homenaje al personaje.

---

## 🎯 Propósito

- Aprender a desarrollar un videojuego completo: diseño, programación, arte y música.
- Practicar Python con un proyecto grande y organizado en módulos.
- Formar parte de mi **portafolio** como desarrollador.

## 🎮 El juego

Superman vuela sobre el cielo de Metrópolis (con el Daily Planet al fondo) y enfrenta oleadas de robots de Lex Luthor (**Rexbots / LexBots**) hasta llegar al jefe final: un temible **Robot Gigante (Final Boss)**.

El Nivel 1 enseña las 3 habilidades básicas: **vuelo, golpe físico y rayo láser**.

**Flujo del nivel:** Título → 5 oleadas (Tutorial con Rexbot 1, Escuadrón LexBot, Lluvia de misiles, Élite Rexbot 10, Pesado Rexbot 20 en motocicleta con puños mecánicos extensibles), con una **Zona de sol** de 6 s después de cada una → **Jefe final (Robot Gigante en 3 fases)** con sol permanente y láser continuo → **Victoria**.

| Concepto | Detalle |
|---|---|
| Género | Shooter horizontal (*side-scroller*) |
| Estética | Pixel art estilo 16 bits, Metrópolis brillante de día |
| Resolución | 1280 × 720, 60 FPS |
| Duración | ~2 min 30 s (lo que dura la canción original en bucle) |
| Plataforma | PC (Windows) |

## 🕹️ Controles

| Acción | Tecla |
|---|---|
| Volar | Flechas ↑ ↓ ← → (o W A S D) |
| Láser (visión térmica) | Espacio (disparo continuo sin recarga contra el Jefe) |
| Golpe físico | X (destruye misiles al instante sin recibir daño) |
| Recargar vida ☀️ | Volar hacia la parte superior (Sol radiante) |
| Pausa / continuar | P o Esc |
| Iniciar / reintentar | Enter |

## 🚀 Cómo ejecutarlo

### 🌐 Opción 1: En el Navegador Web (En línea / Local)
No necesitas configurar Pygame, funciona en cualquier navegador (Chrome, Edge, Firefox o móvil):
```powershell
cd Level1
python servidor_web.py
```
O simplemente haz doble clic en `Level1/jugar_en_navegador.bat`. El juego se abrirá automáticamente en tu navegador en [http://localhost:8000/index.html](http://localhost:8000/index.html).

---

### 💻 Opción 2: Versión de Escritorio (Pygame nativa)
Requisito: Python 3.10 o más reciente.

```powershell
cd Level1
python -m pip install -r requirements.txt
python main.py
```

La primera vez, el juego genera solo los sprites en `assets/sprites/`. Las instrucciones completas están en [`Level1/README.md`](Level1/README.md).

## 📁 Estructura

| Archivo | Contenido |
|---|---|
| `Level1/main.py` | Punto de entrada y estados del juego |
| `Level1/config.py` | Todos los valores ajustables (vida, daño, velocidades, oleadas, colores) |
| `Level1/jugador.py` | Superman: vuelo, vida, láser y golpe |
| `Level1/enemigos.py` | Rexbots (LexBot1, LexBot10, LexBot20 en moto) y misiles |
| `Level1/jefe.py` | Jefe final: Robot Gigante (puño cohete, misiles, mega rayo y 3 fases) |
| `Level1/oleadas.py` | Secuencia de oleadas y Zona de sol |
| `Level1/fondo.py` | Metrópolis en pixel art con sol brillante y efecto *parallax* |
| `Level1/efectos.py` | Chispas, explosiones, partículas y sacudida de pantalla |
| `Level1/pantallas.py` | Barra de vida dinámica, mensajes y pantallas de menú |
| `Level1/sonidos.py` | Música en bucle continuo y efectos retro sintetizados |
| `Level1/preparar_assets.py` | Procesa las imágenes y genera los sprites y audios |
| `Level1/requirements.txt` | Dependencias del proyecto (pygame, pillow, numpy, imageio-ffmpeg) |
| `Level1/GDD_Nivel1.md` | Documento de diseño del juego (reglas) |
| `Level1/GUIA_ESTILO.md` | Guía de estilo visual |

## 🎨 Créditos

| Elemento | Autor |
|---|---|
| Diseño de personajes | Fernando Sánchez Mejía |
| Fondo de la ciudad | Fernando Sánchez Mejía |
| Música original: *"Soaring Above the Metropolis"* | Fernando Sánchez Mejía |
| Diseño del juego y programación | Fernando Sánchez Mejía, con apoyo de Claude Code |

## 🗺️ Próximos pasos

- [ ] Imagen de la fase 2 del jefe
- [ ] Soporte para control (Xbox / PlayStation)
- [ ] Nuevos niveles

## 👤 Autor

**Fernando Sánchez Mejía**

📺 Video del gameplay en YouTube: *(agregar link)*
