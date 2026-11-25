/**
 * game.js — Motor de juego en HTML5 Canvas para Superman: Nivel 1 (Metrópolis).
 * Réplica exacta y optimizada a 60 FPS del juego en Python / Pygame.
 */

// =============================================================================
// 1. CONFIGURACIÓN Y CONSTANTES
// =============================================================================
const CONFIG = {
  CANVAS_WIDTH: 1280,
  CANVAS_HEIGHT: 720,
  FPS: 60,

  // Superman
  SUPERMAN_MAX_HP: 100,
  SUPERMAN_SPEED: 7.0,
  SUPERMAN_WIDTH: 120,
  SUPERMAN_LASER_CD: 0.25,
  SUPERMAN_LASER_CD_BOSS: 0.08,
  SUPERMAN_LASER_DAMAGE: 2,
  SUPERMAN_LASER_SPEED: 22.0,
  SUPERMAN_PUNCH_CD: 0.35,
  SUPERMAN_PUNCH_DAMAGE: 1,
  SUPERMAN_PUNCH_RANGE: 90,
  SUPERMAN_PUNCH_PUSH: 60,
  SUPERMAN_INVULNERABLE_TIME: 1.0,
  SUPERMAN_SOLAR_HEAL_RATE: 15.0,

  // Enemigos
  MISIL_HP: 1,
  MISIL_SPEED: 9.0,
  MISIL_DAMAGE: 10,
  MISIL_WIDTH: 60,

  LEXBOT1_HP: 2,
  LEXBOT1_SPEED: 2.5,
  LEXBOT1_CD: 2.8,

  LEXBOT10_HP: 6,
  LEXBOT10_SPEED: 3.8,
  LEXBOT10_CD: 1.9,

  LEXBOT20_HP: 12,
  LEXBOT20_SPEED: 4.2,
  LEXBOT20_CD: 1.8,
  LEXBOT20_PUNCH_CD: 3.5,
  LEXBOT20_PUNCH_DAMAGE: 18,

  // Jefe Final
  BOSS_MAX_HP: 70,
  BOSS_PUNCH_DAMAGE: 20,
  BOSS_RAY_DAMAGE: 25,

  // Zona Solar
  SUN_ZONE_TIME: 6.0,

  // Colores principales
  COLORS: {
    RED_CAPE: '#A50E0D',
    RED_LIGHT: '#C71E17',
    BLUE_SUIT: '#315892',
    YELLOW_EMBLEM: '#F5C518',
    GREEN_LASER: '#39FF14',
    RED_SUN_LASER: '#C2185B',
    SUN_GOLD: '#FFE680',
    HP_GREEN: '#3DDC5A',
    HP_YELLOW: '#FFC93C',
    HP_RED: '#E63946'
  }
};


// =============================================================================
// 2. GESTOR DE AUDIO (WEB AUDIO + HTML5 AUDIO)
// =============================================================================
class SoundManager {
  constructor() {
    this.music = new Audio('assets/audio/musica_nivel1.ogg');
    this.music.loop = true;
    this.music.volume = 0.55;
    this.musicStarted = false;

    this.sfxPaths = {
      laser: 'assets/sfx/laser.wav',
      golpe: 'assets/sfx/golpe.wav',
      enemy_laser: 'assets/sfx/enemy_laser.wav',
      explosion: 'assets/sfx/explosion.wav',
      sun_recharge: 'assets/sfx/sun_recharge.wav',
      rocket_punch: 'assets/sfx/rocket_punch.wav',
      boss_alert: 'assets/sfx/boss_alert.wav'
    };

    this.sfxPool = {};
    for (const [key, path] of Object.entries(this.sfxPaths)) {
      this.sfxPool[key] = [];
      for (let i = 0; i < 4; i++) {
        const audio = new Audio(path);
        audio.volume = 0.45;
        this.sfxPool[key].push(audio);
      }
    }
  }

  unlockAudio() {
    if (!this.musicStarted) {
      this.music.play().then(() => {
        this.musicStarted = true;
      }).catch(() => {});
    }
  }

  playMusic() {
    this.music.play().catch(() => {});
  }

  pauseMusic() {
    this.music.pause();
  }

  playSFX(name) {
    if (this.sfxPool[name]) {
      const audioList = this.sfxPool[name];
      for (const a of audioList) {
        if (a.paused || a.ended) {
          a.currentTime = 0;
          a.play().catch(() => {});
          return;
        }
      }
      // Si todos están ocupados, usar el primero
      audioList[0].currentTime = 0;
      audioList[0].play().catch(() => {});
    }
  }
}


// =============================================================================
// 3. CARGADOR DE SPRITES E IMÁGENES
// =============================================================================
class AssetLoader {
  constructor() {
    this.images = {};
    this.loadedCount = 0;
    this.totalCount = 0;
  }

  loadImages(imageMap, onComplete) {
    const keys = Object.keys(imageMap);
    this.totalCount = keys.length;
    if (this.totalCount === 0) {
      if (onComplete) onComplete();
      return;
    }

    for (const key of keys) {
      const img = new Image();
      img.src = imageMap[key];
      img.onload = () => {
        this.loadedCount++;
        if (this.loadedCount === this.totalCount && onComplete) {
          onComplete();
        }
      };
      img.onerror = () => {
        console.warn(`Error al cargar imagen: ${imageMap[key]}`);
        this.loadedCount++;
        if (this.loadedCount === this.totalCount && onComplete) {
          onComplete();
        }
      };
      this.images[key] = img;
    }
  }

  get(key) {
    return this.images[key] || null;
  }
}


// =============================================================================
// 4. SISTEMA DE PARTÍCULAS Y SACUDIDA
// =============================================================================
class Particle {
  constructor(x, y, vx, vy, color, life, size = 6, drag = 0.96) {
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;
    this.color = color;
    this.life = life;
    this.maxLife = life;
    this.size = size;
    this.drag = drag;
  }

  update(dt) {
    this.x += this.vx * (dt * 60);
    this.y += this.vy * (dt * 60);
    this.vx *= this.drag;
    this.vy *= this.drag;
    this.life -= dt;
    return this.life > 0;
  }

  draw(ctx) {
    if (this.life <= 0) return;
    const ratio = this.life / this.maxLife;
    const sz = Math.max(2, Math.floor(this.size * ratio));
    ctx.fillStyle = this.color;
    ctx.fillRect(Math.floor(this.x - sz / 2), Math.floor(this.y - sz / 2), sz, sz);
  }
}

class FloatingText {
  constructor(x, y, text, color = '#FFFFFF', duration = 0.8) {
    this.x = x;
    this.y = y;
    this.text = text;
    this.color = color;
    this.life = duration;
  }

  update(dt) {
    this.y -= 35 * dt;
    this.life -= dt;
    return this.life > 0;
  }

  draw(ctx) {
    if (this.life <= 0) return;
    ctx.font = '12px "Press Start 2P", monospace';
    ctx.fillStyle = '#000000';
    ctx.fillText(this.text, this.x + 1, this.y + 1);
    ctx.fillStyle = this.color;
    ctx.fillText(this.text, this.x, this.y);
  }
}

class ParticleSystem {
  constructor() {
    this.particles = [];
    this.texts = [];
    this.shakeDuration = 0;
    this.shakeIntensity = 0;
  }

  shake(duration = 0.3, intensity = 6.0) {
    this.shakeDuration = duration;
    this.shakeIntensity = intensity;
  }

  getShakeOffset() {
    if (this.shakeDuration > 0) {
      const dx = (Math.random() - 0.5) * 2 * this.shakeIntensity;
      const dy = (Math.random() - 0.5) * 2 * this.shakeIntensity;
      return { x: Math.floor(dx), y: Math.floor(dy) };
    }
    return { x: 0, y: 0 };
  }

  createSparks(x, y, color = '#FFD23F', count = 12) {
    for (let i = 0; i < count; i++) {
      const ang = Math.random() * Math.PI * 2;
      const vel = 3.0 + Math.random() * 5.0;
      const life = 0.15 + Math.random() * 0.2;
      const sz = [4, 6, 8][Math.floor(Math.random() * 3)];
      this.particles.push(new Particle(x, y, Math.cos(ang) * vel, Math.sin(ang) * vel, color, life, sz));
    }
  }

  createExplosion(x, y, big = false) {
    const colors = ['#FFFFFF', '#FFD23F', '#FF9F1C', '#E63946', '#5A5A5A'];
    const count = big ? 45 : 25;
    for (let i = 0; i < count; i++) {
      const ang = Math.random() * Math.PI * 2;
      const vel = 2.0 + Math.random() * (big ? 9.0 : 5.0);
      const col = colors[Math.floor(Math.random() * colors.length)];
      const life = 0.3 + Math.random() * 0.4;
      const sz = big ? 10 : 8;
      this.particles.push(new Particle(x, y, Math.cos(ang) * vel, Math.sin(ang) * vel, col, life, sz, 0.94));
    }
  }

  createSolarHealParticles(rect) {
    for (let i = 0; i < 2; i++) {
      const px = rect.x + Math.random() * rect.w;
      const py = rect.y + 20 + Math.random() * (rect.h - 20);
      const vy = -2.5 - Math.random() * 2.0;
      const col = ['#FFF4C2', '#FFD23F', '#FFFFFF'][Math.floor(Math.random() * 3)];
      this.particles.push(new Particle(px, py, (Math.random() - 0.5) * 0.5, vy, col, 0.4, 5, 0.99));
    }
  }

  addText(x, y, text, color = '#FFFFFF') {
    this.texts.push(new FloatingText(x, y, text, color));
  }

  update(dt) {
    if (this.shakeDuration > 0) {
      this.shakeDuration -= dt;
      if (this.shakeDuration <= 0) this.shakeIntensity = 0;
    }
    this.particles = this.particles.filter(p => p.update(dt));
    this.texts = this.texts.filter(t => t.update(dt));
  }

  draw(ctx) {
    for (const p of this.particles) p.draw(ctx);
    for (const t of this.texts) t.draw(ctx);
  }
}


// =============================================================================
// 5. FONDO DE METRÓPOLIS EN PARALLAX
// =============================================================================
class BackgroundParallax {
  constructor(assets) {
    this.assets = assets;
    this.posLejanos = 0;
    this.posEdificios = 0;
    this.velLejanos = 0.8;
    this.velEdificios = 2.4;

    this.sunActive = false;
    this.sunPermanent = false;
    this.sunTimer = 0;
    this.pulseAnim = 0;

    this.clouds = [
      { x: 100, y: 80, vel: 0.5, w: 110, h: 35 },
      { x: 480, y: 140, vel: 0.7, w: 140, h: 45 },
      { x: 920, y: 60, vel: 0.4, w: 90, h: 30 },
      { x: 1280, y: 110, vel: 0.6, w: 130, h: 40 }
    ];
  }

  activateSunZone(permanent = false) {
    this.sunActive = true;
    this.sunPermanent = permanent;
    this.sunTimer = CONFIG.SUN_ZONE_TIME;
  }

  deactivateSunZone() {
    if (!this.sunPermanent) {
      this.sunActive = false;
    }
  }

  isInSunZone(rectSuperman) {
    if (!this.sunActive) return false;
    return rectSuperman.y <= 160 && (rectSuperman.x + rectSuperman.w) >= 400;
  }

  update(dt) {
    this.pulseAnim += dt * 3.0;
    this.posLejanos = (this.posLejanos + this.velLejanos) % CONFIG.CANVAS_WIDTH;
    this.posEdificios = (this.posEdificios + this.velEdificios) % CONFIG.CANVAS_WIDTH;

    for (const c of this.clouds) {
      c.x -= c.vel;
      if (c.x + c.w < 0) c.x = CONFIG.CANVAS_WIDTH + 20;
    }

    if (this.sunActive && !this.sunPermanent) {
      this.sunTimer -= dt;
      if (this.sunTimer <= 0) this.sunActive = false;
    }
  }

  draw(ctx) {
    const cielo = this.assets.get('fondo_cielo_sol');
    const lejanos = this.assets.get('fondo_lejanos');
    const edificios = this.assets.get('fondo_edificios');

    // 1. Cielo y Sol
    if (cielo) {
      ctx.drawImage(cielo, 0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
    } else {
      ctx.fillStyle = '#0177FA';
      ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
    }

    // Resplandor del Sol
    if (this.sunActive) {
      const sunX = 850, sunY = 90;
      const pulso = Math.sin(this.pulseAnim) * 10;
      ctx.save();
      ctx.fillStyle = 'rgba(255, 230, 128, 0.25)';
      ctx.beginPath();
      ctx.arc(sunX, sunY, 130 + pulso, 0, Math.PI * 2);
      ctx.fill();

      // Rayos descendentes
      for (let ox = 450; ox < 1200; ox += 140) {
        ctx.fillStyle = 'rgba(255, 244, 194, 0.18)';
        ctx.fillRect(ox, 0, 4, 180);
      }
      ctx.restore();
    }

    // 2. Nubes
    ctx.fillStyle = 'rgba(255, 255, 255, 0.85)';
    for (const c of this.clouds) {
      ctx.fillRect(Math.floor(c.x), Math.floor(c.y + 8), c.w, c.h - 8);
      ctx.fillRect(Math.floor(c.x + 15), Math.floor(c.y), c.w - 30, c.h);
    }

    // 3. Edificios Lejanos
    if (lejanos) {
      const x1 = -Math.floor(this.posLejanos);
      ctx.drawImage(lejanos, x1, 0);
      ctx.drawImage(lejanos, x1 + CONFIG.CANVAS_WIDTH, 0);
    }

    // 4. Edificios Medios (Daily Planet)
    if (edificios) {
      const x2 = -Math.floor(this.posEdificios);
      ctx.drawImage(edificios, x2, 0);
      ctx.drawImage(edificios, x2 + CONFIG.CANVAS_WIDTH, 0);
    }
  }
}


// =============================================================================
// 6. PROYECTILES
// =============================================================================
class SupermanLaser {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.w = 36;
    this.h = 6;
    this.vx = CONFIG.SUPERMAN_LASER_SPEED;
    this.damage = CONFIG.SUPERMAN_LASER_DAMAGE;
    this.active = true;
  }

  get rect() {
    return { x: this.x, y: this.y, w: this.w, h: this.h };
  }

  update(dt) {
    this.x += this.vx * (dt * 60);
    if (this.x > CONFIG.CANVAS_WIDTH) this.active = false;
  }

  draw(ctx) {
    ctx.fillStyle = CONFIG.COLORS.RED_LIGHT;
    ctx.fillRect(this.x - 2, this.y - 2, this.w + 4, this.h + 4);
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(this.x, this.y, this.w, this.h);
  }
}

class EnemyLaser {
  constructor(x, y, isRedSun = false) {
    this.x = x;
    this.y = y;
    this.r = 7;
    this.vx = -11.0;
    this.damage = isRedSun ? 8 : 5;
    this.isRedSun = isRedSun;
    this.active = true;
  }

  get rect() {
    return { x: this.x - this.r, y: this.y - this.r, w: this.r * 2, h: this.r * 2 };
  }

  update(dt) {
    this.x += this.vx * (dt * 60);
    if (this.x < -20) this.active = false;
  }

  draw(ctx) {
    ctx.fillStyle = this.isRedSun ? CONFIG.COLORS.RED_SUN_LASER : CONFIG.COLORS.GREEN_LASER;
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r + 3, 0, Math.PI * 2);
    ctx.fill();

    ctx.fillStyle = '#FFFFFF';
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.r - 2, 0, Math.PI * 2);
    ctx.fill();
  }
}


// =============================================================================
// 7. SUPERMAN (JUGADOR)
// =============================================================================
class Superman {
  constructor(assets, sound, effects) {
    this.assets = assets;
    this.sound = sound;
    this.effects = effects;

    this.x = 150;
    this.y = 300;
    this.w = CONFIG.SUPERMAN_WIDTH;
    this.h = 157;
    this.hp = CONFIG.SUPERMAN_MAX_HP;
    this.maxHp = CONFIG.SUPERMAN_MAX_HP;

    this.invulnerableTime = 0;
    this.laserCooldown = 0;
    this.punchCooldown = 0;
    this.animPunchTime = 0;
    this.animLaserTime = 0;
    this.sunSoundTime = 0;

    this.frameIdx = 0;
    this.lasers = [];
    this.punchActive = false;
    this.rectPunch = null;
  }

  get rect() {
    return { x: this.x + 15, y: this.y + 10, w: this.w * 0.75, h: this.h * 0.8 };
  }

  handleInput(input, isBossActive) {
    let dx = 0, dy = 0;
    if (input.up) dy -= CONFIG.SUPERMAN_SPEED;
    if (input.down) dy += CONFIG.SUPERMAN_SPEED;
    if (input.left) dx -= CONFIG.SUPERMAN_SPEED;
    if (input.right) dx += CONFIG.SUPERMAN_SPEED;

    if (dx !== 0 && dy !== 0) {
      dx *= 0.7071;
      dy *= 0.7071;
    }

    this.x = Math.max(10, Math.min(CONFIG.CANVAS_WIDTH - this.w - 10, this.x + dx));
    this.y = Math.max(10, Math.min(CONFIG.CANVAS_HEIGHT - this.h - 10, this.y + dy));

    // Láser con Espacio
    const maxCD = isBossActive ? CONFIG.SUPERMAN_LASER_CD_BOSS : CONFIG.SUPERMAN_LASER_CD;
    if (input.laser && this.laserCooldown <= 0) {
      this.fireLaser();
      this.laserCooldown = maxCD;
    }

    // Golpe con X
    if (input.punch && this.punchCooldown <= 0) {
      this.executePunch();
      this.punchCooldown = CONFIG.SUPERMAN_PUNCH_CD;
    }
  }

  fireLaser() {
    const eyeX = this.x + this.w * 0.75;
    const eyeY1 = this.y + this.h * 0.22;
    const eyeY2 = this.y + this.h * 0.26;
    this.lasers.push(new SupermanLaser(eyeX, eyeY1));
    this.lasers.push(new SupermanLaser(eyeX, eyeY2));
    this.animLaserTime = 0.18;
    this.sound.playSFX('laser');
  }

  executePunch() {
    this.animPunchTime = 0.24;
    this.punchActive = true;
    this.rectPunch = {
      x: this.x + this.w * 0.7,
      y: this.y + this.h * 0.2,
      w: CONFIG.SUPERMAN_PUNCH_RANGE,
      h: this.h * 0.6
    };
    this.sound.playSFX('golpe');
  }

  takeDamage(amount) {
    if (this.invulnerableTime > 0) return false;
    this.hp = Math.max(0, this.hp - amount);
    this.invulnerableTime = CONFIG.SUPERMAN_INVULNERABLE_TIME;
    this.effects.shake(0.25, 5.0);
    this.effects.createSparks(this.rect.x + this.rect.w / 2, this.rect.y + this.rect.h / 2, CONFIG.COLORS.RED_LIGHT, 14);
    this.effects.addText(this.rect.x + 20, this.rect.y - 10, `-${amount} HP`, CONFIG.COLORS.HP_RED);
    return true;
  }

  rechargeSolar(dt) {
    if (this.hp < this.maxHp) {
      this.hp = Math.min(this.maxHp, this.hp + CONFIG.SUPERMAN_SOLAR_HEAL_RATE * dt);
      this.effects.createSolarHealParticles(this.rect);
      this.sunSoundTime -= dt;
      if (this.sunSoundTime <= 0) {
        this.sound.playSFX('sun_recharge');
        this.sunSoundTime = 0.4;
        this.effects.addText(this.rect.x + 20, this.rect.y - 12, '+SOLAR', CONFIG.COLORS.YELLOW_EMBLEM);
      }
    }
  }

  update(dt) {
    if (this.invulnerableTime > 0) this.invulnerableTime -= dt;
    if (this.laserCooldown > 0) this.laserCooldown -= dt;
    if (this.punchCooldown > 0) this.punchCooldown -= dt;
    if (this.animLaserTime > 0) this.animLaserTime -= dt;

    if (this.animPunchTime > 0) {
      this.animPunchTime -= dt;
      if (this.animPunchTime <= 0) {
        this.punchActive = false;
        this.rectPunch = null;
      }
    }

    this.frameIdx = (this.frameIdx + 6.0 * dt) % 4;
    this.lasers.forEach(l => l.update(dt));
    this.lasers = this.lasers.filter(l => l.active);
  }

  draw(ctx) {
    // Parpadeo de invulnerabilidad
    if (this.invulnerableTime > 0 && Math.floor(this.invulnerableTime * 16) % 2 === 0) {
      // Invisible este frame
    } else {
      let spriteKey = `superman_idle_${Math.floor(this.frameIdx)}`;
      if (this.animPunchTime > 0) spriteKey = 'superman_punch';
      else if (this.animLaserTime > 0) spriteKey = 'superman_laser';
      else if (this.invulnerableTime > 0) spriteKey = 'superman_hurt';

      const sprite = this.assets.get(spriteKey) || this.assets.get('superman_base');
      if (sprite) {
        ctx.drawImage(sprite, Math.floor(this.x), Math.floor(this.y));
      } else {
        ctx.fillStyle = CONFIG.COLORS.BLUE_SUIT;
        ctx.fillRect(this.x, this.y, this.w, this.h);
      }
    }

    // Proyectiles láser
    this.lasers.forEach(l => l.draw(ctx));
  }
}


// =============================================================================
// 8. ENEMIGOS (MISIL, LEXBOT1, LEXBOT10, LEXBOT20)
// =============================================================================
class Misil {
  constructor(assets, x, y) {
    this.assets = assets;
    this.x = x;
    this.y = y;
    this.w = CONFIG.MISIL_WIDTH;
    this.h = 21;
    this.hp = CONFIG.MISIL_HP;
    this.vx = -CONFIG.MISIL_SPEED;
    this.damage = CONFIG.MISIL_DAMAGE;
    this.active = true;
    this.frameIdx = 0;
  }

  get rect() {
    return { x: this.x, y: this.y, w: this.w, h: this.h };
  }

  takeDamage(amount) {
    this.hp -= amount;
    if (this.hp <= 0) {
      this.active = false;
      return true;
    }
    return false;
  }

  update(dt) {
    this.x += this.vx * (dt * 60);
    this.frameIdx = (this.frameIdx + 12.0 * dt) % 3;
    if (this.x < -this.w - 50) this.active = false;
  }

  draw(ctx) {
    const sprite = this.assets.get(`misil_idle_${Math.floor(this.frameIdx)}`);
    if (sprite) {
      ctx.drawImage(sprite, Math.floor(this.x), Math.floor(this.y));
    }
  }
}

class LexBot1 {
  constructor(assets, sound, x, y) {
    this.assets = assets;
    this.sound = sound;
    this.x = x;
    this.y = y;
    this.baseY = y;
    this.w = 80;
    this.h = 50;
    this.hp = CONFIG.LEXBOT1_HP;
    this.vx = -CONFIG.LEXBOT1_SPEED;
    this.damageContact = 5;
    this.active = true;
    this.shootCD = 1.0 + Math.random() * CONFIG.LEXBOT1_CD;
    this.floatTime = Math.random() * Math.PI * 2;
    this.hurtTime = 0;
  }

  get rect() {
    return { x: this.x, y: this.y, w: this.w, h: this.h };
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.hurtTime = 0.12;
    if (this.hp <= 0) {
      this.active = false;
      return true;
    }
    return false;
  }

  push(dist) {
    this.x = Math.min(CONFIG.CANVAS_WIDTH - this.w, this.x + dist);
  }

  update(dt, enemyLasers) {
    this.floatTime += dt * 3.0;
    this.y = this.baseY + Math.sin(this.floatTime) * 25.0;

    if (this.x > 820) {
      this.x += this.vx * (dt * 60);
    } else {
      this.x += Math.cos(this.floatTime * 0.5) * 0.5;
    }

    if (this.hurtTime > 0) this.hurtTime -= dt;

    this.shootCD -= dt;
    if (this.shootCD <= 0) {
      const isRed = Math.random() < 0.35;
      enemyLasers.push(new EnemyLaser(this.x, this.y + this.h * 0.5, isRed));
      this.sound.playSFX('enemy_laser');
      this.shootCD = CONFIG.LEXBOT1_CD + (Math.random() - 0.5);
    }
  }

  draw(ctx) {
    let spriteKey = `lexbot1_idle_${Math.floor(this.floatTime * 4) % 2}`;
    if (this.hurtTime > 0) spriteKey = 'lexbot1_hurt';
    const sprite = this.assets.get(spriteKey);
    if (sprite) {
      ctx.drawImage(sprite, Math.floor(this.x), Math.floor(this.y));
    }
  }
}

class LexBot10 {
  constructor(assets, sound, x, y) {
    this.assets = assets;
    this.sound = sound;
    this.x = x;
    this.y = y;
    this.baseY = y;
    this.w = 110;
    this.h = 101;
    this.hp = CONFIG.LEXBOT10_HP;
    this.vx = -CONFIG.LEXBOT10_SPEED;
    this.damageContact = 10;
    this.active = true;
    this.shootCD = 0.8 + Math.random() * CONFIG.LEXBOT10_CD;
    this.floatTime = Math.random() * Math.PI * 2;
    this.hurtTime = 0;
    this.altChangeTimer = 2.0;
  }

  get rect() {
    return { x: this.x, y: this.y, w: this.w, h: this.h };
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.hurtTime = 0.12;
    if (this.hp <= 0) {
      this.active = false;
      return true;
    }
    return false;
  }

  push(dist) {
    this.x = Math.min(CONFIG.CANVAS_WIDTH - this.w, this.x + dist);
  }

  update(dt, enemyLasers) {
    this.floatTime += dt * 4.0;
    this.altChangeTimer -= dt;
    if (this.altChangeTimer <= 0) {
      this.baseY = 120 + Math.random() * (CONFIG.CANVAS_HEIGHT - this.h - 180);
      this.altChangeTimer = 2.0 + Math.random() * 2.0;
    }
    this.y += (this.baseY - this.y) * 0.05;

    if (this.x > 750) {
      this.x += this.vx * (dt * 60);
    } else {
      this.x += Math.sin(this.floatTime * 0.8) * 1.2;
    }

    if (this.hurtTime > 0) this.hurtTime -= dt;

    this.shootCD -= dt;
    if (this.shootCD <= 0) {
      const isRed = Math.random() < 0.5;
      enemyLasers.push(new EnemyLaser(this.x, this.y + 25, isRed));
      enemyLasers.push(new EnemyLaser(this.x, this.y + this.h - 25, isRed));
      this.sound.playSFX('enemy_laser');
      this.shootCD = CONFIG.LEXBOT10_CD + (Math.random() - 0.5) * 0.4;
    }
  }

  draw(ctx) {
    let spriteKey = `lexbot10_idle_${Math.floor(this.floatTime * 5) % 2}`;
    if (this.hurtTime > 0) spriteKey = 'lexbot10_hurt';
    const sprite = this.assets.get(spriteKey);
    if (sprite) {
      ctx.drawImage(sprite, Math.floor(this.x), Math.floor(this.y));
    }
  }
}

class LexBot20 {
  constructor(assets, sound, x, y) {
    this.assets = assets;
    this.sound = sound;
    this.x = x;
    this.y = y;
    this.w = 150;
    this.h = 85;
    this.hp = CONFIG.LEXBOT20_HP;
    this.vx = -CONFIG.LEXBOT20_SPEED;
    this.damageContact = 15;
    this.active = true;
    this.shootCD = 1.2;
    this.punchCD = CONFIG.LEXBOT20_PUNCH_CD;
    this.hurtTime = 0;
    this.animTime = 0;

    // Brazo mecánico extensible
    this.isPunching = false;
    this.punchReturning = false;
    this.armReach = 0;
    this.maxArmReach = 380;
    this.armSpeed = 650;
    this.rectPunch = null;
  }

  get rect() {
    return { x: this.x, y: this.y, w: this.w, h: this.h };
  }

  takeDamage(amount) {
    this.hp -= amount;
    this.hurtTime = 0.12;
    if (this.hp <= 0) {
      this.active = false;
      return true;
    }
    return false;
  }

  push(dist) {
    this.x = Math.min(CONFIG.CANVAS_WIDTH - this.w, this.x + dist);
  }

  update(dt, superman, enemyLasers) {
    this.animTime += dt * 6.0;

    if (this.x > 680) {
      this.x += this.vx * (dt * 60);
    } else {
      const diffY = (superman.rect.y + superman.rect.h / 2) - (this.y + this.h * 0.5);
      this.y += diffY * 0.03;
    }

    if (this.hurtTime > 0) this.hurtTime -= dt;

    // Disparos
    this.shootCD -= dt;
    if (this.shootCD <= 0 && !this.isPunching) {
      enemyLasers.push(new EnemyLaser(this.x, this.y + 20, true));
      enemyLasers.push(new EnemyLaser(this.x, this.y + this.h - 15, true));
      this.sound.playSFX('enemy_laser');
      this.shootCD = CONFIG.LEXBOT20_CD;
    }

    // Estirar puño mecánico
    this.punchCD -= dt;
    if (this.punchCD <= 0 && !this.isPunching) {
      this.isPunching = true;
      this.punchReturning = false;
      this.armReach = 0;
      this.sound.playSFX('rocket_punch');
    }

    if (this.isPunching) {
      if (!this.punchReturning) {
        this.armReach += this.armSpeed * dt;
        if (this.armReach >= this.maxArmReach) this.punchReturning = true;
      } else {
        this.armReach -= this.armSpeed * dt * 1.2;
        if (this.armReach <= 0) {
          this.armReach = 0;
          this.isPunching = false;
          this.punchCD = CONFIG.LEXBOT20_PUNCH_CD;
          this.rectPunch = null;
        }
      }

      if (this.isPunching && this.armReach > 10) {
        this.rectPunch = {
          x: this.x - this.armReach,
          y: this.y + this.h * 0.35,
          w: 36,
          h: 26
        };
      } else {
        this.rectPunch = null;
      }
    }
  }

  draw(ctx) {
    // Dibujar brazo extensible
    if (this.isPunching && this.armReach > 5) {
      const origX = this.x + 10;
      const origY = this.y + this.h * 0.45;
      const fistX = this.x - this.armReach;

      ctx.strokeStyle = '#424A4E';
      ctx.lineWidth = 6;
      ctx.beginPath();
      ctx.moveTo(origX, origY);
      ctx.lineTo(fistX, origY);
      ctx.stroke();

      const spriteFist = this.assets.get('lexbot20_fist');
      if (spriteFist) {
        ctx.drawImage(spriteFist, Math.floor(fistX), Math.floor(origY - 13));
      }
    }

    let spriteKey = `lexbot20_idle_${Math.floor(this.animTime) % 2}`;
    if (this.hurtTime > 0) spriteKey = 'lexbot20_hurt';
    const sprite = this.assets.get(spriteKey);
    if (sprite) {
      ctx.drawImage(sprite, Math.floor(this.x), Math.floor(this.y));
    }
  }
}


// =============================================================================
// 9. JEFE FINAL (ROBOT GIGANTE)
// =============================================================================
class FinalBoss {
  constructor(assets, sound, effects) {
    this.assets = assets;
    this.sound = sound;
    this.effects = effects;

    this.x = 820;
    this.y = 140;
    this.w = 340;
    this.h = 450;
    this.hp = CONFIG.BOSS_MAX_HP;
    this.maxHp = CONFIG.BOSS_MAX_HP;
    this.phase = 1;
    this.active = true;
    this.defeated = false;

    this.animTime = 0;
    this.hurtTime = 0;
    this.attackTimer = 2.0;

    // 1. Rocket Punch
    this.isPunching = false;
    this.punchReturning = false;
    this.fistDist = 0;
    this.maxFistDist = 780;
    this.fistSpeed = 750;
    this.rectPunch = null;
    this.fistY = 300;

    // 2. Mega Rayo
    this.isChargingRay = false;
    this.chargeRayTimer = 0;
    this.megaRayActive = false;
    this.megaRayTimer = 0;
    this.rectMegaRay = null;

    // 3. Misiles
    this.pendingMissiles = 0;
    this.missileCD = 0;
  }

  get rect() {
    return { x: this.x + 30, y: this.y + 20, w: this.w - 50, h: this.h - 40 };
  }

  takeDamage(amount) {
    this.hp = Math.max(0, this.hp - amount);
    this.hurtTime = 0.08;
    this.effects.createSparks(this.x + 80, this.y + 180, '#FFE680', 6);

    const pct = this.hp / this.maxHp;
    if (pct <= 0.33 && this.phase < 3) {
      this.phase = 3;
      this.effects.shake(0.6, 10.0);
      this.effects.createExplosion(this.x + 100, this.y + 200, true);
      this.effects.addText(this.x - 40, this.y + 60, '¡ARMADURA DESTRUIDA!', CONFIG.COLORS.HP_RED);
    } else if (pct <= 0.66 && this.phase < 2) {
      this.phase = 2;
      this.effects.shake(0.4, 7.0);
      this.effects.createExplosion(this.x + 100, this.y + 160, true);
      this.effects.addText(this.x - 30, this.y + 60, '¡DAÑO CRÍTICO!', CONFIG.COLORS.YELLOW_EMBLEM);
    }

    if (this.hp <= 0) {
      this.defeated = true;
      this.active = false;
      return true;
    }
    return false;
  }

  update(dt, superman, missiles) {
    this.animTime += dt * 3.0;
    this.y = 140 + Math.sin(this.animTime) * 18.0;

    if (this.hurtTime > 0) this.hurtTime -= dt;

    // Mega Rayo
    if (this.isChargingRay) {
      this.chargeRayTimer -= dt;
      this.effects.createSparks(this.x + 50, this.y + 140, CONFIG.COLORS.GREEN_LASER, 4);
      if (this.chargeRayTimer <= 0) {
        this.isChargingRay = false;
        this.megaRayActive = true;
        this.megaRayTimer = 1.1;
        this.sound.playSFX('boss_alert');
        this.effects.shake(0.8, 8.0);
      }
    }

    if (this.megaRayActive) {
      this.megaRayTimer -= dt;
      this.rectMegaRay = { x: 0, y: this.y + 140 - 14, w: this.x + 50, h: 28 };
      if (this.megaRayTimer <= 0) {
        this.megaRayActive = false;
        this.rectMegaRay = null;
      }
    }

    // Misiles
    if (this.pendingMissiles > 0) {
      this.missileCD -= dt;
      if (this.missileCD <= 0) {
        missiles.push(new Misil(this.assets, this.x + 40, this.y + 50 + (this.pendingMissiles * 35)));
        this.sound.playSFX('enemy_laser');
        this.pendingMissiles--;
        this.missileCD = 0.22;
      }
    }

    // Puño Cohete
    if (this.isPunching) {
      if (!this.punchReturning) {
        this.fistDist += this.fistSpeed * dt;
        if (this.fistDist >= this.maxFistDist) this.punchReturning = true;
      } else {
        this.fistDist -= this.fistSpeed * dt * 1.3;
        if (this.fistDist <= 0) {
          this.fistDist = 0;
          this.isPunching = false;
          this.rectPunch = null;
        }
      }

      if (this.isPunching && this.fistDist > 20) {
        this.rectPunch = {
          x: this.x - this.fistDist,
          y: this.fistY - 30,
          w: 90,
          h: 60
        };
      } else {
        this.rectPunch = null;
      }
    }

    // Selección periódica de ataques
    this.attackTimer -= dt;
    const cadencia = this.phase === 1 ? 2.8 : (this.phase === 2 ? 2.1 : 1.5);
    if (this.attackTimer <= 0 && !this.isPunching && !this.isChargingRay && !this.megaRayActive) {
      this.attackTimer = cadencia;
      const opts = ['punio', 'misiles', 'mega_rayo'];
      const choice = opts[Math.floor(Math.random() * opts.length)];

      if (choice === 'punio') {
        this.isPunching = true;
        this.punchReturning = false;
        this.fistDist = 0;
        this.fistY = superman.rect.y + superman.rect.h / 2;
        this.sound.playSFX('rocket_punch');
        this.effects.shake(0.3, 5.0);
      } else if (choice === 'misiles') {
        this.pendingMissiles = this.phase < 3 ? 3 : 5;
        this.missileCD = 0;
      } else if (choice === 'mega_rayo') {
        this.isChargingRay = true;
        this.chargeRayTimer = 0.8;
        this.sound.playSFX('boss_alert');
      }
    }
  }

  draw(ctx) {
    // 1. Mega Rayo
    if (this.megaRayActive && this.rectMegaRay) {
      ctx.fillStyle = this.phase === 3 ? CONFIG.COLORS.RED_SUN_LASER : CONFIG.COLORS.GREEN_LASER;
      ctx.fillRect(this.rectMegaRay.x, this.rectMegaRay.y, this.rectMegaRay.w, this.rectMegaRay.h);
      ctx.fillStyle = '#FFFFFF';
      ctx.fillRect(this.rectMegaRay.x, this.rectMegaRay.y + 6, this.rectMegaRay.w, this.rectMegaRay.h - 12);
    }

    // 2. Puño Cohete
    if (this.isPunching && this.fistDist > 10) {
      const origX = this.x + 60;
      const origY = this.fistY;
      const fistX = this.x - this.fistDist;

      ctx.strokeStyle = '#424A4E';
      ctx.lineWidth = 14;
      ctx.beginPath();
      ctx.moveTo(origX, origY);
      ctx.lineTo(fistX + 50, origY);
      ctx.stroke();

      const spriteFist = this.assets.get('boss_fist');
      if (spriteFist) {
        ctx.drawImage(spriteFist, Math.floor(fistX), Math.floor(origY - 35));
      }
    }

    // 3. Cuerpo del Jefe según Fase
    let spriteKey = `boss_fase${this.phase}`;
    if (this.hurtTime > 0) spriteKey = 'boss_hurt';
    const sprite = this.assets.get(spriteKey) || this.assets.get('boss_fase1');
    if (sprite) {
      ctx.drawImage(sprite, Math.floor(this.x), Math.floor(this.y));
    }
  }
}


// =============================================================================
// 10. GESTOR DE OLEADAS
// =============================================================================
class WaveManager {
  constructor(assets, sound, effects, background) {
    this.assets = assets;
    this.sound = sound;
    this.effects = effects;
    this.background = background;

    this.currentWave = 1;
    this.totalWaves = 6;
    this.state = 'COMBAT'; // 'COMBAT', 'SUN_ZONE', 'VICTORY'

    this.enemies = [];
    this.missiles = [];
    this.enemyLasers = [];
    this.finalBoss = null;

    this.spawnQueue = [];
    this.sunTimer = 0;

    this.waveBanner = '';
    this.waveBannerTime = 0;
    this.tutorialMsg = '';
    this.tutorialMsgTime = 0;

    this.startWave(1);
  }

  startWave(num) {
    this.currentWave = num;
    this.state = 'COMBAT';
    this.spawnQueue = [];
    this.background.deactivateSunZone();

    if (num === 1) {
      this.waveBanner = 'OLEADA 1: TUTORIAL';
      this.waveBannerTime = 3.0;
      this.tutorialMsg = 'FLECHAS/WASD = Volar  |  ESPACIO = Láser  |  X = Golpe';
      this.tutorialMsgTime = 6.0;
      this.enemies.push(new LexBot1(this.assets, this.sound, CONFIG.CANVAS_WIDTH + 40, 300));
    } else if (num === 2) {
      this.waveBanner = 'OLEADA 2: ESCUADRÓN LEXBOT';
      this.waveBannerTime = 2.5;
      this.tutorialMsg = '¡Destrúyelos con tu visión térmica!';
      this.tutorialMsgTime = 4.0;
      const heights = [160, 260, 360, 460, 540];
      heights.forEach((y, i) => {
        this.spawnQueue.push({
          time: i * 0.7,
          spawn: () => this.enemies.push(new LexBot1(this.assets, this.sound, CONFIG.CANVAS_WIDTH + 40, y))
        });
      });
    } else if (num === 3) {
      this.waveBanner = 'OLEADA 3: ¡LLUVIA DE MISILES!';
      this.waveBannerTime = 2.5;
      this.tutorialMsg = 'Usa X para golpear misiles o esquívalos libremente';
      this.tutorialMsgTime = 5.0;
      for (let g = 0; g < 4; g++) {
        const heights = [200, 360, 500];
        heights.forEach((y, i) => {
          this.spawnQueue.push({
            time: g * 1.8 + i * 0.25,
            spawn: () => this.missiles.push(new Misil(this.assets, CONFIG.CANVAS_WIDTH + 40, y))
          });
        });
      }
    } else if (num === 4) {
      this.waveBanner = 'OLEADA 4: LEXBOTS ÉLITE';
      this.waveBannerTime = 2.5;
      this.tutorialMsg = '¡Cuidado con los láseres verdes y de sol rojo!';
      this.tutorialMsgTime = 5.0;
      [200, 340, 480].forEach((y, i) => {
        this.spawnQueue.push({
          time: i * 1.0,
          spawn: () => this.enemies.push(new LexBot10(this.assets, this.sound, CONFIG.CANVAS_WIDTH + 40, y))
        });
      });
    } else if (num === 5) {
      this.waveBanner = 'OLEADA 5: MOTO-BOT PESADO';
      this.waveBannerTime = 2.5;
      this.tutorialMsg = '¡El LexBot20 estira sus puños mecánicos!';
      this.tutorialMsgTime = 5.0;
      this.enemies.push(new LexBot20(this.assets, this.sound, CONFIG.CANVAS_WIDTH + 40, 320));
      this.spawnQueue.push({
        time: 1.2,
        spawn: () => this.enemies.push(new LexBot1(this.assets, this.sound, CONFIG.CANVAS_WIDTH + 40, 180))
      });
      this.spawnQueue.push({
        time: 1.6,
        spawn: () => this.enemies.push(new LexBot1(this.assets, this.sound, CONFIG.CANVAS_WIDTH + 40, 480))
      });
    } else if (num === 6) {
      this.waveBanner = '¡ALERTA: JEFE FINAL ROBOT GIGANTE!';
      this.waveBannerTime = 4.0;
      this.tutorialMsg = '¡Láser sin recarga! Acércate al sol para recargar vida constante';
      this.tutorialMsgTime = 7.0;
      this.sound.playSFX('boss_alert');
      this.effects.shake(1.0, 8.0);
      this.finalBoss = new FinalBoss(this.assets, this.sound, this.effects);
      this.background.activateSunZone(true);
    }
  }

  update(dt, superman) {
    if (this.waveBannerTime > 0) this.waveBannerTime -= dt;
    if (this.tutorialMsgTime > 0) this.tutorialMsgTime -= dt;

    // Spawn diferido
    this.spawnQueue = this.spawnQueue.filter(item => {
      item.time -= dt;
      if (item.time <= 0) {
        item.spawn();
        return false;
      }
      return true;
    });

    // Actualizar entidades
    this.enemies.forEach(e => {
      if (e instanceof LexBot20) e.update(dt, superman, this.enemyLasers);
      else e.update(dt, this.enemyLasers);
    });
    this.enemies = this.enemies.filter(e => e.active);

    this.missiles.forEach(m => m.update(dt));
    this.missiles = this.missiles.filter(m => m.active);

    this.enemyLasers.forEach(l => l.update(dt));
    this.enemyLasers = this.enemyLasers.filter(l => l.active);

    if (this.finalBoss && this.finalBoss.active) {
      this.finalBoss.update(dt, superman, this.missiles);
      if (this.finalBoss.defeated) {
        this.state = 'VICTORY';
        this.waveBanner = '¡METRÓPOLIS ESTÁ A SALVO!';
        this.waveBannerTime = 999;
      }
    }

    // Fin de oleada normal -> activar Zona de Sol
    if (this.state === 'COMBAT' && this.currentWave < 6) {
      if (this.enemies.length === 0 && this.missiles.length === 0 && this.spawnQueue.length === 0) {
        this.state = 'SUN_ZONE';
        this.sunTimer = CONFIG.SUN_ZONE_TIME;
        this.background.activateSunZone(false);
        this.waveBanner = '¡OLEADA COMPLETADA!';
        this.waveBannerTime = 2.0;
        this.tutorialMsg = '☀️ ¡VUELA HACIA EL SOL PARA RECARGAR TU ENERGÍA! ☀️';
        this.tutorialMsgTime = 5.5;
      }
    }

    if (this.state === 'SUN_ZONE') {
      this.sunTimer -= dt;
      if (this.sunTimer <= 0) {
        this.background.deactivateSunZone();
        if (this.currentWave < this.totalWaves) {
          this.startWave(this.currentWave + 1);
        }
      }
    }
  }

  draw(ctx) {
    this.missiles.forEach(m => m.draw(ctx));
    this.enemies.forEach(e => e.draw(ctx));
    if (this.finalBoss && this.finalBoss.active) this.finalBoss.draw(ctx);
    this.enemyLasers.forEach(l => l.draw(ctx));
  }
}


// =============================================================================
// 11. MOTOR PRINCIPAL Y RENDERIZADOR
// =============================================================================
class SupermanGame {
  constructor() {
    this.canvas = document.getElementById('gameCanvas');
    this.ctx = this.canvas.getContext('2d');
    this.ctx.imageSmoothingEnabled = false;

    this.assets = new AssetLoader();
    this.sound = new SoundManager();
    this.effects = new ParticleSystem();

    this.state = 'LOADING'; // 'LOADING', 'TITLE', 'PLAYING', 'PAUSED', 'GAME_OVER', 'VICTORY'
    this.lastTime = performance.now();

    this.input = {
      up: false, down: false, left: false, right: false,
      laser: false, punch: false, pause: false, confirm: false
    };

    this.setupInputs();
    this.loadAssets();
  }

  setupInputs() {
    // Teclado
    window.addEventListener('keydown', (e) => {
      this.sound.unlockAudio();
      switch (e.code) {
        case 'ArrowUp': case 'KeyW': this.input.up = true; break;
        case 'ArrowDown': case 'KeyS': this.input.down = true; break;
        case 'ArrowLeft': case 'KeyA': this.input.left = true; break;
        case 'ArrowRight': case 'KeyD': this.input.right = true; break;
        case 'Space': this.input.laser = true; e.preventDefault(); break;
        case 'KeyX': case 'KeyJ': this.input.punch = true; break;
        case 'KeyP': case 'Escape': this.togglePause(); break;
        case 'Enter': this.handleConfirm(); break;
      }
    });

    window.addEventListener('keyup', (e) => {
      switch (e.code) {
        case 'ArrowUp': case 'KeyW': this.input.up = false; break;
        case 'ArrowDown': case 'KeyS': this.input.down = false; break;
        case 'ArrowLeft': case 'KeyA': this.input.left = false; break;
        case 'ArrowRight': case 'KeyD': this.input.right = false; break;
        case 'Space': this.input.laser = false; break;
        case 'KeyX': case 'KeyJ': this.input.punch = false; break;
      }
    });

    // Controles táctiles
    const bindTouch = (id, prop) => {
      const el = document.getElementById(id);
      if (!el) return;
      const start = (e) => { e.preventDefault(); this.sound.unlockAudio(); this.input[prop] = true; };
      const end = (e) => { e.preventDefault(); this.input[prop] = false; };
      el.addEventListener('touchstart', start, { passive: false });
      el.addEventListener('touchend', end, { passive: false });
      el.addEventListener('mousedown', start);
      el.addEventListener('mouseup', end);
    };

    bindTouch('btn-up', 'up');
    bindTouch('btn-down', 'down');
    bindTouch('btn-left', 'left');
    bindTouch('btn-right', 'right');
    bindTouch('btn-laser', 'laser');
    bindTouch('btn-punch', 'punch');

    this.canvas.addEventListener('click', () => {
      this.sound.unlockAudio();
      if (this.state === 'TITLE' || this.state === 'GAME_OVER' || this.state === 'VICTORY') {
        this.handleConfirm();
      }
    });
  }

  togglePause() {
    if (this.state === 'PLAYING') {
      this.state = 'PAUSED';
      this.sound.pauseMusic();
    } else if (this.state === 'PAUSED') {
      this.state = 'PLAYING';
      this.sound.playMusic();
    }
  }

  handleConfirm() {
    if (this.state === 'TITLE' || this.state === 'GAME_OVER' || this.state === 'VICTORY') {
      this.restartGame();
      this.state = 'PLAYING';
      this.sound.playMusic();
    }
  }

  loadAssets() {
    const sprites = {
      superman_base: 'assets/sprites/superman_base.png',
      superman_idle_0: 'assets/sprites/superman_idle_0.png',
      superman_idle_1: 'assets/sprites/superman_idle_1.png',
      superman_idle_2: 'assets/sprites/superman_idle_2.png',
      superman_idle_3: 'assets/sprites/superman_idle_3.png',
      superman_laser: 'assets/sprites/superman_laser.png',
      superman_punch: 'assets/sprites/superman_punch.png',
      superman_hurt: 'assets/sprites/superman_hurt.png',

      lexbot1_idle_0: 'assets/sprites/lexbot1_idle_0.png',
      lexbot1_idle_1: 'assets/sprites/lexbot1_idle_1.png',
      lexbot1_hurt: 'assets/sprites/lexbot1_hurt.png',

      lexbot10_idle_0: 'assets/sprites/lexbot10_idle_0.png',
      lexbot10_idle_1: 'assets/sprites/lexbot10_idle_1.png',
      lexbot10_hurt: 'assets/sprites/lexbot10_hurt.png',

      lexbot20_idle_0: 'assets/sprites/lexbot20_idle_0.png',
      lexbot20_idle_1: 'assets/sprites/lexbot20_idle_1.png',
      lexbot20_fist: 'assets/sprites/lexbot20_fist.png',
      lexbot20_hurt: 'assets/sprites/lexbot20_hurt.png',

      misil_idle_0: 'assets/sprites/misil_idle_0.png',
      misil_idle_1: 'assets/sprites/misil_idle_1.png',
      misil_idle_2: 'assets/sprites/misil_idle_2.png',

      boss_fase1: 'assets/sprites/boss_fase1.png',
      boss_fase2: 'assets/sprites/boss_fase2.png',
      boss_fase3: 'assets/sprites/boss_fase3.png',
      boss_fist: 'assets/sprites/boss_fist.png',
      boss_hurt: 'assets/sprites/boss_hurt.png',

      fondo_cielo_sol: 'assets/sprites/fondo_cielo_sol.png',
      fondo_lejanos: 'assets/sprites/fondo_lejanos.png',
      fondo_edificios: 'assets/sprites/fondo_edificios.png'
    };

    this.assets.loadImages(sprites, () => {
      this.background = new BackgroundParallax(this.assets);
      this.state = 'TITLE';
      requestAnimationFrame(this.loop.bind(this));
    });
  }

  restartGame() {
    this.superman = new Superman(this.assets, this.sound, this.effects);
    this.waves = new WaveManager(this.assets, this.sound, this.effects, this.background);
    this.effects.particles = [];
    this.effects.texts = [];
    this.background.deactivateSunZone();
  }

  checkAABB(r1, r2) {
    return (
      r1.x < r2.x + r2.w &&
      r1.x + r1.w > r2.x &&
      r1.y < r2.y + r2.h &&
      r1.y + r1.h > r2.y
    );
  }

  checkCollisions(dt) {
    const sm = this.superman;
    const wm = this.waves;
    const eff = this.effects;
    const snd = this.sound;

    // 1. Láser de Superman vs Enemigos, Misiles y Jefe
    sm.lasers.forEach(laser => {
      if (!laser.active) return;

      // Vs Enemigos
      for (const e of wm.enemies) {
        if (e.active && this.checkAABB(laser.rect, e.rect)) {
          laser.active = false;
          const killed = e.takeDamage(laser.damage);
          eff.createSparks(laser.x + laser.w, laser.y, CONFIG.COLORS.RED_LIGHT, 8);
          if (killed) {
            eff.createExplosion(e.rect.x + e.rect.w / 2, e.rect.y + e.rect.h / 2);
            snd.playSFX('explosion');
          }
          break;
        }
      }

      // Vs Misiles
      if (laser.active) {
        for (const m of wm.missiles) {
          if (m.active && this.checkAABB(laser.rect, m.rect)) {
            laser.active = false;
            m.takeDamage(laser.damage);
            eff.createExplosion(m.rect.x + m.rect.w / 2, m.rect.y + m.rect.h / 2);
            snd.playSFX('explosion');
            break;
          }
        }
      }

      // Vs Jefe Final
      if (laser.active && wm.finalBoss && wm.finalBoss.active) {
        if (this.checkAABB(laser.rect, wm.finalBoss.rect)) {
          laser.active = false;
          wm.finalBoss.takeDamage(laser.damage);
        }
      }
    });

    // 2. Golpe de Superman vs Todo
    if (sm.punchActive && sm.rectPunch) {
      // Vs Enemigos
      for (const e of wm.enemies) {
        if (e.active && this.checkAABB(sm.rectPunch, e.rect)) {
          const killed = e.takeDamage(CONFIG.SUPERMAN_PUNCH_DAMAGE);
          e.push(CONFIG.SUPERMAN_PUNCH_PUSH);
          eff.createSparks(e.rect.x + e.rect.w / 2, e.rect.y + e.rect.h / 2, '#FFFFFF', 14);
          eff.addText(e.rect.x + 20, e.rect.y - 15, '¡GOLPE!', CONFIG.COLORS.YELLOW_EMBLEM);
          if (killed) {
            eff.createExplosion(e.rect.x + e.rect.w / 2, e.rect.y + e.rect.h / 2);
            snd.playSFX('explosion');
          }
        }
      }

      // Vs Misiles: ¡Destrucción instantánea sin recibir daño!
      for (const m of wm.missiles) {
        if (m.active && this.checkAABB(sm.rectPunch, m.rect)) {
          m.takeDamage(999);
          eff.createExplosion(m.rect.x + m.rect.w / 2, m.rect.y + m.rect.h / 2);
          eff.addText(m.rect.x + 10, m.rect.y - 10, '¡DESTRUIDO!', CONFIG.COLORS.YELLOW_EMBLEM);
          snd.playSFX('explosion');
        }
      }

      // Vs Jefe Final
      if (wm.finalBoss && wm.finalBoss.active) {
        if (this.checkAABB(sm.rectPunch, wm.finalBoss.rect)) {
          wm.finalBoss.takeDamage(CONFIG.SUPERMAN_PUNCH_DAMAGE);
          eff.createSparks(sm.rectPunch.x + sm.rectPunch.w, sm.rectPunch.y + 20, '#FFFFFF', 10);
        }
      }
    }

    // 3. Láseres enemigos vs Superman
    wm.enemyLasers.forEach(l => {
      if (l.active && this.checkAABB(l.rect, sm.rect)) {
        l.active = false;
        sm.takeDamage(l.damage);
      }
    });

    // 4. Misiles choque vs Superman
    wm.missiles.forEach(m => {
      if (m.active && this.checkAABB(m.rect, sm.rect)) {
        m.takeDamage(999);
        eff.createExplosion(m.rect.x + m.rect.w / 2, m.rect.y + m.rect.h / 2);
        snd.playSFX('explosion');
        sm.takeDamage(m.damage);
      }
    });

    // 5. Contacto enemigos vs Superman
    wm.enemies.forEach(e => {
      if (e.active && this.checkAABB(e.rect, sm.rect)) {
        sm.takeDamage(e.damageContact);
        e.push(80);
      }
      // Puño de LexBot20
      if (e instanceof LexBot20 && e.rectPunch && this.checkAABB(e.rectPunch, sm.rect)) {
        sm.takeDamage(CONFIG.LEXBOT20_PUNCH_DAMAGE);
        eff.shake(0.35, 6.0);
      }
    });

    // 6. Ataques Jefe Final vs Superman
    if (wm.finalBoss && wm.finalBoss.active) {
      const boss = wm.finalBoss;
      if (boss.rectPunch && this.checkAABB(boss.rectPunch, sm.rect)) {
        sm.takeDamage(CONFIG.BOSS_PUNCH_DAMAGE);
        eff.shake(0.45, 8.0);
      }
      if (boss.rectMegaRay && this.checkAABB(boss.rectMegaRay, sm.rect)) {
        sm.takeDamage(CONFIG.BOSS_RAY_DAMAGE * dt);
      }
      if (this.checkAABB(boss.rect, sm.rect)) {
        sm.takeDamage(20);
      }
    }

    // 7. Recarga Solar
    if (this.background.isInSunZone(sm.rect)) {
      sm.rechargeSolar(dt);
    }

    // 8. Game Over y Victoria
    if (sm.hp <= 0) {
      this.state = 'GAME_OVER';
      eff.shake(0.8, 10.0);
    } else if (wm.state === 'VICTORY') {
      this.state = 'VICTORY';
    }
  }

  update(dt) {
    if (this.state === 'TITLE') {
      this.background.update(dt);
    } else if (this.state === 'PLAYING') {
      const isBoss = (this.waves.finalBoss && this.waves.finalBoss.active);
      this.superman.handleInput(this.input, isBoss);
      this.superman.update(dt);
      this.background.update(dt);
      this.waves.update(dt, this.superman);
      this.effects.update(dt);
      this.checkCollisions(dt);
    }
  }

  drawTextWithBorder(text, x, y, font, fillCol, borderCol = '#000000', center = false) {
    this.ctx.font = font;
    this.ctx.textAlign = center ? 'center' : 'left';
    this.ctx.textBaseline = 'middle';

    this.ctx.strokeStyle = borderCol;
    this.ctx.lineWidth = 4;
    this.ctx.strokeText(text, x, y);

    this.ctx.fillStyle = fillCol;
    this.ctx.fillText(text, x, y);
  }

  drawHUD() {
    const sm = this.superman;
    const wm = this.waves;

    // 1. Barra de Vida de Superman
    const bx = 30, by = 35, bw = 280, bh = 20;
    this.drawTextWithBorder('SUPERMAN', bx, by - 14, '12px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM);

    this.ctx.fillStyle = '#1B1825';
    this.ctx.fillRect(bx - 3, by - 3, bw + 6, bh + 6);
    this.ctx.fillStyle = '#282830';
    this.ctx.fillRect(bx, by, bw, bh);

    const pct = Math.max(0, Math.min(1, sm.hp / sm.maxHp));
    const curW = Math.floor(bw * pct);

    let col = CONFIG.COLORS.HP_GREEN;
    if (sm.hp <= 25) col = CONFIG.COLORS.HP_RED;
    else if (sm.hp <= 50) col = CONFIG.COLORS.HP_YELLOW;

    if (curW > 0) {
      this.ctx.fillStyle = col;
      this.ctx.fillRect(bx, by, curW, bh);
    }

    this.drawTextWithBorder(`${Math.floor(sm.hp)} / ${sm.maxHp} HP`, bx + bw + 12, by + 10, '12px "Press Start 2P"', '#FFFFFF');

    // Estado del Sol
    if (this.background.sunActive) {
      const inSun = this.background.isInSunZone(sm.rect);
      const text = inSun ? '☀️ RADIACIÓN SOLAR ABSORBIÉNDOSE (+HP)' : '☀️ ZONA DE SOL ACTIVA: VUELA ARRIBA';
      const textCol = inSun ? CONFIG.COLORS.YELLOW_EMBLEM : '#FFF4C2';
      this.drawTextWithBorder(text, bx, by + 32, '10px "Press Start 2P"', textCol);
    }

    // 2. Barra del Jefe Final
    if (wm.finalBoss && wm.finalBoss.active) {
      const jx = 650, jy = 35, jw = 450, jh = 18;
      this.drawTextWithBorder(`JEFE FINAL: ROBOT GIGANTE (FASE ${wm.finalBoss.phase})`, jx, jy - 14, '11px "Press Start 2P"', '#FF4444');
      this.ctx.fillStyle = '#1B1825';
      this.ctx.fillRect(jx - 3, jy - 3, jw + 6, jh + 6);
      this.ctx.fillStyle = '#252028';
      this.ctx.fillRect(jx, jy, jw, jh);

      const jpct = Math.max(0, wm.finalBoss.hp / wm.finalBoss.maxHp);
      this.ctx.fillStyle = CONFIG.COLORS.GREEN_LASER;
      this.ctx.fillRect(jx, jy, Math.floor(jw * jpct), jh);
    }

    // 3. Banner de Oleada
    if (wm.waveBannerTime > 0) {
      this.drawTextWithBorder(wm.waveBanner, CONFIG.CANVAS_WIDTH / 2, 90, '24px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
    }

    // 4. Mensajes de Tutorial
    if (wm.tutorialMsgTime > 0) {
      const rx = CONFIG.CANVAS_WIDTH / 2 - 420;
      const ry = CONFIG.CANVAS_HEIGHT - 65;
      this.ctx.fillStyle = 'rgba(20, 24, 38, 0.88)';
      this.ctx.fillRect(rx, ry, 840, 45);
      this.ctx.strokeStyle = CONFIG.COLORS.YELLOW_EMBLEM;
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(rx, ry, 840, 45);
      this.drawTextWithBorder(wm.tutorialMsg, CONFIG.CANVAS_WIDTH / 2, ry + 22, '13px "Press Start 2P"', '#FFFFFF', '#000000', true);
    }
  }

  draw() {
    this.ctx.clearRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

    // Sacudida de pantalla
    const shake = this.effects.getShakeOffset();
    this.ctx.save();
    this.ctx.translate(shake.x, shake.y);

    if (this.state === 'TITLE') {
      this.background.draw(this.ctx);
      this.ctx.fillStyle = 'rgba(10, 20, 45, 0.65)';
      this.ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);

      const cx = CONFIG.CANVAS_WIDTH / 2;
      this.drawTextWithBorder('SUPERMAN', cx, 180, '46px "Press Start 2P"', CONFIG.COLORS.RED_LIGHT, '#000000', true);
      this.drawTextWithBorder('NIVEL 1: METRÓPOLIS', cx, 240, '20px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
      this.drawTextWithBorder('TUTORIAL DE VUELO, FUERZA Y RAYO LÁSER', cx, 280, '12px "Press Start 2P"', '#E6F0FF', '#000000', true);

      // Cuadro de controles
      this.ctx.fillStyle = 'rgba(20, 25, 40, 0.85)';
      this.ctx.fillRect(cx - 300, 320, 600, 190);
      this.ctx.strokeStyle = '#5E90BF';
      this.ctx.lineWidth = 2;
      this.ctx.strokeRect(cx - 300, 320, 600, 190);

      this.drawTextWithBorder('CONTROLES:', cx, 350, '13px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
      this.drawTextWithBorder('FLECHAS / WASD -> Volar por Metrópolis', cx - 260, 385, '11px "Press Start 2P"', '#FFFFFF');
      this.drawTextWithBorder('ESPACIO        -> Rayos Láser (Visión Térmica)', cx - 260, 415, '11px "Press Start 2P"', '#FFFFFF');
      this.drawTextWithBorder('TECLA X / J    -> Golpe (Destruye misiles)', cx - 260, 445, '11px "Press Start 2P"', '#FFFFFF');
      this.drawTextWithBorder('SOL ☀️          -> Vuela al sol para curarte', cx - 260, 475, '11px "Press Start 2P"', '#FFE680');

      if (Math.floor(performance.now() / 500) % 2 === 0) {
        this.drawTextWithBorder('>> PRESIONA ENTER O TOCA AQUÍ PARA COMENZAR <<', cx, 560, '15px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
      }
    } else if (this.state === 'PLAYING' || this.state === 'PAUSED' || this.state === 'GAME_OVER' || this.state === 'VICTORY') {
      this.background.draw(this.ctx);
      this.waves.draw(this.ctx);
      this.superman.draw(this.ctx);
      this.effects.draw(this.ctx);

      this.drawHUD();

      if (this.state === 'PAUSED') {
        this.ctx.fillStyle = 'rgba(10, 15, 30, 0.75)';
        this.ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
        this.drawTextWithBorder('JUEGO EN PAUSA', CONFIG.CANVAS_WIDTH / 2, 320, '36px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
        this.drawTextWithBorder('Presiona P o ESC para continuar', CONFIG.CANVAS_WIDTH / 2, 380, '14px "Press Start 2P"', '#FFFFFF', '#000000', true);
      } else if (this.state === 'GAME_OVER') {
        this.ctx.fillStyle = 'rgba(50, 10, 15, 0.85)';
        this.ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
        const cx = CONFIG.CANVAS_WIDTH / 2;
        this.drawTextWithBorder('GAME OVER', cx, 280, '42px "Press Start 2P"', CONFIG.COLORS.HP_RED, '#000000', true);
        this.drawTextWithBorder('Superman ha agotado su energía solar.', cx, 340, '14px "Press Start 2P"', '#FFFFFF', '#000000', true);
        this.drawTextWithBorder('Acércate al sol para recargar energía cuando te hieran.', cx, 385, '11px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
        this.drawTextWithBorder('>> Presiona ENTER o Toca para reintentar <<', cx, 470, '14px "Press Start 2P"', '#FFFFFF', '#000000', true);
      } else if (this.state === 'VICTORY') {
        this.ctx.fillStyle = 'rgba(15, 35, 60, 0.85)';
        this.ctx.fillRect(0, 0, CONFIG.CANVAS_WIDTH, CONFIG.CANVAS_HEIGHT);
        const cx = CONFIG.CANVAS_WIDTH / 2;
        this.drawTextWithBorder('¡VICTORIA HEROICA!', cx, 210, '38px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
        this.drawTextWithBorder('¡El robot gigante de LexCorp ha sido destruido!', cx, 270, '14px "Press Start 2P"', '#FFFFFF', '#000000', true);
        this.drawTextWithBorder('Metrópolis está a salvo y has completado el tutorial.', cx, 310, '12px "Press Start 2P"', '#D0E5FF', '#000000', true);
        this.drawTextWithBorder('Próximamente: Nivel 2', cx, 360, '12px "Press Start 2P"', '#5E90BF', '#000000', true);
        this.drawTextWithBorder('>> Presiona ENTER o Toca para reiniciar <<', cx, 480, '14px "Press Start 2P"', CONFIG.COLORS.YELLOW_EMBLEM, '#000000', true);
      }
    }

    this.ctx.restore();
  }

  loop(currentTime) {
    const dt = Math.min(0.05, (currentTime - this.lastTime) / 1000);
    this.lastTime = currentTime;

    this.update(dt);
    this.draw();

    requestAnimationFrame(this.loop.bind(this));
  }
}

// Iniciar al cargar
window.addEventListener('DOMContentLoaded', () => {
  window.game = new SupermanGame();
});
