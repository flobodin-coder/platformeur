import pyxel
import time

gravity = 0.5
scroll_x = 0
scroll_border = 64
scroll_y = 0
max_width = 255*8
max_height = 255*8
mode = "menu"

TILE_floor = (0,1)
TILE_floor1 = (1,1)
TILE_floor2 = (2,1)
TILE_floor3 = (0,4)
TILE_floor4 = (1,4)
TILE_floor5 = (2,4)
TILE_floor6 = (5,1)
TILE_floor7 = (5,2)
TILE_floor8 = (6,1)
TILE_floor9 = (6,2)
TILE_floor10 = (4,18)
TILE_floor11 = (5, 18)
TILE_floor12 = (6, 18)
tile_floor13 = (7, 18)
TILE_floor14 = (8, 18)
TILE_floor15 = (6, 17)
TILE_floor16 = (5, 16)
TILE_floor17 = (5, 17)
TILE_floor18 = (6, 15)
TILE_floor19 = (6, 16)

SOLID_TILE = [TILE_floor, TILE_floor1, TILE_floor2, TILE_floor3, TILE_floor4, TILE_floor5, TILE_floor6, TILE_floor7, TILE_floor8, TILE_floor9, TILE_floor10, TILE_floor11, TILE_floor11, TILE_floor12, tile_floor13, TILE_floor1, TILE_floor15, TILE_floor16, TILE_floor17,TILE_floor18, TILE_floor19 ]

shoot = []
enemies_slime1 = []
#joueur#

player = {
    "x" : 10,
    "y" : 245*8,
    "vx" : 2,
    "vy" : 2,
    "vie" : 3,
    "f" : True, #vers la droite
    "move" : False,
    "last_dir" : 1, # prend la variable 0, 1, 2 correspondant respectivement à gauche, pas bouger et droite
    "jump_force" : 6,
    "is_on_floor" : False,
    "invincibilite" : False
}

enemie_slime = {
    "x": 30,
    "y": 252*8,
    "vx": 1,
    "dir": -1,   # -1 gauche / 1 droite
    "alive": True
}

balle = {
    "x" : 10,
    "y" : 245*8,
    "vx" : 2,
    "f" : True, #vers la droite
    "last_dir" : False, #direction de la balle, prend deux argument booléen vu qu'il ne peut pas etre statique
}

enemie_canon = {
    "x" : 10,
    "y" : 245*8,
    "vx" : 2,
    "f" : True, #vers la droite
    "last_dir" : False, #direction de l'enemie, prend deux argument booléen vu qu'il ne peut pas etre statique
}

def player_update():

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

    if pyxel.btn(pyxel.KEY_UP) and player["is_on_floor"] : 
        player["vy"] -= player["jump_force"]
        player["is_on_floor"] = False
    
    if pyxel.btn(pyxel.KEY_SHIFT) and player["last_dir"] == 2:
        player["x"] += 10

    if pyxel.btn(pyxel.KEY_SHIFT) and player["last_dir"] == 0:
        player["x"] -= 10

    player["vy"] += gravity
    player["y"] += player["vy"]

    #detection des tuile en dessous du personnage
    tile_under_left = get_tile(player["x"] + 2, player["y"] + 8)
    tile_under_right= get_tile(player["x"] + 6, player["y"] + 8)

    #collisiosn pied personnage et tuile 
    if tile_under_left in SOLID_TILE or tile_under_right in SOLID_TILE : 
        if player["vy"] > 0 : # si le joueuer tombe
            player["vy"] = 0
            player["y"] = ((player["y"] + 8) // 8) * 8 - 8
            player["is_on_floor"] = True

        else :
            player["is_on_floor"] = False
            
    if player["vie"] <= 0:
        mode = "gameover"

def player_draw():

    screnn_x = player["x"] - scroll_x
    screnn_y = player["y"] - scroll_y


    u = 8 if player["f"] else -8

    if player["move"] == True:
        if (pyxel.frame_count // 5) % 2 == 0:
            pyxel.blt(screnn_x, screnn_y, 0, 16, 56, u, 8, 5) #saute 

        else :
            pyxel.blt(screnn_x, screnn_y, 0, 0, 80, u, 8, 5) #vers droite
    else: 
        pyxel.blt(screnn_x, screnn_y, 0, 16, 80, u, 8, 5) #immobile
        
def slime_update():

    if not enemie_slime["alive"]:
        return

    x = enemie_slime["x"]
    y = enemie_slime["y"]
    dir = enemie_slime["dir"]
    speed = enemie_slime["vx"]

    # collision mur devant
    front_tile = get_tile(x + dir*8, y + 4)

    # sol devant
    ground_front = get_tile(x + dir*8, y + 8)

    if front_tile in SOLID_TILE or ground_front not in SOLID_TILE:
        enemie_slime["dir"] *= -1
    else:
        enemie_slime["x"] += speed * dir

def slime_player_collision():

    if not enemie_slime["alive"]:
        return

    px = player["x"]
    py = player["y"]
    ex = enemie_slime["x"]
    ey = enemie_slime["y"]

    if abs(px - ex) < 8 and abs(py - ey) < 8:

        # joueur tombe sur l'ennemi
        if player["vy"] > 0 and py < ey:
            enemie_slime["alive"] = False
            player["vy"] = -4  # rebond
        else:
            if player["invincibilite"] == False:
                player["vie"] -= 1
                player["invincibilite"] = True
            else:
                player["vie"] = player["vie"]

def slime_draw():

    if not enemie_slime["alive"]:
        return

    screen_x = enemie_slime["x"] - scroll_x
    screen_y = enemie_slime["y"] - scroll_y

    pyxel.blt(screen_x, screen_y, 0, 48, 88, 8, 8, 5)

def get_tile(x, y):
    tile_x = x//8
    tile_y = y//8
    return pyxel.tilemaps[0].pget(tile_x, tile_y)

def restart_game():
    global shoot, mode, enemies_slime1, player
    player["x"] = 10
    player["y"] = 245*8
    shoot = []
    enemies_slime1 = []
    mode = "game"

pyxel.init(128, 128, title = "Jeu de plateforme")
pyxel.load("jeu.pyxres")

def update():
    global scroll_x, scroll_y
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
    slime_update()
    slime_player_collision()
    scroll_x = player["x"] - scroll_border
    scroll_x = max(0, min(scroll_x, max_width - 128))
    scroll_y= player["y"] - scroll_border
    scroll_y = max(0, min(scroll_y, max_height - 128))

def draw():
    pyxel.cls(0)
    pyxel.bltm(0, 0, 0, scroll_x, scroll_y, 128, 128)
    if mode == "menu":
        pyxel.text(40, 40, "Ponographx", 7)
        pyxel.text(55, 70, "Space to play", 7)
        return

    if mode == "gameover":
        pyxel.text(62, 40, "GAME OVER", 8)
        pyxel.text(25, 70, "Appuie sur R pour recommencer", 7)
        return
    
    pyxel.text(20, 90, str(player["vie"]), 7)

    player_draw()
    tile_x, tile_y =  get_tile(player["x"], player["y"]+8)
    slime_draw()

pyxel.run(update, draw)