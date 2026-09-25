"""打飞机小游戏 —— Python + pygame

经典飞机大战：
- 方向键 ← → 左右移动战机
- 空格键发射子弹
- 击落敌机得分，敌机撞到战机损失生命
- 生命归零游戏结束，按 R 重新开始

运行方式：
    pip install pygame
    python main.py
"""

import random
import sys

import pygame

# ---------- 基础设置 ----------
pygame.init()
WIDTH, HEIGHT = 480, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("打飞机小游戏")
clock = pygame.time.Clock()
FPS = 60

# 颜色
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (230, 50, 50)
YELLOW = (255, 230, 0)
BLUE = (80, 150, 255)

try:
    FONT = pygame.font.SysFont("simhei,msyh,arial", 26)
    FONT_SMALL = pygame.font.SysFont("simhei,msyh,arial", 20)
except Exception:
    FONT = pygame.font.Font(None, 32)
    FONT_SMALL = pygame.font.Font(None, 24)


# ---------- 玩家战机 ----------
class Player:
    def __init__(self):
        self.w = 50
        self.h = 50
        self.x = WIDTH // 2 - self.w // 2
        self.y = HEIGHT - 90
        self.speed = 7
        self.lives = 3
        self.invincible = 0  # 受击后的无敌帧

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.x > 0:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] and self.x < WIDTH - self.w:
            self.x += self.speed
        if self.invincible > 0:
            self.invincible -= 1

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self):
        # 无敌时闪烁
        if self.invincible > 0 and self.invincible // 5 % 2 == 0:
            return
        cx, w, h = self.x + self.w // 2, self.w, self.h
        # 机身
        pygame.draw.polygon(
            screen, GREEN,
            [(cx, self.y), (self.x, self.y + h), (self.x + w, self.y + h)],
        )
        # 机翼
        pygame.draw.polygon(
            screen, BLUE,
            [(self.x, self.y + h), (self.x - 12, self.y + h + 14),
             (self.x + 8, self.y + h - 8)],
        )
        pygame.draw.polygon(
            screen, BLUE,
            [(self.x + w, self.y + h), (self.x + w + 12, self.y + h + 14),
             (self.x + w - 8, self.y + h - 8)],
        )


# ---------- 子弹 ----------
class Bullet:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.w = 5
        self.h = 14
        self.speed = 13

    def update(self):
        self.y -= self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self):
        pygame.draw.rect(screen, YELLOW, (self.x, self.y, self.w, self.h))


# ---------- 敌机 ----------
class Enemy:
    def __init__(self):
        self.w = 46
        self.h = 46
        self.x = random.randint(0, WIDTH - self.w)
        self.y = random.randint(-160, -50)
        self.speed = random.randint(2, 5)

    def update(self):
        self.y += self.speed

    def rect(self):
        return pygame.Rect(self.x, self.y, self.w, self.h)

    def draw(self):
        cx, w, h = self.x + self.w // 2, self.w, self.h
        # 红色倒三角敌机
        pygame.draw.polygon(
            screen, RED,
            [(cx, self.y + h), (self.x, self.y), (self.x + w, self.y)],
        )


def draw_text(text, color, x, y, center=True, font=FONT):
    img = font.render(text, True, color)
    rect = img.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(img, rect)


def reset_game():
    return Player(), [], [], 0, True


def main():
    player, bullets, enemies, score, running = reset_game()
    spawn_timer = 0
    game_over = False

    while True:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and game_over:
                if event.key == pygame.K_r:
                    player, bullets, enemies, score, running = reset_game()
                    game_over = False

        keys = pygame.key.get_pressed()

        # 非游戏结束状态下的逻辑
        if not game_over:
            player.update(keys)
            # 发射子弹（按住空格连续发射）
            if keys[pygame.K_SPACE]:
                bullets.append(Bullet(player.x + player.w // 2 - 2, player.y))

            # 生成敌机
            spawn_timer += 1
            if spawn_timer >= 40:
                enemies.append(Enemy())
                spawn_timer = 0

            # 子弹与敌机更新
            bullets = [b for b in bullets if b.y > -20]
            for b in bullets:
                b.update()
            for e in enemies:
                e.update()

            # 子弹击中敌机
            hit_enemies = set()
            for b in bullets:
                for i, e in enumerate(enemies):
                    if i not in hit_enemies and b.rect().colliderect(e.rect()):
                        hit_enemies.add(i)
                        score += 10
            if hit_enemies:
                bullets = [b for b in bullets
                           if not any(b.rect().colliderect(enemies[i].rect())
                                      for i in hit_enemies)]
                enemies = [e for i, e in enumerate(enemies) if i not in hit_enemies]

            # 敌机撞玩家
            enemies = [e for e in enemies if e.y < HEIGHT + 60]
            for e in enemies:
                if player.invincible == 0 and e.rect().colliderect(player.rect()):
                    player.lives -= 1
                    player.invincible = 90  # 1.5 秒无敌
                    enemies.remove(e)
                    if player.lives <= 0:
                        game_over = True

        # ---------- 绘制 ----------
        screen.fill(BLACK)

        # 顶部信息
        draw_text(f"分数 {score}", WHITE, 90, 30)
        draw_text(f"生命 {'♥' * max(player.lives, 0)}{'♡' * (3 - max(player.lives, 0))}",
                  RED, WIDTH - 110, 30)

        if game_over:
            draw_text("游戏结束", WHITE, WIDTH // 2, HEIGHT // 2 - 60, font=FONT)
            draw_text(f"最终得分 {score}", YELLOW, WIDTH // 2, HEIGHT // 2 - 20)
            draw_text("按 R 重新开始", WHITE, WIDTH // 2, HEIGHT // 2 + 20, font=FONT_SMALL)
        else:
            player.draw()
            for b in bullets:
                b.draw()
            for e in enemies:
                e.draw()
            draw_text("←→ 移动  空格 发射", WHITE, WIDTH // 2, HEIGHT - 25, font=FONT_SMALL)

        pygame.display.flip()


if __name__ == "__main__":
    main()
