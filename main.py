import pygame
import random
import math
import os
import cv2
import mediapipe as mp

# -----------------------------
# Initialize Pygame
# -----------------------------
pygame.init()
pygame.mixer.init()

# -----------------------------
# Screen Settings
# -----------------------------
WIDTH = 800
HEIGHT = 600

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Motion Fruit Ninja")

clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)

# -----------------------------
# Camera Setup
# -----------------------------
cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

if not cap.isOpened():
    print("Camera Not Found!")
    pygame.quit()
    exit()

# -----------------------------
# MediaPipe Hands
# -----------------------------
mp_hands = mp.solutions.hands

hands = mp_hands.Hands(
    static_image_mode=False,
    model_complexity=1,
    max_num_hands=1,
    min_detection_confidence=0.8,
    min_tracking_confidence=0.8
)

mp_draw = mp.solutions.drawing_utils

# -----------------------------
# Load Images
# -----------------------------
apple_img = pygame.image.load("images/apple.png").convert_alpha()
orange_img = pygame.image.load("images/orange.png").convert_alpha()
watermelon_img = pygame.image.load("images/watermelon.png").convert_alpha()
bomb_img = pygame.image.load("images/bomb.png").convert_alpha()

apple_img = pygame.transform.scale(apple_img, (80, 80))
orange_img = pygame.transform.scale(orange_img, (80, 80))
watermelon_img = pygame.transform.scale(watermelon_img, (80, 80))
bomb_img = pygame.transform.scale(bomb_img, (60, 60))

# -----------------------------
# Load Sounds
# -----------------------------
slice_sound = pygame.mixer.Sound("sounds/slice.mp3")
bomb_sound = pygame.mixer.Sound("sounds/bomb.mp3")
gameover_sound = pygame.mixer.Sound("sounds/gameover.mp3")

pygame.mixer.music.load("sounds/bgmusic.mp3")
pygame.mixer.music.set_volume(0.3)
pygame.mixer.music.play(-1)

# -----------------------------
# Cursor Variables
# -----------------------------
cursor_x = WIDTH // 2
cursor_y = HEIGHT // 2

current_mouse_pos = (cursor_x, cursor_y)
prev_mouse_pos = None

# Cursor Smoothing
SMOOTHING = 0.18


# -----------------------------
# Split Fruit Function
# -----------------------------
def split_image(image):

    width, height = image.get_size()

    left = pygame.Surface((width // 2, height), pygame.SRCALPHA)
    right = pygame.Surface((width // 2, height), pygame.SRCALPHA)

    left.blit(image, (0, 0), (0, 0, width // 2, height))
    right.blit(image, (0, 0), (width // 2, 0, width // 2, height))

    return left, right


# -----------------------------
# Fruits
# -----------------------------
fruits = []

fruit_slices = []

particles = []

for i in range(3):

    fruits.append({

        "x": random.randint(120, 680),

        "y": HEIGHT + random.randint(50, 250),

        "radius": 40,

        "speed_x": random.choice([-4, -3, 3, 4]),

        "speed_y": random.randint(-18, -14),

        "visible": True,

        "hide_time": 0,

        "image": random.choice([
            apple_img,
            orange_img,
            watermelon_img
        ])

    })


# -----------------------------
# Bomb
# -----------------------------
bomb = {

    "x": random.randint(120, 680),

    "y": -60,

    "radius": 30,

    "speed_x": random.choice([-2, -1, 1, 2]),

    "speed_y": -16

}


# -----------------------------
# High Score
# -----------------------------
if os.path.exists("highscore.txt"):

    with open("highscore.txt", "r") as file:

        high_score = int(file.read())

else:

    high_score = 0


# -----------------------------
# Game Variables
# -----------------------------
score = 0

combo = 0

lives = 3

game_over = False

running = True


# -----------------------------
# Game Loop
# -----------------------------
while running:

    clock.tick(60)

    # -----------------------------
    # Camera
    # -----------------------------
    ret, frame = cap.read()

    if not ret:
        continue

    frame = cv2.flip(frame, 1)

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)

    # -----------------------------
    # Hand Detection
    # -----------------------------
    if results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        mp_draw.draw_landmarks(
            frame,
            hand_landmarks,
            mp_hands.HAND_CONNECTIONS
        )

        index_tip = hand_landmarks.landmark[8]

        target_x = int(index_tip.x * WIDTH)
        target_y = int(index_tip.y * HEIGHT)

        cursor_x += (target_x - cursor_x) * 0.20
        cursor_y += (target_y - cursor_y) * 0.20

        current_mouse_pos = (
            cursor_x,
            cursor_y
        )

    cv2.imshow(
        "Hand Tracking",
        frame
    )

    if cv2.waitKey(1) & 0xFF == 27:
        running = False
    # -----------------------------
    # Events
    # -----------------------------
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:

            if event.key == pygame.K_r and game_over:

                score = 0
                combo = 0
                lives = 3
                game_over = False

                pygame.mixer.music.play(-1)

                for fruit in fruits:

                    fruit["visible"] = True
                    fruit["x"] = random.randint(120, 680)
                    fruit["y"] = HEIGHT + random.randint(50, 250)
                    fruit["speed_x"] = random.choice([-4, -3, 3, 4])
                    fruit["speed_y"] = random.randint(-18, -14)

                bomb["x"] = random.randint(120, 680)
                bomb["y"] = -60
                bomb["speed_x"] = random.choice([-2, -1, 1, 2])
                bomb["speed_y"] = -16

                fruit_slices.clear()
                prev_mouse_pos = None

                bomb["speed_x"] = random.choice([-2, -1, 1, 2])
                bomb["speed_y"] = -16
                
                

    # -----------------------------
    # Background
    # -----------------------------
    screen.fill((255, 255, 255))

    # -----------------------------
    # Sword Trail
    # -----------------------------
    pygame.draw.circle(
        screen,
        (0, 0, 255),
        current_mouse_pos,
        12
    )
    # -----------------------------
    if prev_mouse_pos is not None:

        pygame.draw.line(
            screen,
            (255, 0, 0),
            prev_mouse_pos,
            current_mouse_pos,
            6
        )

    

    mouse_speed = 0

    if prev_mouse_pos is not None:

        mouse_speed = math.sqrt(

            (current_mouse_pos[0] -
             prev_mouse_pos[0]) ** 2 +

            (current_mouse_pos[1] -
             prev_mouse_pos[1]) ** 2

        )
    prev_mouse_pos = current_mouse_pos
        
        
        # -----------------------------
    # Fruit Collision
    # -----------------------------
    if not game_over:

        mx, my = current_mouse_pos

        for fruit in fruits:

            if fruit["visible"]:

                distance = math.sqrt(
                    (mx - fruit["x"]) ** 2 +
                    (my - fruit["y"]) ** 2
                )

                if distance <= fruit["radius"] :

                    combo += 1

                    if combo == 1:
                        score += 1

                    elif combo == 2:
                        score += 3

                    else:
                        score += 5

                    slice_sound.play()

                    left_img, right_img = split_image(
                        fruit["image"]
                    )

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

                    if score > high_score:

                        high_score = score

                        with open(
                            "highscore.txt",
                            "w"
                        ) as file:

                            file.write(
                                str(high_score)
                            )

                    fruit["visible"] = False

                    fruit["hide_time"] = pygame.time.get_ticks()

    # -----------------------------
    # Respawn Fruits
    # -----------------------------
    for fruit in fruits:

        if not fruit["visible"]:

            if pygame.time.get_ticks() - fruit["hide_time"] > 1000:

                fruit["visible"] = True

                fruit["x"] = random.randint(
                    120,
                    680
                )

                fruit["y"] = HEIGHT + random.randint(
                    50,
                    250
                )

                fruit["speed_x"] = random.choice(
                    [-4, -3, 3, 4]
                )

                fruit["speed_y"] = random.randint(
                    -18,
                    -14
                )

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

                fruit["speed_y"] += 0.4

                if (
                    fruit["x"] <= fruit["radius"]
                    or
                    fruit["x"] >= WIDTH - fruit["radius"]
                ):

                    fruit["speed_x"] *= -1

                if fruit["y"] > HEIGHT + 40:

                    fruit["x"] = random.randint(
                        120,
                        680
                    )

                    fruit["y"] = HEIGHT + random.randint(
                        50,
                        250
                    )

                    fruit["speed_x"] = random.choice(
                        [-4, -3, 3, 4]
                    )

                    fruit["speed_y"] = random.randint(
                        -18,
                        -14
                    )
                    
                    
                    # -----------------------------
    # Bomb Collision
    # -----------------------------
    distance = math.sqrt(
        (current_mouse_pos[0] - bomb["x"]) ** 2 +
        (current_mouse_pos[1] - bomb["y"]) ** 2
    )

    if distance <= bomb["radius"] :

        bomb_sound.play()

        lives -= 1

        bomb["x"] = random.randint(120, 680)
        bomb["y"] = -60

        if lives <= 0:

            game_over = True

            pygame.mixer.music.stop()

            gameover_sound.play()

    # -----------------------------
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

        if (
            bomb["x"] <= bomb["radius"]
            or
            bomb["x"] >= WIDTH - bomb["radius"]
        ):

            bomb["speed_x"] *= -1

        if bomb["y"] > HEIGHT + 40:

            bomb["x"] = random.randint(120, 680)

            bomb["y"] = -60

            bomb["speed_y"] = -16

    # -----------------------------
    # Fruit Slice Animation
    # -----------------------------
    for piece in fruit_slices[:]:

        piece["x"] += piece["vx"]

        piece["y"] += piece["vy"]

        piece["vy"] += 0.4

        piece["rotation"] += 8

        piece["life"] -= 1

        image = pygame.transform.rotate(
            piece["image"],
            piece["rotation"]
        )

        rect = image.get_rect(
            center=(piece["x"], piece["y"])
        )

        screen.blit(image, rect)

        if piece["life"] <= 0:

            fruit_slices.remove(piece)

    # -----------------------------
    # Score
    # -----------------------------
    score_text = font.render(
        f"Score : {score}",
        True,
        (0, 0, 0)
    )

    screen.blit(score_text, (20, 20))

    high_text = font.render(
        f"High Score : {high_score}",
        True,
        (0, 0, 255)
    )

    screen.blit(high_text, (20, 55))

    lives_text = font.render(
        f"Lives : {lives}",
        True,
        (255, 0, 0)
    )

    screen.blit(lives_text, (620, 20))

    # -----------------------------
    # Game Over
    # -----------------------------
    if game_over:

        over = font.render(
            "GAME OVER",
            True,
            (255, 0, 0)
        )

        restart = font.render(
            "Press R to Restart",
            True,
            (0, 0, 255)
        )

        screen.blit(over, (250, 250))
        screen.blit(restart, (210, 310))

    # -----------------------------
    # FPS
    # -----------------------------
    pygame.display.set_caption(
        f"Motion Fruit Ninja | FPS : {int(clock.get_fps())}"
    )

    pygame.display.flip()

# -----------------------------
# Exit
# -----------------------------
cap.release()

cv2.destroyAllWindows()

pygame.quit()

