import pygame
import random
import math
import os

pygame.init()

pygame.mixer.init()

# -----------------------------
# Screen
# -----------------------------
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Motion Fruit Ninja V3")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# -----------------------------
# Images
# -----------------------------
apple_img = pygame.image.load("images/apple.png")
orange_img = pygame.image.load("images/orange.png")
watermelon_img = pygame.image.load("images/watermelon.png")
bomb_img = pygame.image.load("images/bomb.png")

apple_img = pygame.transform.scale(apple_img, (80, 80))
orange_img = pygame.transform.scale(orange_img, (80, 80))
watermelon_img = pygame.transform.scale(watermelon_img, (80, 80))
bomb_img = pygame.transform.scale(bomb_img, (60, 60))


#slice_sound = pygame.mixer.Sound("sounds/slice.wav")
#bomb_sound = pygame.mixer.Sound("sounds/bomb.wav")
#gameover_sound = pygame.mixer.Sound("sounds/gameover.wav")

# -----------------------------
# Split Fruit Function
# -----------------------------
def split_image(img):
    w, h = img.get_size()

    left = pygame.Surface((w // 2, h), pygame.SRCALPHA)
    right = pygame.Surface((w // 2, h), pygame.SRCALPHA)

    left.blit(img, (0, 0), (0, 0, w // 2, h))
    right.blit(img, (0, 0), (w // 2, 0, w // 2, h))

    return left, right



# -----------------------------
# Fruits
# -----------------------------
fruits = []
fruit_slices = []

particles = []

for i in range(3):

    fruits.append({

        "x": random.randint(100, 700),
        "y": random.randint(HEIGHT + 50, HEIGHT + 250),

        "radius": 40,

        "speed_x": random.choice([-4, -3, 3, 4]),
        "speed_y": random.randint(-18, -14),

        "visible": True,
        "hide_time": 0,

        "image": random.choice([
            apple_img, 
            
            orange_img,
            
            watermelon_img,
        ])
    })

# -----------------------------
# Bomb
# -----------------------------
bomb = {

    "x": random.randint(100, 700),
    "y": -60,

    "radius": 30,

    "speed_x": random.choice([-2, -1,1,2]),
    "speed_y": -5
}
# -----------------------------
# High Score
# -----------------------------
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        high_score = int(f.read())
else:
    high_score = 0
# -----------------------------
# Game Variables
# -----------------------------
score = 0
lives = 3
combo = 0

game_over = False
running = True

prev_mouse_pos = None
current_mouse_pos = None

# -----------------------------
# Game Loop
# -----------------------------
while running:

    clock.tick(60)

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        # Restart Game
        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:

                score = 0
                lives = 3
                game_over = False

                fruit_slices.clear()

                for fruit in fruits:

                    fruit["visible"] = True
                    fruit["x"] = random.randint(100,700)
                    fruit["y"] = HEIGHT + random.randint(50,250)

                    fruit["speed_x"] = random.choice([-4,-3,3,4])
                    fruit["speed_y"] = random.randint(-18,-14)

                bomb["x"] = random.randint(100,700)
                bomb["y"] = -60
                bomb["speed_y"] = -5
                bomb["speed_x"] = random.choice([-2,-1,1,2])

    # -----------------------------
    # Cursor Position
    # -----------------------------
    current_mouse_pos = pygame.mouse.get_pos()

    # Cursor Trail
    screen.fill((255,255,255))

    if prev_mouse_pos is not None:
        pygame.draw.line(
            screen,
            (255,0,0),
            prev_mouse_pos,
            current_mouse_pos,
            6
        )

    prev_mouse_pos = current_mouse_pos
    
    # -----------------------------
    # Cursor Fruit Collision
    # -----------------------------
    if not game_over:

        mx, my = pygame.mouse.get_pos()
        mouse_speed = math.sqrt(
    (current_mouse_pos[0] - prev_mouse_pos[0]) ** 2 +
    (current_mouse_pos[1] - prev_mouse_pos[1]) ** 2
)

        for fruit in fruits:

            if fruit["visible"]:

                distance = math.sqrt(
                    (mx - fruit["x"]) ** 2 +
                    (my - fruit["y"]) ** 2
                )

                if distance <= fruit["radius"] :
                    
                    score += 1

                    score += combo
                    
                    left_img, right_img = split_image(fruit["image"])
                    
                    if score > high_score:
                        high_score = score

                        with open("highscore.txt", "w") as f:
                            f.write(str(high_score))

                    fruit_slices.append({
                        "image": left_img,
                        "x": fruit["x"] - 10,
                        "y": fruit["y"],
                        "vx": -5,
                        "vy": -6,
                        "rotation": -10,
                        "life": 35
                    })

                    fruit_slices.append({
                        "image": right_img,
                        "x": fruit["x"] + 10,
                        "y": fruit["y"],
                        "vx": 5,
                        "vy": -6,
                        "rotation": 10,
                        "life": 35
                    })

                    fruit["visible"] = False
                    fruit["hide_time"] = pygame.time.get_ticks()
                    if fruit["image"] == apple_img:
                        juice_color = (255, 0, 0)

                    elif fruit["image"] == orange_img:
                        juice_color = (255, 165, 0)

                    else:
                        juice_color = (0, 200, 0)
                    for i in range(15):

                        particles.append({

                            "x": fruit["x"],
                            "y": fruit["y"],

                            "vx": random.randint(-6, 6),
                            "vy": random.randint(-8, -2),

                            "radius": random.randint(2, 5),

                            "life": 30,
                            "color": juice_color
                            
                        })

        distance = math.sqrt(
            (mx - bomb["x"]) ** 2 +
            (my - bomb["y"]) ** 2
        )

        if distance <= bomb["radius"]:

            lives -= 1
            
            #bomb_sound.play()

            bomb["x"] = random.randint(100,700)
            bomb["y"] = -60
            bomb["speed_y"] = -16

            if lives <= 0:
                game_over = True
                
                #gameover_sound.play()

    # -----------------------------
    # Respawn Fruits
    # -----------------------------
    for fruit in fruits:

        if not fruit["visible"]:

            if pygame.time.get_ticks() - fruit["hide_time"] > 1000:

                fruit["visible"] = True
                combo = 0
                fruit["x"] = random.randint(100,700)
                fruit["y"] = HEIGHT + random.randint(50,250)

                fruit["speed_x"] = random.choice([-4,-3,3,4])
                fruit["speed_y"] = random.randint(-18,-14)

    # -----------------------------
    # Score
    # -----------------------------
    score_text = font.render(f"Score : {score}", True, (0,0,0))
    screen.blit(score_text, (20,20))

    high_text = font.render(f"High Score : {high_score}", True, (0,0,255))
    screen.blit(high_text, (20,55))

    lives_text = font.render(f"Lives : {lives}", True, (255,0,0))
    screen.blit(lives_text, (620,20))
    
    # -----------------------------
    # Draw Fruits
    # -----------------------------
    for fruit in fruits:

        if fruit["visible"]:

            screen.blit(
                fruit["image"],
                (
                    int(fruit["x"] - 40),
                    int(fruit["y"] - 40)
                )
            )

            if not game_over:

                fruit["x"] += fruit["speed_x"]
                fruit["y"] += fruit["speed_y"]

                # Gravity
                fruit["speed_y"] += 0.4

                if fruit["x"] <= fruit["radius"] or fruit["x"] >= WIDTH - fruit["radius"]:
                    fruit["speed_x"] *= -1

                if fruit["y"] > HEIGHT + 40:

                    fruit["x"] = random.randint(100,700)
                    fruit["y"] = HEIGHT + random.randint(50,250)

                    fruit["speed_x"] = random.choice([-4,-3,3,4])
                    fruit["speed_y"] = random.randint(-18,-14)
                    

    ## -----------------------------
    # Draw Fruit Slice Animation
    # -----------------------------
    for piece in fruit_slices[:]:

        piece["x"] += piece["vx"]
        piece["y"] += piece["vy"]

        piece["vy"] += 0.4
        piece["rotation"] += 8
        piece["life"] -= 1

        img = pygame.transform.rotate(
            piece["image"],
            piece["rotation"]
        )

        rect = img.get_rect(
            center=(piece["x"], piece["y"])
        )

        screen.blit(img, rect)

        if piece["life"] <= 0:
            fruit_slices.remove(piece) 
            
            # -----------------------------
    # Draw Juice Particles
    # -----------------------------
    for particle in particles[:]:

        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]

        particle["vy"] += 0.3
        particle["life"] -= 1

        pygame.draw.circle(
            screen,
            particle["color"],
            (int(particle["x"]), int(particle["y"])),
            particle["radius"]
        )

        if particle["life"] <= 0:
            particles.remove(particle)
    # Draw Bomb

    # -----------------------------
    screen.blit(
        bomb_img,
        (
            int(bomb["x"] - 30),
            int(bomb["y"] - 30)
        )
    )

    if not game_over:

        bomb["x"] += bomb["speed_x"]
        bomb["y"] += bomb["speed_y"]

        bomb["speed_y"] += 0.08

        if bomb["x"] <= bomb["radius"] or bomb["x"] >= WIDTH - bomb["radius"]:
            bomb["speed_x"] *= -1

        if bomb["y"] > HEIGHT + 40:

            bomb["x"] = random.randint(100,700)
            bomb["y"] = -60
            bomb["speed_y"] = -16

    # -----------------------------
    # Game Over
    # -----------------------------
    if game_over:

        game_over_text = font.render(
            "GAME OVER",
            True,
            (255,0,0)
        )

        restart_text = font.render(
            "Press R to Restart",
            True,
            (0,0,255)
        )

        screen.blit(game_over_text, (250,260))
        screen.blit(restart_text, (220,320))

    pygame.display.update()

pygame.quit()