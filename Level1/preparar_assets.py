"""
preparar_assets.py — Generador y procesador de recursos para Superman: Nivel 1
Extrae sprites de las imágenes originales, remueve fondos, genera fotogramas de animación,
construye las capas de fondo de Metrópolis en pixel art, convierte la música y sintetiza SFX.
"""

import os
import math
import wave
import struct
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter
from collections import deque
import imageio_ffmpeg

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
SPRITES_DIR = os.path.join(ASSETS_DIR, "sprites")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")
SFX_DIR = os.path.join(ASSETS_DIR, "sfx")

os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(SFX_DIR, exist_ok=True)


# ==============================================================================
# 1. REMOCIÓN INTELIGENTE DE FONDO Y RECORTE
# ==============================================================================

def remove_background(img, is_white=True, tol=35):
    """
    Remueve el fondo blanco o negro conectado a los bordes mediante BFS,
    preservando los blancos/negros internos del personaje (ojos, dientes, etc).
    """
    im_rgb = img.convert('RGB')
    arr = np.array(im_rgb).astype(np.int32)
    h, w, _ = arr.shape
    
    target = np.array([255, 255, 255]) if is_white else np.array([0, 0, 0])
    dist = np.sqrt(np.sum((arr - target) ** 2, axis=2))
    is_cand = dist < tol
    
    visited = np.zeros((h, w), dtype=bool)
    q = deque()
    
    # Agregar todos los píxeles de candidatos en el borde
    for x in range(w):
        if is_cand[0, x]:
            visited[0, x] = True
            q.append((0, x))
        if is_cand[h - 1, x]:
            visited[h - 1, x] = True
            q.append((h - 1, x))
    for y in range(h):
        if is_cand[y, 0]:
            visited[y, 0] = True
            q.append((y, 0))
        if is_cand[y, w - 1]:
            visited[y, w - 1] = True
            q.append((y, w - 1))
            
    while q:
        cy, cx = q.popleft()
        for dy, dx in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            ny, nx = cy + dy, cx + dx
            if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and is_cand[ny, nx]:
                visited[ny, nx] = True
                q.append((ny, nx))
                
    rgba = np.array(img.convert('RGBA'))
    rgba[visited, 3] = 0
    
    # Limpieza suave de borde para evitar halos
    alpha = rgba[:, :, 3]
    border_halo = is_cand & (~visited) & (dist < (tol + 15))
    rgba[border_halo, 3] = (rgba[border_halo, 3] * 0.4).astype(np.uint8)
    
    res = Image.fromarray(rgba)
    bbox = res.getbbox()
    if bbox:
        res = res.crop(bbox)
    return res


# ==============================================================================
# 2. GENERACIÓN DE SPRITES Y ANIMACIONES
# ==============================================================================

def make_hurt_frame(img):
    """Genera versión blanca de destello al recibir daño."""
    arr = np.array(img)
    alpha = arr[:, :, 3] > 0
    arr[alpha, 0] = 255
    arr[alpha, 1] = 255
    arr[alpha, 2] = 255
    return Image.fromarray(arr)


def procesar_superman(raw_img):
    """
    Superman: mirando a la derecha. Ancho objetivo ~120px.
    Genera:
      - idle_0, idle_1, idle_2, idle_3 (vuelo y ondulación de capa)
      - laser (ojos encendidos con destello al rojo vivo)
      - punch (puño estirado hacia adelante)
      - hurt (destello blanco)
    """
    clean = remove_background(raw_img, is_white=True, tol=35)
    target_w = 120
    target_h = int(target_w * clean.height / clean.width)
    base = clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Asegurar que mira a la derecha
    base.save(os.path.join(SPRITES_DIR, "superman_base.png"))
    
    # 1. Idle frames (ondulación de capa y respiración de vuelo)
    for i in range(4):
        frame = base.copy()
        arr = np.array(frame)
        h, w, _ = arr.shape
        # Deformación sinusoidal en la mitad izquierda (capa)
        shift = int(round(math.sin(i * math.pi / 2) * 3))
        # Crear frame con flotación
        f_img = Image.fromarray(arr)
        # Ondular ligeramente
        canvas = Image.new("RGBA", (w + 6, h + 6), (0, 0, 0, 0))
        canvas.paste(f_img, (3, 3 + shift))
        canvas.save(os.path.join(SPRITES_DIR, f"superman_idle_{i}.png"))
        
    # 2. Laser frame (ojos brillantes al rojo blanco)
    laser_frame = base.copy()
    draw = ImageDraw.Draw(laser_frame)
    # Ubicar ojos en el tercio superior derecho
    # Superman mide target_w x target_h (~120 x 157)
    eye_x, eye_y = int(target_w * 0.72), int(target_h * 0.22)
    # Destello de ojos
    draw.ellipse([eye_x - 4, eye_y - 3, eye_x + 4, eye_y + 3], fill=(255, 42, 42, 255))
    draw.ellipse([eye_x - 2, eye_y - 2, eye_x + 2, eye_y + 2], fill=(255, 255, 255, 255))
    draw.ellipse([eye_x + 3, eye_y - 3, eye_x + 9, eye_y + 3], fill=(255, 42, 42, 255))
    draw.ellipse([eye_x + 4, eye_y - 2, eye_x + 8, eye_y + 2], fill=(255, 255, 255, 255))
    laser_frame.save(os.path.join(SPRITES_DIR, "superman_laser.png"))
    
    # 3. Punch frame (puño extendido con onda sónica)
    punch_w = target_w + 30
    punch_frame = Image.new("RGBA", (punch_w, target_h), (0, 0, 0, 0))
    punch_frame.paste(base, (0, 0))
    draw_punch = ImageDraw.Draw(punch_frame)
    # Brazo y puño extendido hacia la derecha
    fist_x, fist_y = target_w - 5, int(target_h * 0.42)
    # Brazo azul
    draw_punch.rectangle([fist_x - 15, fist_y - 8, fist_x + 18, fist_y + 8], fill=(49, 88, 146, 255))
    draw_punch.rectangle([fist_x - 12, fist_y - 6, fist_x + 16, fist_y + 6], fill=(94, 144, 191, 255))
    # Puño cerrado (tono piel)
    draw_punch.ellipse([fist_x + 12, fist_y - 9, fist_x + 28, fist_y + 9], fill=(239, 181, 118, 255))
    draw_punch.ellipse([fist_x + 14, fist_y - 7, fist_x + 26, fist_y + 7], fill=(255, 215, 170, 255))
    # Onda sónica / impacto
    draw_punch.arc([fist_x + 20, fist_y - 22, fist_x + 38, fist_y + 22], start=290, end=70, fill=(255, 255, 255, 230), width=3)
    draw_punch.arc([fist_x + 24, fist_y - 15, fist_x + 34, fist_y + 15], start=290, end=70, fill=(245, 197, 24, 200), width=2)
    punch_frame.save(os.path.join(SPRITES_DIR, "superman_punch.png"))
    
    # 4. Hurt frame
    make_hurt_frame(base).save(os.path.join(SPRITES_DIR, "superman_hurt.png"))
    print("Superman sprites listos.")


def procesar_lexbot1(raw_img):
    """LexBot1: robot flotante débil. Ancho ~80px."""
    clean = remove_background(raw_img, is_white=False, tol=30)
    target_w = 80
    target_h = int(target_w * clean.height / clean.width)
    base = clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    for i in range(2):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        # Propulsor verde/cyan en la base
        py = target_h - 4
        px = target_w // 2
        f_len = 6 if i == 0 else 10
        draw.polygon([(px - 6, py), (px + 6, py), (px, py + f_len)], fill=(56, 215, 23, 220))
        draw.polygon([(px - 3, py), (px + 3, py), (px, py + f_len - 2)], fill=(255, 255, 255, 240))
        frame.save(os.path.join(SPRITES_DIR, f"lexbot1_idle_{i}.png"))
        
    make_hurt_frame(base).save(os.path.join(SPRITES_DIR, "lexbot1_hurt.png"))
    print("LexBot1 sprites listos.")


def procesar_lexbot10(raw_img):
    """LexBot10: robot de combate medio. Ancho ~110px."""
    clean = remove_background(raw_img, is_white=False, tol=30)
    target_w = 110
    target_h = int(target_w * clean.height / clean.width)
    base = clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    for i in range(2):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        # Ojos/sensores brillantes
        eye_y = int(target_h * 0.3)
        eye_col = (56, 215, 23) if i == 0 else (211, 75, 84)
        draw.ellipse([20, eye_y, 28, eye_y + 8], fill=eye_col)
        draw.ellipse([target_w - 28, eye_y, target_w - 20, eye_y + 8], fill=eye_col)
        frame.save(os.path.join(SPRITES_DIR, f"lexbot10_idle_{i}.png"))
        
    make_hurt_frame(base).save(os.path.join(SPRITES_DIR, "lexbot10_hurt.png"))
    print("LexBot10 sprites listos.")


def procesar_lexbot20(raw_img):
    """
    LexBot20: robot en motocicleta voladora con brazos mecánicos extensibles.
    Ancho objetivo ~150px.
    """
    clean = remove_background(raw_img, is_white=True, tol=35)
    target_w = 150
    target_h = int(target_w * clean.height / clean.width)
    base = clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Motor de moto y propulsor trasero
    for i in range(2):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        flame_len = 12 if i == 0 else 18
        # Llama de propulsión de motocicleta en la parte derecha (hacia atrás)
        draw.polygon([(target_w - 8, int(target_h * 0.7)),
                      (target_w - 8, int(target_h * 0.7) + 12),
                      (target_w + flame_len, int(target_h * 0.7) + 6)], fill=(125, 31, 115, 220))
        draw.polygon([(target_w - 8, int(target_h * 0.7) + 2),
                      (target_w - 8, int(target_h * 0.7) + 10),
                      (target_w + flame_len - 4, int(target_h * 0.7) + 6)], fill=(255, 200, 255, 255))
        frame.save(os.path.join(SPRITES_DIR, f"lexbot20_idle_{i}.png"))
        
    # Puño mecánico de LexBot20 (sprite separado para la extensión de puñetazo)
    fist_img = Image.new("RGBA", (36, 26), (0, 0, 0, 0))
    d_fist = ImageDraw.Draw(fist_img)
    # Puño metálico morado oscuro y gris
    d_fist.rectangle([4, 4, 30, 22], fill=(66, 74, 78, 255))
    d_fist.rectangle([2, 6, 28, 20], fill=(125, 31, 115, 255))
    d_fist.rectangle([0, 8, 8, 18], fill=(56, 215, 23, 255))  # Nudillos energizados
    fist_img.save(os.path.join(SPRITES_DIR, "lexbot20_fist.png"))
    
    make_hurt_frame(base).save(os.path.join(SPRITES_DIR, "lexbot20_hurt.png"))
    print("LexBot20 sprites listos.")


def procesar_misil(raw_img):
    """Misil: vuela hacia la izquierda. Ancho ~60px."""
    clean = remove_background(raw_img, is_white=False, tol=30)
    target_w = 60
    target_h = int(target_w * clean.height / clean.width)
    base = clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Invertir para que la punta apunte a la izquierda y el fuego salga a la derecha
    base = base.transpose(Image.FLIP_LEFT_RIGHT)
    
    for i in range(3):
        frame = base.copy()
        draw = ImageDraw.Draw(frame)
        flame_len = 8 + i * 4
        my = target_h // 2
        # Fuego a la derecha
        draw.polygon([(target_w - 4, my - 5), (target_w - 4, my + 5), (target_w + flame_len, my)], fill=(255, 159, 28, 240))
        draw.polygon([(target_w - 4, my - 2), (target_w - 4, my + 2), (target_w + flame_len - 3, my)], fill=(255, 210, 63, 255))
        frame.save(os.path.join(SPRITES_DIR, f"misil_idle_{i}.png"))
        
    print("Misil sprites listos.")


def procesar_final_boss(raw_img):
    """
    Final Boss: robot gigante. Alto objetivo ~450px.
    Genera:
      - boss_fase1 (piel/armadura completa)
      - boss_fase2 (dañado con chispas y metal expuesto)
      - boss_fase3 (estructura metálica expuesta / robot completo)
      - boss_fist (puño gigante para estirar brazos / rocket punch)
      - boss_hurt (destello blanco)
    """
    clean = remove_background(raw_img, is_white=True, tol=35)
    target_h = 450
    target_w = int(target_h * clean.width / clean.height)
    base = clean.resize((target_w, target_h), Image.Resampling.LANCZOS)
    
    # Fase 1: Armadura completa
    base.save(os.path.join(SPRITES_DIR, "boss_fase1.png"))
    
    # Fase 2: Dañado intermedio (grietas, cables, resplandor de sobrecalentamiento)
    fase2 = base.copy()
    draw2 = ImageDraw.Draw(fase2)
    # Grietas y cables
    for y_crack in range(80, target_h - 80, 50):
        draw2.line([(40, y_crack), (80, y_crack + 15), (60, y_crack + 30)], fill=(57, 255, 20, 240), width=3)
        draw2.line([(100, y_crack + 10), (140, y_crack - 5)], fill=(255, 42, 42, 230), width=2)
    fase2.save(os.path.join(SPRITES_DIR, "boss_fase2.png"))
    
    # Fase 3: Robot interno al descubierto (tonos metálicos oscuros y núcleo brillante)
    arr3 = np.array(base).copy()
    # Desaturar y oscurecer hacia metal crudo
    r, g, b, a = arr3[:, :, 0], arr3[:, :, 1], arr3[:, :, 2], arr3[:, :, 3]
    gray = (0.299 * r + 0.587 * g + 0.114 * b).astype(np.uint8)
    arr3[:, :, 0] = np.clip(gray * 0.8 + 20, 0, 255).astype(np.uint8)
    arr3[:, :, 1] = np.clip(gray * 0.85 + 25, 0, 255).astype(np.uint8)
    arr3[:, :, 2] = np.clip(gray * 0.8 + 20, 0, 255).astype(np.uint8)
    fase3 = Image.fromarray(arr3)
    draw3 = ImageDraw.Draw(fase3)
    # Núcleo brillante en el pecho
    cx, cy = int(target_w * 0.4), int(target_h * 0.45)
    draw3.ellipse([cx - 25, cy - 25, cx + 25, cy + 25], fill=(57, 255, 20, 255))
    draw3.ellipse([cx - 15, cy - 15, cx + 15, cy + 15], fill=(255, 255, 255, 255))
    fase3.save(os.path.join(SPRITES_DIR, "boss_fase3.png"))
    
    # Puño gigante para el ataque de estirar puño (Rocket Punch)
    fist_w, fist_h = 90, 70
    boss_fist = Image.new("RGBA", (fist_w, fist_h), (0, 0, 0, 0))
    d_bfist = ImageDraw.Draw(boss_fist)
    # Armadura de puño
    d_bfist.rounded_rectangle([10, 8, 85, 62], radius=12, fill=(66, 74, 78, 255))
    d_bfist.rounded_rectangle([15, 12, 80, 58], radius=8, fill=(36, 40, 35, 255))
    # Nudillos de acero y propulsor
    for kn in range(14, 58, 12):
        d_bfist.rectangle([2, kn, 12, kn + 8], fill=(57, 255, 20, 255))
    # Llama propulsora trasera del puño
    d_bfist.polygon([(85, 25), (85, 45), (105, 35)], fill=(255, 159, 28, 230))
    boss_fist.save(os.path.join(SPRITES_DIR, "boss_fist.png"))
    
    make_hurt_frame(base).save(os.path.join(SPRITES_DIR, "boss_hurt.png"))
    print("Final Boss sprites listos.")


# ==============================================================================
# 3. GENERACIÓN DE METRÓPOLIS EN PIXEL ART (PARALLAX EN CAPAS)
# ==============================================================================

def generar_metropolis_pixelart():
    """
    Genera las capas de Metrópolis en pixel art con sol brillante de día:
      1. cielo_sol.png: Cielo azul radiante con sol brillante y zona solar.
      2. edificios_lejanos.png: Silueta de torres en azul/dorado lejanos.
      3. edificios_medios.png: Ciudad con edificios altos, coloridos, ventanas y el Daily Planet.
    """
    w, h = 1280, 720
    
    # Capa 1: Cielo con degradado brillante y el Sol radiante de día
    cielo = Image.new("RGBA", (w, h))
    cielo_arr = np.zeros((h, w, 4), dtype=np.uint8)
    
    # Degradado por bandas (pixel art 16-bit): #0177FA a #82B7E8
    top_c = np.array([1, 119, 250])
    bot_c = np.array([130, 183, 232])
    for y in range(h):
        t = y / h
        # Bandas de 8 píxeles para auténtico estilo 16 bits
        t_stepped = (y // 8) / (h // 8)
        col = (1 - t_stepped) * top_c + t_stepped * bot_c
        cielo_arr[y, :, :3] = col.astype(np.uint8)
        cielo_arr[y, :, 3] = 255
    cielo = Image.fromarray(cielo_arr)
    draw_c = ImageDraw.Draw(cielo)
    
    # Sol radiante de día: arriba centrado-derecha (X=850, Y=90)
    sun_x, sun_y = 850, 90
    # Halo brillante exterior
    for r in range(160, 40, -10):
        alpha = int(40 * (1 - r / 160))
        draw_c.ellipse([sun_x - r, sun_y - r, sun_x + r, sun_y + r], fill=(255, 244, 194, alpha))
    # Corona de rayos solares en cruz y diagonales
    ray_len = 140
    for ang in range(0, 360, 30):
        rad = math.radians(ang)
        rx = sun_x + math.cos(rad) * ray_len
        ry = sun_y + math.sin(rad) * ray_len
        draw_c.line([(sun_x, sun_y), (rx, ry)], fill=(255, 230, 128, 80), width=4)
    # Núcleo del sol blanco-dorado
    draw_c.ellipse([sun_x - 45, sun_y - 45, sun_x + 45, sun_y + 45], fill=(255, 244, 194, 255))
    draw_c.ellipse([sun_x - 30, sun_y - 30, sun_x + 30, sun_y + 30], fill=(255, 255, 255, 255))
    
    cielo.save(os.path.join(SPRITES_DIR, "fondo_cielo_sol.png"))
    
    # Capa 2: Edificios lejanos (repetible horizontalmente, 1280x720)
    far = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_far = ImageDraw.Draw(far)
    rng = np.random.RandomState(42)
    # Generar torres delgadas con agujas
    x = 0
    while x < w:
        b_w = rng.randint(40, 90)
        b_h = rng.randint(220, 380)
        col_far = (75 + rng.randint(-10, 15), 97 + rng.randint(-10, 15), 150 + rng.randint(-15, 20), 220)
        draw_far.rectangle([x, h - b_h, x + b_w, h], fill=col_far)
        # Aguja en el techo
        draw_far.line([(x + b_w // 2, h - b_h), (x + b_w // 2, h - b_h - 40)], fill=col_far, width=2)
        x += b_w + rng.randint(4, 18)
    far.save(os.path.join(SPRITES_DIR, "fondo_lejanos.png"))
    
    # Capa 3: Edificios medios y cercanos — Ciudad de Metrópolis vibrante
    mid = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw_mid = ImageDraw.Draw(mid)
    rng2 = np.random.RandomState(1337)
    
    # Paleta de edificios: Dorados (#DDAE5D), Crema (#F2E6B3), Azul moderno (#315892), Acero (#424A4E)
    paleta_edificios = [
        ((221, 174, 93), (180, 140, 70)),   # Dorado art deco
        ((242, 230, 179), (200, 190, 140)), # Crema / mármol
        ((49, 88, 146), (30, 55, 95)),      # Azul Metrópolis
        ((66, 74, 78), (45, 50, 55)),       # Acero moderno
        ((122, 107, 113), (85, 75, 80))     # Titanio
    ]
    
    x = 0
    daily_planet_placed = False
    while x < w:
        b_w = rng2.randint(80, 160)
        b_h = rng2.randint(300, 520)
        b_col, shadow_col = paleta_edificios[rng2.randint(0, len(paleta_edificios))]
        
        # ¿Es el Daily Planet?
        is_planet = (not daily_planet_placed) and (x > 350)
        if is_planet:
            daily_planet_placed = True
            b_h = 560
            b_w = 180
            b_col = (221, 174, 93)  # Dorado majestuoso
            shadow_col = (180, 140, 70)
            
        # Cuerpo del edificio con sombra lateral estilo pixel art
        draw_mid.rectangle([x, h - b_h, x + b_w, h], fill=b_col + (255,))
        draw_mid.rectangle([x + b_w - 18, h - b_h, x + b_w, h], fill=shadow_col + (255,))
        
        # Ventanas iluminadas por el sol brillante
        win_w, win_h = 6, 8
        win_col = (255, 255, 230, 240)
        for wy in range(h - b_h + 20, h - 20, 16):
            for wx in range(x + 12, x + b_w - 24, 14):
                if rng2.rand() > 0.15:
                    draw_mid.rectangle([wx, wy, wx + win_w, wy + win_h], fill=win_col)
                    
        # Corona / Globo del Daily Planet
        if is_planet:
            globe_x = x + b_w // 2
            globe_y = h - b_h - 40
            # Soporte
            draw_mid.rectangle([globe_x - 12, globe_y + 20, globe_x + 12, h - b_h], fill=(180, 140, 70, 255))
            # Globo dorado brillante
            draw_mid.ellipse([globe_x - 38, globe_y - 38, globe_x + 38, globe_y + 38], fill=(245, 197, 24, 255))
            draw_mid.ellipse([globe_x - 30, globe_y - 30, globe_x + 20, globe_y + 20], fill=(255, 240, 150, 255))
            # Anillo ecuatorial del planeta
            draw_mid.ellipse([globe_x - 55, globe_y - 12, globe_x + 55, globe_y + 12], outline=(255, 255, 255, 255), width=4)
        else:
            # Aguja o antena con baliza de advertencia
            ant_h = rng2.randint(15, 35)
            draw_mid.line([(x + b_w // 2, h - b_h), (x + b_w // 2, h - b_h - ant_h)], fill=(255, 255, 255, 255), width=2)
            draw_mid.rectangle([x + b_w // 2 - 2, h - b_h - ant_h - 2, x + b_w // 2 + 2, h - b_h - ant_h + 2], fill=(255, 42, 42, 255))
            
        x += b_w - 6  # Solapamiento suave
        
    mid.save(os.path.join(SPRITES_DIR, "fondo_edificios.png"))
    print("Fondos de Metrópolis generados con éxito.")


# ==============================================================================
# 4. CONVERSIÓN DE MÚSICA Y SÍNTESIS DE EFECTOS DE SONIDO (SFX)
# ==============================================================================

def generar_sfx_wav(filename, samples, sample_rate=44100):
    samples = np.clip(samples, -1.0, 1.0)
    data = (samples * 32767).astype(np.int16)
    with wave.open(filename, 'w') as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sample_rate)
        w.writeframes(data.tobytes())


def construir_efectos_audio():
    sr = 44100
    
    # 1. Láser de Superman (disparo rápido, barrido agudo)
    t = np.linspace(0, 0.16, int(sr * 0.16), False)
    freq = np.linspace(1600, 250, len(t))
    laser = np.sin(2 * np.pi * freq * t) * np.exp(-t * 18)
    generar_sfx_wav(os.path.join(SFX_DIR, "laser.wav"), laser)
    
    # 2. Golpe de Superman (impacto contundente con crujido sónico)
    t_p = np.linspace(0, 0.22, int(sr * 0.22), False)
    thud = np.sin(2 * np.pi * 90 * t_p) * np.exp(-t_p * 20)
    noise = np.random.uniform(-0.6, 0.6, len(t_p)) * np.exp(-t_p * 35)
    punch = thud + noise
    generar_sfx_wav(os.path.join(SFX_DIR, "golpe.wav"), punch)
    
    # 3. Láser enemigo (pulso alienígena sintetizado)
    t_e = np.linspace(0, 0.20, int(sr * 0.20), False)
    freq_e = np.linspace(700, 180, len(t_e))
    laser_e = np.sign(np.sin(2 * np.pi * freq_e * t_e)) * 0.5 * np.exp(-t_e * 14)
    generar_sfx_wav(os.path.join(SFX_DIR, "enemy_laser.wav"), laser_e)
    
    # 4. Explosión (destrucción de robot/misil)
    t_x = np.linspace(0, 0.45, int(sr * 0.45), False)
    noise_x = np.random.uniform(-0.9, 0.9, len(t_x)) * np.exp(-t_x * 7)
    rumble = np.sin(2 * np.pi * 65 * t_x) * np.exp(-t_x * 9)
    explosion = noise_x * 0.7 + rumble * 0.5
    generar_sfx_wav(os.path.join(SFX_DIR, "explosion.wav"), explosion)
    
    # 5. Recarga solar (armonía celestial y zumbido brillante)
    t_s = np.linspace(0, 0.35, int(sr * 0.35), False)
    chord = (np.sin(2 * np.pi * 523.25 * t_s) + 
             np.sin(2 * np.pi * 659.25 * t_s) + 
             np.sin(2 * np.pi * 783.99 * t_s) + 
             np.sin(2 * np.pi * 1046.50 * t_s)) / 4.0
    sun_hum = chord * np.exp(-t_s * 5) * (0.8 + 0.2 * np.sin(2 * np.pi * 15 * t_s))
    generar_sfx_wav(os.path.join(SFX_DIR, "sun_recharge.wav"), sun_hum)
    
    # 6. Puño cohete / estiramiento mecánico del Jefe y LexBot20
    t_r = np.linspace(0, 0.30, int(sr * 0.30), False)
    whoosh = np.sin(2 * np.pi * np.linspace(120, 480, len(t_r)) * t_r) * np.exp(-t_r * 8)
    clank = np.random.uniform(-0.5, 0.5, len(t_r)) * np.exp(-t_r * 25)
    rocket_punch = whoosh * 0.6 + clank * 0.5
    generar_sfx_wav(os.path.join(SFX_DIR, "rocket_punch.wav"), rocket_punch)
    
    # 7. Alerta de Jefe Final
    t_a = np.linspace(0, 0.8, int(sr * 0.8), False)
    siren = np.sin(2 * np.pi * (440 + 220 * np.sin(2 * np.pi * 4 * t_a)) * t_a) * np.exp(-t_a * 1.5)
    generar_sfx_wav(os.path.join(SFX_DIR, "boss_alert.wav"), siren)
    
    print("Efectos de sonido (SFX) generados con éxito.")


def convertir_musica():
    """Convierte la canción original MP4 a OGG Vorbis compatible con Pygame."""
    dst = os.path.join(AUDIO_DIR, "musica_nivel1.ogg")
    if os.path.exists(dst) and os.path.getsize(dst) > 100000:
        print("Música musica_nivel1.ogg ya existe y está lista.")
        return
        
    src = os.path.join(BASE_DIR, "Soaring above the metropolis.ogg")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [ffmpeg, "-y", "-i", src, "-c:a", "libvorbis", "-q:a", "5", dst]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print("Música convertida exitosamente a musica_nivel1.ogg.")
    else:
        print("Error al convertir música:", res.stderr[:300])


# ==============================================================================
# MAIN EJECUTOR
# ==============================================================================

def main():
    print("Iniciando preparación completa de assets...")
    
    # 1. Personajes
    procesar_superman(Image.open(os.path.join(BASE_DIR, "Superman.jpeg")))
    procesar_lexbot1(Image.open(os.path.join(BASE_DIR, "LexBot1.jpeg")))
    procesar_lexbot10(Image.open(os.path.join(BASE_DIR, "LexBot10.jpeg")))
    procesar_lexbot20(Image.open(os.path.join(BASE_DIR, "LexBot20.jpeg")))
    procesar_misil(Image.open(os.path.join(BASE_DIR, "Misil.jpeg")))
    procesar_final_boss(Image.open(os.path.join(BASE_DIR, "FinalBoss.jpeg")))
    
    # 2. Metrópolis en pixel art
    generar_metropolis_pixelart()
    
    # 3. Audio
    convertir_musica()
    construir_efectos_audio()
    
    print("¡Todos los assets han sido preparados y guardados en assets/!")


if __name__ == "__main__":
    main()
