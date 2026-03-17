import pyxel
import time

gravity = 0.5
scroll_x = 0
scroll_border = 64
scroll_y = 0
max_width = 255 * 8
max_height = 255 * 8
mode = "menu"

# Tiles
TILE_floor = (0, 1)
TILE_floor1 = (1, 1)
TILE_floor2 = (2, 1)
TILE_floor3 = (0, 4)
TILE_floor4 = (1, 4)
TILE_floor5 = (2, 4)
TILE_floor6 = (5, 1)
TILE_floor7 = (5, 2)
TILE_floor8 = (6, 1)
TILE_floor9 = (6, 2)
TILE_floor10 = (4, 18)
TILE_floor11 = (5, 18)
TILE_floor12 = (6, 18)
tile_floor13 = (7, 18)
TILE_floor14 = (8, 18)
TILE_floor15 = (6, 17)
TILE_floor16 = (5, 16)
TILE_floor17 = (5, 17)
TILE_floor18 = (6, 15)
TILE_floor19 = (6, 16)
TILE_floor20 = (48, 136)

SOLID_TILE = [
    TILE_floor, TILE_floor1, TILE_floor2, TILE_floor3, TILE_floor4, TILE_floor5,
    TILE_floor6, TILE_floor7, TILE_floor8, TILE_floor9, TILE_floor10, TILE_floor11,
    TILE_floor11, TILE_floor12, tile_floor13, TILE_floor1, TILE_floor15, TILE_floor16,
    TILE_floor17, TILE_floor18, TILE_floor19, TILE_floor20
]

# listes
shoot = []
enemies = []
pickups = []   # items like "gun" or "ammo"
doors = []     # doors with target positions

# joueur
player = {
    "x": 10,
    "y": 245 * 8,
    "vx": 2,
    "vy": 2,
    "vie": 3,
    "f": True,  # vers la droite
    "move": False,
    "last_dir": 1,  # 0 left, 1 idle, 2 right
    "jump_force": 6,
    "is_on_floor": False,
    "invincible_until": 0.0,  # timestamp until which invincible
    "has_gun": False,
    "ammo": 0,
    "door_cooldown": 0
}

# helper spawn
def spawn_enemy(x, y, type, **kwargs):
    e = {
        "x": int(x),
        "y": int(y),
        "vx": kwargs.get("vx", 1),
        "vy": 1,
        "dir": kwargs.get("dir", -1),
        "alive": True,
        "anim": 0,
        "type": type,
    }
    # cannon-specific
    if type == "canon":
        e["shoot_interval"] = kwargs.get("shoot_interval", 2.0)  # seconds
        e["last_shot"] = time.time()
    # bullet-specific
    if type == "bullet":
        e["born_time"] = time.time()
        e["lifetime"] = kwargs.get("lifetime", 3.0)
    enemies.append(e)
    return e

def spawn_pickup(x, y, ptype):
    pickups.append({"x": int(x), "y": int(y), "type": ptype})

#   position x et y de la porte, puis l'endroit ou le joueur est teleporter
def spawn_door(x, y, tx, ty):
    doors.append({"x": int(x), "y": int(y), "tx": int(tx), "ty": int(ty)})

# movement and input
def player_update():
    global mode
    player["move"] = False
    player["last_dir"] = 1

    if pyxel.btn(pyxel.KEY_RIGHT):
        player["x"] += player["vx"]
        player["f"] = True
        player["move"] = True
        player["last_dir"] = 2

    if pyxel.btn(pyxel.KEY_LEFT):
        player["x"] -= player["vx"]
        player["f"] = False
        player["move"] = True
        player["last_dir"] = 0

    if pyxel.btn(pyxel.KEY_UP) and player["is_on_floor"]:
        player["vy"] -= player["jump_force"]
        player["is_on_floor"] = False

    if pyxel.btn(pyxel.KEY_SHIFT) and player["last_dir"] == 2:
        player["x"] += 10
    if pyxel.btn(pyxel.KEY_SHIFT) and player["last_dir"] == 0:
        player["x"] -= 10

    # tirer si a l'arme et ammo > 0 : touche X
    if pyxel.btnp(pyxel.KEY_X) and player["has_gun"] and player["ammo"] > 0:
        shoot_player_bullet()
        player["ammo"] -= 1

    player["vy"] += gravity
    player["y"] += player["vy"]

    # detection des tuiles sous le joueur
    tile_under_left = get_tile(player["x"] + 2, player["y"] + 8)
    tile_under_right = get_tile(player["x"] + 6, player["y"] + 8)

    if tile_under_left in SOLID_TILE or tile_under_right in SOLID_TILE:
        if player["vy"] > 0:
            player["vy"] = 0
            player["y"] = ((player["y"] + 8) // 8) * 8 - 8
            player["is_on_floor"] = True
        else:
            player["is_on_floor"] = False

    # si chute sous la map -> restart
    if player["y"] > max_height + 64:
        restart_game()

    # gameover mode
    if player["vie"] <= 0:
        mode = "gameover"

# dessin joueur
def player_draw():
    screnn_x = player["x"] - scroll_x
    screnn_y = player["y"] - scroll_y

    # clignote si invincible (mais pour le moment il clignote tt le temps :)
    if time.time() < player["invincible_until"]:
        if (pyxel.frame_count // 4) % 2 == 0:
            return  # saute un affichage pour clignoter

    u = 8 if player["f"] else -8

    if player["move"]:
        if (pyxel.frame_count // 5) % 2 == 0:
            pyxel.blt(screnn_x, screnn_y, 0, 0, 80, u, 8, 5)
        else:
            pyxel.blt(screnn_x, screnn_y, 0, 0, 80, u, 8, 5)
    else:
        pyxel.blt(screnn_x, screnn_y, 0, 16, 80, u, 8, 5)

# comportements ennemis slime
def slime_behavior(e):
    x = e["x"]
    y = e["y"]
    dir = e["dir"]

    front_tile = get_tile(x + dir * 8, y + 4)
    ground_front = get_tile(x + dir * 8, y + 8)

    if front_tile in SOLID_TILE or ground_front not in SOLID_TILE:
        e["dir"] *= -1
    else:
        e["x"] += e["vx"] * dir

    # animation  (en theorie)
    if pyxel.frame_count % 10 == 0:
        e["anim"] = (e["anim"] + 1) % 2

def bullet_behavior(e):
    # bullet (ennemi) : avance et meurt si touche mur ou dépasse lifetime
    e["x"] += e["vx"] * e["dir"]
    if get_tile(e["x"], e["y"]) in SOLID_TILE:
        e["alive"] = False
    # lifetime check (pour bullets ennemis)
    if "born_time" in e and time.time() - e["born_time"] > e.get("lifetime", 3.0):
        e["alive"] = False

def canon_behavior(e):
    # canons ne bougent pas : tirent des bullets à intervalle
    now = time.time()
    if now - e.get("last_shot", 0) >= e.get("shoot_interval", 2.0):
        # spawn bullet devant la bouche du canon
        dir = e.get("dir", -1)
        bx = e["x"] + dir * 8
        by = e["y"]
        spawn_enemy(bx, by, "bullet", vx=2, dir=dir, lifetime=3.0)
        e["last_shot"] = now

# mise à jour de tous les ennemis
def enemies_update():
    # on parcourt une copie pour pouvoir supprimer en toute sécurité
    for e in enemies[:]:
        if not e["alive"]:
            enemies.remove(e)
            continue

        if e["type"] == "slime":
            slime_behavior(e)
        elif e["type"] == "bullet":
            bullet_behavior(e)
        elif e["type"] == "canon":
            canon_behavior(e)

# dessin des ennemis
def enemies_draw():
    for e in enemies:
        if not e["alive"]:
            continue
        screen_x = e["x"] - scroll_x
        screen_y = e["y"] - scroll_y
        if e["type"] == "slime":
            if e["dir"] == 1:
                pyxel.blt(screen_x, screen_y, 0, 48, 88, -8, 8, 5)
            else:
                pyxel.blt(screen_x, screen_y, 0, 48, 88, 8, 8, 5)
        elif e["type"] == "bullet":
            pyxel.blt(screen_x, screen_y, 0, 40, 104, 8, 8, 5)
        elif e["type"] == "canon":
            pyxel.blt(screen_x, screen_y, 0, 56, 80, 8, 8, 5)  # adapte la zone du sprite pour canon

# collision joueur ennemis (gère invincibilité)
def enemies_collision():
    for e in enemies[:]:
        if not e["alive"]:
            continue
        # collision simple par distance
        if abs(player["x"] - e["x"]) < 8 and abs(player["y"] - e["y"]) < 8:
            # si joueur tombe sur l'ennemi -> tue l'ennemi
            if player["vy"] > 0 and player["y"] < e["y"]:
                e["alive"] = False
                player["vy"] = -4
            else:
                # si déjà invincible, ne rien faire
                if time.time() < player["invincible_until"]:
                    continue
                # sinon perdre 1 pv et devenir invincible 2s
                player["vie"] -= 1
                player["invincible_until"] = time.time() + 2.0
                # petit recul
                if e["x"] > player["x"]:
                    player["x"] -= 8
                else:
                    player["x"] += 8

# collision joueur <-> pickups
def pickups_update():
    for p in pickups[:]:
        if abs(player["x"] - p["x"]) < 8 and abs(player["y"] - p["y"]) < 8:
            if p["type"] == "gun":
                player["has_gun"] = True
                player["ammo"] = 5
                pickups.remove(p)
            elif p["type"] == "ammo":
                if player["has_gun"]:
                    player["ammo"] = 5
                    pickups.remove(p)

# portes : interaction
def doors_update():
    if player["door_cooldown"] > 0:
        player["door_cooldown"] -= 1
        return

    for d in doors:
        if abs(player["x"] - d["x"]) < 8 and abs(player["y"] - d["y"]) < 8:
            # appuie sur E pour interagir
            if pyxel.btnp(pyxel.KEY_E):
                player["x"] = d["tx"]
                player["y"] = d["ty"]
                # reset vitesse verticale
                player["vy"] = 0
                player["door_cooldown"] = 30

# spawn d'une balle de joueur (projectile)
def shoot_player_bullet():
    dir = 1 if player["last_dir"] == 2 else -1
    bx = player["x"] + (8 if dir == 1 else -8)
    by = player["y"] + 4
    b = {
        "x": int(bx),
        "y": int(by),
        "vx": 3,
        "dir": dir,
        "type": "player_bullet",
        "alive": True,
        "born_time": time.time(),
        "lifetime": 3.0
    }
    enemies.append(b)  # on met dans enemies pour gérer collisions communes

def player_bullet_behavior(e):
    e["x"] += e["vx"] * e["dir"]
    # détruit si touche un mur
    if get_tile(e["x"], e["y"]) in SOLID_TILE:
        e["alive"] = False
    if time.time() - e.get("born_time", 0) > e.get("lifetime", 3.0):
        e["alive"] = False
    # collision avec ennemis (sauf autres player_bullet)
    for target in enemies[:]:
        if target is e:
            continue
        if not target.get("alive", False):
            continue
        if target.get("type") in ("slime", "canon", "bullet"):
            if abs(e["x"] - target["x"]) < 8 and abs(e["y"] - target["y"]) < 8:
                target["alive"] = False
                e["alive"] = False
                break

# get tile function (comme avant)
def get_tile(x, y):
    tile_x = int(x // 8)
    tile_y = int(y // 8)
    return pyxel.tilemaps[0].pget(tile_x, tile_y)

# restart/reset du jeu
def restart_game():
    global enemies, pickups, doors, mode, player
    player["x"] = 10
    player["y"] = 245 * 8
    player["vy"] = 0
    player["vie"] = 3
    player["has_gun"] = False
    player["ammo"] = 0
    player["invincible_until"] = 0.0
    enemies = []
    pickups = []
    doors = []
    mode = "game"
    # (re-spawn quelques entités d'exemple)
    spawn_enemy(120, 252 * 8, "slime")
    spawn_enemy(200, 245 * 8, "slime")
    spawn_enemy(300, 245 * 8, "canon", dir=-1, shoot_interval=2.0)

    # exemples de pickups et portes (ajuste positions)
    spawn_pickup(150, 245 * 8 - 8, "gun")
    spawn_pickup(220, 245 * 8 - 8, "ammo")
    spawn_door(120, 252 * 8, 120, 252 * 8)  # ex: door teleporte a (60, 240*8)

# initialisation pyxel
pyxel.init(128, 128, title="Jeu de plateforme")
pyxel.load("jeu.pyxres")

def update():
    global scroll_x, scroll_y, mode, doors
    if pyxel.btnp(pyxel.KEY_Q):
        pyxel.quit()

    if mode == "menu":
        if pyxel.btnp(pyxel.KEY_SPACE) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
            restart_game()
        return

    if mode == "gameover":
        if pyxel.btnp(pyxel.KEY_R) or pyxel.btnp(pyxel.GAMEPAD1_BUTTON_START):
            restart_game()
        return

    player_update()
    enemies_update()

    # behaviours for player bullets (in enemies list)
    for e in enemies:
        if e.get("type") == "player_bullet" and e.get("alive", False):
            player_bullet_behavior(e)

    enemies_collision()
    pickups_update()
    doors_update()

    scroll_x = player["x"] - scroll_border
    scroll_x = max(0, min(scroll_x, max_width - 128))
    scroll_y = player["y"] - scroll_border
    scroll_y = max(0, min(scroll_y, max_height - 128))

def draw():
    pyxel.cls(0)
    pyxel.bltm(0, 0, 0, scroll_x, scroll_y, 128, 128)
    if mode == "menu":
        pyxel.text(40, 40, "rUn", 7)
        pyxel.text(55, 70, "Space to play", 7)
        return

    if mode == "gameover":
        pyxel.text(62, 40, "GAME OVER", 8)
        pyxel.text(25, 70, "Appuie sur R pour recommencer", 7)
        return

    # Texte sur l'écrant
    pyxel.text(20, 90, f"Vie: {player['vie']}", 7)
    pyxel.text(20, 98, f"Ammo: {player['ammo'] if player['has_gun'] else '-'}", 7)

    # dessin
    player_draw()
    enemies_draw()

    # dessin pickups
    for p in pickups:
        sx = p["x"] - scroll_x
        sy = p["y"] - scroll_y
        if p["type"] == "gun":
            pyxel.blt(sx, sy, 0, 64, 80, 8, 8, 0)
        elif p["type"] == "ammo":
            pyxel.blt(sx, sy, 0, 72, 80, 8, 8, 0)
            

pyxel.run(update, draw)