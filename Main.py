import pygame
import random
import sys
import math

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rocket vs Aliens - Advanced")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
CYAN = (0, 255, 255)
ORANGE = (255, 165, 0)

# Player setup
player_width = 40
player_height = 60
player_x = WIDTH // 2 - player_width // 2
player_y = HEIGHT - player_height - 20
player_speed = 5
player_level = 1  # Rocket level
max_player_level = 5  # Maximum rocket level

# Ship specifications for each level
ship_specs = {
    1: {"width": 40, "height": 60, "color1": WHITE, "color2": RED, "color3": BLUE, "bullet_count": 1},
    2: {"width": 45, "height": 65, "color1": WHITE, "color2": YELLOW, "color3": BLUE, "bullet_count": 2},
    3: {"width": 50, "height": 70, "color1": WHITE, "color2": GREEN, "color3": YELLOW, "bullet_count": 3},
    4: {"width": 55, "height": 75, "color1": CYAN, "color2": PURPLE, "color3": RED, "bullet_count": 4},
    5: {"width": 60, "height": 80, "color1": YELLOW, "color2": ORANGE, "color3": RED, "bullet_count": 5}
}

# Enemy setup
enemies = []
enemy_spawn_rate = 30  # Lower is faster
enemy_types = {
    "basic": {"width": 50, "height": 40, "speed": 2, "hp": 1, "color": GREEN, "points": 10},
    "speedy": {"width": 40, "height": 35, "speed": 4, "hp": 1, "color": BLUE, "points": 15},
    "tank": {"width": 60, "height": 50, "speed": 1.5, "hp": 3, "color": RED, "points": 20},
    "elite": {"width": 55, "height": 45, "speed": 3, "hp": 2, "color": PURPLE, "points": 25},
    "boss": {"width": 80, "height": 70, "speed": 1, "hp": 10, "color": ORANGE, "points": 50}
}

# Power-up setup
power_ups = []
powerup_types = {
    "rapid_fire": {"width": 25, "height": 25, "color": YELLOW, "duration": 5000},
    "spread_shot": {"width": 25, "height": 25, "color": BLUE, "duration": 8000},
    "shield": {"width": 25, "height": 25, "color": GREEN, "duration": 7000},
    "speed_boost": {"width": 25, "height": 25, "color": CYAN, "duration": 6000}
}
powerup_spawn_rate = 200  # Lower is more frequent

# Bullet setup
bullet_width = 6
bullet_height = 15
bullets = []
bullet_speed = 10
bullet_damage = 1
fire_rate = 300  # Milliseconds between shots
spread_angle = 0  # For spread shots

# Active power-ups
active_power_ups = {
    "rapid_fire": 0,  # End time
    "spread_shot": 0,
    "shield": 0,
    "speed_boost": 0
}

# Game variables
score = 0
game_over = False
level = 1
next_level_score = 100
next_ship_upgrade = 500
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 36)
small_font = pygame.font.SysFont(None, 24)
has_shield = False

# Stars for background
stars = []
for _ in range(100):
    x = random.randint(0, WIDTH)
    y = random.randint(0, HEIGHT)
    stars.append([x, y, random.uniform(0.5, 2)])

def draw_background():
    # Draw stars
    for star in stars:
        pygame.draw.circle(screen, WHITE, (int(star[0]), int(star[1])), int(star[2]))
        # Move stars slowly down
        star[1] += 0.5
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)

def draw_rocket(x, y):
    # Get current ship specs
    specs = ship_specs[player_level]
    w = specs["width"]
    h = specs["height"]
    color1 = specs["color1"]
    color2 = specs["color2"]
    color3 = specs["color3"]
    
    # Rocket body
    pygame.draw.rect(screen, color1, (x + w//8, y + h//4, w - w//4, h - h//4))
    
    # Rocket nose
    pygame.draw.polygon(screen, color2, [(x + w // 2, y), 
                                       (x, y + h // 4), 
                                       (x + w, y + h // 4)])
    
    # Rocket fins
    pygame.draw.polygon(screen, color3, [(x, y + h - h//6), 
                                        (x, y + h), 
                                        (x + w//4, y + h - h//4)])
    pygame.draw.polygon(screen, color3, [(x + w, y + h - h//6), 
                                        (x + w, y + h), 
                                        (x + w - w//4, y + h - h//4)])
    
    # Rocket engine fire
    fire_height = random.randint(15, 25)  # Flicker effect
    pygame.draw.polygon(screen, YELLOW, [(x + w//4, y + h), 
                                        (x + w - w//4, y + h), 
                                        (x + w // 2, y + h + fire_height)])
    
    # Draw shield if active
    if pygame.time.get_ticks() < active_power_ups["shield"]:
        shield_radius = max(w, h)
        shield_surf = pygame.Surface((shield_radius*2, shield_radius*2), pygame.SRCALPHA)
        alpha = 100 + 50 * math.sin(pygame.time.get_ticks() / 200)  # Pulsing effect
        pygame.draw.circle(shield_surf, (100, 200, 255, alpha), (shield_radius, shield_radius), shield_radius)
        screen.blit(shield_surf, (x + w//2 - shield_radius, y + h//2 - shield_radius))

def draw_alien(x, y, type_name):
    alien_type = enemy_types[type_name]
    width = alien_type["width"]
    height = alien_type["height"]
    color = alien_type["color"]
    
    if type_name == "basic":
        # Basic alien (simple green alien)
        pygame.draw.ellipse(screen, color, (x, y + height//3, width, height - height//3))
        pygame.draw.circle(screen, color, (x + width // 2, y + height//4), height//4)
        # Eyes
        pygame.draw.circle(screen, RED, (x + width // 2 - width//6, y + height//5), height//10)
        pygame.draw.circle(screen, RED, (x + width // 2 + width//6, y + height//5), height//10)
        # Antennae
        pygame.draw.line(screen, color, (x + width // 2 - width//10, y + height//10), 
                                    (x + width // 2 - width//5, y - height//5), 2)
        pygame.draw.line(screen, color, (x + width // 2 + width//10, y + height//10), 
                                    (x + width // 2 + width//5, y - height//5), 2)
    
    elif type_name == "speedy":
        # Speedy alien (streamlined)
        pygame.draw.ellipse(screen, color, (x, y, width, height))
        # Eyes
        pygame.draw.circle(screen, YELLOW, (x + width // 2 - width//6, y + height//3), height//10)
        pygame.draw.circle(screen, YELLOW, (x + width // 2 + width//6, y + height//3), height//10)
    
    elif type_name == "tank":
        # Tank alien (larger with armor)
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=10)
        pygame.draw.rect(screen, BLACK, (x + width//6, y + height//6, width - width//3, height - height//3), border_radius=5)
        # Eyes
        pygame.draw.circle(screen, YELLOW, (x + width // 2 - width//6, y + height//3), height//12)
        pygame.draw.circle(screen, YELLOW, (x + width // 2 + width//6, y + height//3), height//12)
        # Armor plates
        for i in range(3):
            pygame.draw.line(screen, WHITE, (x + width//6, y + height//4 + i*height//4),
                                       (x + width - width//6, y + height//4 + i*height//4), 2)
    
    elif type_name == "elite":
        # Elite alien (angular with spikes)
        pygame.draw.polygon(screen, color, [
            (x + width//2, y),
            (x, y + height//2),
            (x + width//2, y + height),
            (x + width, y + height//2)
        ])
        # Eyes
        pygame.draw.circle(screen, WHITE, (x + width // 2 - width//8, y + height//3), height//10)
        pygame.draw.circle(screen, WHITE, (x + width // 2 + width//8, y + height//3), height//10)
        # Spikes
        spike_length = width//4
        pygame.draw.line(screen, YELLOW, (x + width//2, y), (x + width//2, y - spike_length), 3)
        pygame.draw.line(screen, YELLOW, (x, y + height//2), (x - spike_length, y + height//2), 3)
        pygame.draw.line(screen, YELLOW, (x + width, y + height//2), (x + width + spike_length, y + height//2), 3)
    
    elif type_name == "boss":
        # Boss alien (large complex shape)
        # Main body
        pygame.draw.rect(screen, color, (x, y + height//4, width, height - height//4), border_radius=10)
        # Head
        pygame.draw.circle(screen, color, (x + width//2, y + height//4), height//4)
        # Eyes
        eye_radius = height//8
        pygame.draw.circle(screen, RED, (x + width//2 - width//6, y + height//4), eye_radius)
        pygame.draw.circle(screen, RED, (x + width//2 + width//6, y + height//4), eye_radius)
        pygame.draw.circle(screen, BLACK, (x + width//2 - width//6, y + height//4), eye_radius//2)
        pygame.draw.circle(screen, BLACK, (x + width//2 + width//6, y + height//4), eye_radius//2)
        # Armor
        pygame.draw.rect(screen, WHITE, (x + width//4, y + height//2, width//2, height//5), 1)
        # Tentacles
        for i in range(3):
            start_x = x + width//4 + i*width//4
            pygame.draw.line(screen, color, (start_x, y + height), 
                                      (start_x + random.randint(-width//5, width//5), y + height + height//3), 4)

def draw_power_up(x, y, type_name):
    power_type = powerup_types[type_name]
    width = power_type["width"]
    height = power_type["height"]
    color = power_type["color"]
    
    if type_name == "rapid_fire":
        # Draw rapid fire power-up (lightning bolt)
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=5)
        points = [
            (x + width//2, y + height//6),
            (x + width//4, y + height//2),
            (x + width//2, y + height//2),
            (x + width//4, y + height - height//6)
        ]
        pygame.draw.lines(screen, BLACK, False, points, 2)
    
    elif type_name == "spread_shot":
        # Draw spread shot power-up (multiple arrow icon)
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=5)
        # Draw three arrows
        for i in range(3):
            offset = (i - 1) * width//4
            pygame.draw.line(screen, BLACK, (x + width//2 + offset, y + height//4),
                                       (x + width//2 + offset, y + height - height//4), 2)
            pygame.draw.polygon(screen, BLACK, [
                (x + width//2 + offset, y + height//4),
                (x + width//2 + offset - width//8, y + height//2),
                (x + width//2 + offset + width//8, y + height//2)
            ])
            
    elif type_name == "shield":
        # Draw shield power-up (shield icon)
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=5)
        pygame.draw.arc(screen, BLACK, (x + width//6, y + height//6, width - width//3, height - height//3),
                              0, math.pi, 2)
        pygame.draw.line(screen, BLACK, (x + width//6, y + height//2),
                                   (x + width - width//6, y + height//2), 2)
    
    elif type_name == "speed_boost":
        # Draw speed boost power-up (wing icon)
        pygame.draw.rect(screen, color, (x, y, width, height), border_radius=5)
        pygame.draw.polygon(screen, BLACK, [
            (x + width//6, y + height - height//4),
            (x + width//2, y + height//4),
            (x + width - width//6, y + height - height//4)
        ], 2)

def spawn_enemy():
    # Choose enemy type based on current level
    available_types = []
    if level >= 1: available_types.append("basic")
    if level >= 2: available_types.append("speedy")
    if level >= 3: available_types.append("tank")
    if level >= 4: available_types.append("elite")
    
    # Boss appears every 5 levels
    if level % 5 == 0 and random.random() < 0.05:  # 5% chance for boss
        enemy_type = "boss"
    else:
        enemy_type = random.choice(available_types)
    
    enemy_data = enemy_types[enemy_type]
    x = random.randint(0, WIDTH - enemy_data["width"])
    y = random.randint(-100, -enemy_data["height"])
    
    # Store enemy properties: [x, y, type, hp]
    enemies.append([x, y, enemy_type, enemy_data["hp"]])

def spawn_power_up():
    # Choose power-up type randomly
    power_up_type = random.choice(list(powerup_types.keys()))
    power_data = powerup_types[power_up_type]
    
    x = random.randint(0, WIDTH - power_data["width"])
    y = random.randint(-100, -power_data["height"])
    
    # Store power-up properties: [x, y, type]
    power_ups.append([x, y, power_up_type])

def move_enemies():
    for enemy in enemies[:]:
        enemy_type = enemy[2]
        enemy_speed = enemy_types[enemy_type]["speed"]
        
        # Move down
        enemy[1] += enemy_speed
        
        # Add some horizontal movement for certain enemies
        if enemy_type == "speedy" or enemy_type == "elite":
            # Sine wave movement
            enemy[0] += math.sin(pygame.time.get_ticks() / 500) * 2
            
        # Keep in bounds
        enemy[0] = max(0, min(WIDTH - enemy_types[enemy_type]["width"], enemy[0]))
        
        # Remove if off screen
        if enemy[1] > HEIGHT:
            enemies.remove(enemy)

def move_power_ups():
    for power_up in power_ups[:]:
        # Move down slower than enemies
        power_up[1] += 1.5
        
        # Remove if off screen
        if power_up[1] > HEIGHT:
            power_ups.remove(power_up)

def fire_bullet():
    global bullets
    
    specs = ship_specs[player_level]
    bullet_count = specs["bullet_count"]
    current_time = pygame.time.get_ticks()
    
    # Calculate actual fire rate based on power-ups
    actual_fire_rate = fire_rate
    if current_time < active_power_ups["rapid_fire"]:
        actual_fire_rate = fire_rate // 3  # 3x faster firing
    
    # Center position for bullets
    center_x = player_x + specs["width"] // 2 - bullet_width // 2
    
    # Check if spread shot is active
    is_spread = current_time < active_power_ups["spread_shot"]
    
    if is_spread and bullet_count > 1:
        # Fire in a spread pattern
        for i in range(bullet_count):
            if bullet_count > 1:
                angle = (i / (bullet_count - 1) - 0.5) * math.pi / 4  # -π/8 to π/8 radians
            else:
                angle = 0  # Prevent division by zero for single bullet
            
            # Calculate velocity components
            vx = math.sin(angle) * bullet_speed
            vy = -math.cos(angle) * bullet_speed  # Negative because y increases downward
            
            bullets.append([center_x, player_y, vx, vy])
    else:
        # Standard firing pattern based on ship level
        if bullet_count == 1:
            # Single bullet from center
            bullets.append([center_x, player_y, 0, -bullet_speed])
        elif bullet_count == 2:
            # Two bullets side by side
            bullets.append([center_x - bullet_width, player_y, 0, -bullet_speed])
            bullets.append([center_x + bullet_width, player_y, 0, -bullet_speed])
        else:
            # Multiple bullets in row
            spacing = specs["width"] // (bullet_count + 1)
            start_x = player_x + spacing - bullet_width // 2
            
            for i in range(bullet_count):
                bullets.append([start_x + i * spacing, player_y, 0, -bullet_speed])

def draw_bullet(x, y):
    # Draw bullet shape with trail
    pygame.draw.rect(screen, YELLOW, (x, y, bullet_width, bullet_height))
    # Bullet tip
    pygame.draw.polygon(screen, YELLOW, [(x, y), (x + bullet_width, y), (x + bullet_width // 2, y - 5)])
    
    # Bullet trail
    for i in range(3):
        trail_y = y + bullet_height + i * 4
        alpha = 255 - i * 80
        trail_surf = pygame.Surface((bullet_width, 4), pygame.SRCALPHA)
        trail_surf.fill((255, min(255, 100 + i * 50), 0, alpha))
        screen.blit(trail_surf, (x, trail_y))

def move_bullets():
    for bullet in bullets[:]:
        # Update position using velocity
        bullet[0] += bullet[2]  # x position += x velocity
        bullet[1] += bullet[3]  # y position += y velocity
        
        # Remove if off screen
        if bullet[1] < 0 or bullet[0] < 0 or bullet[0] > WIDTH:
            bullets.remove(bullet)

def check_collisions():
    global score, game_over, level, next_level_score, player_level, next_ship_upgrade
    
    current_time = pygame.time.get_ticks()
    
    # Get current ship specs
    specs = ship_specs[player_level]
    w = specs["width"]
    h = specs["height"]
    
    # Check if player hits enemies
    has_shield = current_time < active_power_ups["shield"]
    player_rect = pygame.Rect(player_x, player_y, w, h)
    
    for enemy in enemies[:]:
        enemy_type = enemy[2]
        enemy_width = enemy_types[enemy_type]["width"]
        enemy_height = enemy_types[enemy_type]["height"]
        enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_width, enemy_height)
        
        if player_rect.colliderect(enemy_rect):
            if has_shield:
                # Shield absorbs hit
                create_explosion(enemy[0] + enemy_width//2, enemy[1] + enemy_height//2)
                enemies.remove(enemy)
                # Reduce shield time as penalty
                remaining = active_power_ups["shield"] - current_time
                active_power_ups["shield"] = current_time + remaining // 2
            else:
                game_over = True
                return
    
    # Check if player collects power-ups
    for power_up in power_ups[:]:
        power_type = power_up[2]
        power_width = powerup_types[power_type]["width"]
        power_height = powerup_types[power_type]["height"]
        power_rect = pygame.Rect(power_up[0], power_up[1], power_width, power_height)
        
        if player_rect.colliderect(power_rect):
            # Activate power-up
            duration = powerup_types[power_type]["duration"]
            active_power_ups[power_type] = current_time + duration
            power_ups.remove(power_up)
            
            # Display power-up message
            create_power_up_message(power_type)
    
    # Check if bullets hit enemies
    for bullet in bullets[:]:
        bullet_rect = pygame.Rect(bullet[0], bullet[1], bullet_width, bullet_height)
        
        for enemy in enemies[:]:
            enemy_type = enemy[2]
            enemy_width = enemy_types[enemy_type]["width"]
            enemy_height = enemy_types[enemy_type]["height"]
            enemy_rect = pygame.Rect(enemy[0], enemy[1], enemy_width, enemy_height)
            
            if bullet_rect.colliderect(enemy_rect):
                # Reduce enemy HP
                enemy[3] -= bullet_damage
                
                # Create hit effect
                create_hit_effect(bullet[0], bullet[1])
                
                # Remove bullet
                if bullet in bullets:
                    bullets.remove(bullet)
                
                # Check if enemy is destroyed
                if enemy[3] <= 0:
                    # Create explosion
                    create_explosion(enemy[0] + enemy_width//2, enemy[1] + enemy_height//2)
                    
                    # Add score
                    enemy_points = enemy_types[enemy_type]["points"]
                    score += enemy_points
                    
                    # Check for level up (every 100 points)
                    if score >= next_level_score:
                        level += 1
                        next_level_score += 100
                        enemy_spawn_rate = max(10, 30 - level)  # Enemies spawn faster with level
                        create_level_up_message()
                    
                    # Check for ship upgrade (every 500 points)
                    if score >= next_ship_upgrade and player_level < max_player_level:
                        player_level += 1
                        next_ship_upgrade += 500
                        create_ship_upgrade_message()
                    
                    # Remove enemy
                    enemies.remove(enemy)
                
                # Only process one collision per bullet
                break

# Messages
messages = []
def create_level_up_message():
    messages.append(["Level Up! Level " + str(level), 2000, YELLOW])

def create_ship_upgrade_message():
    messages.append(["Ship Upgraded! Level " + str(player_level), 2000, GREEN])

def create_power_up_message(power_type):
    if power_type == "rapid_fire":
        messages.append(["Rapid Fire Activated!", 2000, YELLOW])
    elif power_type == "spread_shot":
        messages.append(["Spread Shot Activated!", 2000, BLUE])
    elif power_type == "shield":
        messages.append(["Shield Activated!", 2000, GREEN])
    elif power_type == "speed_boost":
        messages.append(["Speed Boost Activated!", 2000, CYAN])

def update_messages():
    current_time = pygame.time.get_ticks()
    for message in messages[:]:
        message[1] -= clock.get_time()
        if message[1] <= 0:
            messages.remove(message)

def draw_messages():
    y_offset = 50
    for message in messages:
        text = font.render(message[0], True, message[2])
        text_rect = text.get_rect(center=(WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 30

# Hit effects
hit_effects = []
def create_hit_effect(x, y):
    hit_effects.append([x, y, 5])  # x, y, radius

def update_hit_effects():
    for effect in hit_effects[:]:
        effect[2] -= 0.5
        if effect[2] <= 0:
            hit_effects.remove(effect)

def draw_hit_effects():
    for effect in hit_effects:
        x, y, radius = effect
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(radius))

# Explosion effects
explosions = []
def create_explosion(x, y):
    explosions.append([x, y, 1])  # x, y, radius

def update_explosions():
    for explosion in explosions[:]:
        explosion[2] += 2  # Increase radius
        if explosion[2] > 30:
            explosions.remove(explosion)

def draw_explosions():
    for explosion in explosions:
        x, y, radius = explosion
        alpha = 255 - (radius * 8)
        if alpha < 0:
            alpha = 0
        
        # Draw multiple circles for explosion effect
        explosion_surf = pygame.Surface((radius*2, radius*2), pygame.SRCALPHA)
        pygame.draw.circle(explosion_surf, (255, 200, 0, alpha), (radius, radius), radius)
        pygame.draw.circle(explosion_surf, (255, 100, 0, alpha), (radius, radius), radius * 0.8)
        pygame.draw.circle(explosion_surf, (255, 50, 0, alpha), (radius, radius), radius * 0.6)
        
        screen.blit(explosion_surf, (x - radius, y - radius))

def draw_active_power_ups():
    current_time = pygame.time.get_ticks()
    x = 10
    y = HEIGHT - 40
    
    for power_type, end_time in active_power_ups.items():
        if current_time < end_time:
            remaining = (end_time - current_time) // 1000  # Convert to seconds
            color = powerup_types[power_type]["color"]
            text = small_font.render(f"{power_type.replace('_', ' ').title()}: {remaining}s", True, color)
            screen.blit(text, (x, y))
            y -= 25

def draw_score():
    # Main score
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    
    # Level info
    level_text = font.render(f"Level: {level}", True, WHITE)
    screen.blit(level_text, (WIDTH - level_text.get_width() - 10, 10))
    
    # Next upgrade info
    if player_level < max_player_level:
        upgrade_text = small_font.render(f"Next ship: {next_ship_upgrade - score} pts", True, YELLOW)
        screen.blit(upgrade_text, (10, 40))

def draw_game_over():
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    game_over_text = font.render("GAME OVER", True, RED)
    restart_text = font.render("Press R to restart", True, WHITE)
    score_text = font.render(f"Final Score: {score}", True, WHITE)
    level_text = font.render(f"Final Level: {level}", True, WHITE)
    
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 80))
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 - 40))
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2))
    screen.blit(level_text, (WIDTH//2 - level_text.get_width()//2, HEIGHT//2 + 40))

def reset_game():
    global player_x, player_y, enemies, bullets, power_ups, explosions, hit_effects
    global score, game_over, level, next_level_score, player_level, next_ship_upgrade
    global active_power_ups, messages
    
    # Reset player
    player_x = WIDTH // 2 - player_width // 2
    player_y = HEIGHT - player_height - 20
    player_level = 1
    
    # Clear game objects
    enemies = []
    bullets = []
    power_ups = []
    explosions = []
    hit_effects = []
    messages = []
    
    # Reset game variables
    score = 0
    game_over = False
    level = 1
    next_level_score = 100
    next_ship_upgrade = 500
    
    # Reset power-ups
    active_power_ups = {
        "rapid_fire": 0,
               "spread_shot": 0,
        "shield": 0,
        "speed_boost": 0
    }

def game_loop():
    global player_x, game_over
    running = True
    last_shot_time = 0
    
    while running:
        screen.fill(BLACK)
        draw_background()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                reset_game()
            
        if not game_over:
            # Handle player movement
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT] and player_x > 0:
                player_x -= player_speed
            if keys[pygame.K_RIGHT] and player_x < WIDTH - ship_specs[player_level]['width']:
                player_x += player_speed
            
            # Fire bullets
            if keys[pygame.K_SPACE]:
                current_time = pygame.time.get_ticks()
                if current_time - last_shot_time > fire_rate:
                    fire_bullet()
                    last_shot_time = current_time
            
            # Update game objects
            move_enemies()
            move_power_ups()
            move_bullets()
            check_collisions()
            update_messages()
            update_hit_effects()
            update_explosions()
            
            # Spawn new enemies and power-ups
            if random.randint(1, enemy_spawn_rate) == 1:
                spawn_enemy()
            if random.randint(1, powerup_spawn_rate) == 1:
                spawn_power_up()
        
        # Draw game elements
        draw_rocket(player_x, player_y)
        for enemy in enemies:
            draw_alien(enemy[0], enemy[1], enemy[2])
        for power_up in power_ups:
            draw_power_up(power_up[0], power_up[1], power_up[2])
        for bullet in bullets:
            draw_bullet(bullet[0], bullet[1])
        draw_score()
        draw_active_power_ups()
        draw_messages()
        draw_hit_effects()
        draw_explosions()
        
        if game_over:
            draw_game_over()
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

game_loop()
