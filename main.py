# -*- coding: utf-8 -*-

"""
============================================================
《一箭又一箭》—— 现代极简风 UI 版本
============================================================

玩法回顾：
    1. 10 × 10 棋盘，格子里放着箭头。
    2. 方向编码：0 = 空，1 = ↑，2 = ↓，3 = ←，4 = →。
    3. 鼠标点击箭头：
         · 前方同行 / 同列没有其他箭头 → 箭头飞出棋盘。
         · 前方有箭头阻挡             → 方块变红并抖动，失误 -1。
    4. 失误次数扣完 → 失败。
    5. 所有箭头全部飞出屏幕 → 通关。

UI 设计要点：
    · 窗口 1000 × 700，背景米白 (249, 249, 246)
    · 左侧 10 × 10 棋盘，格子是带圆角的浅色方块，格间留 3px
    · 右侧浅灰圆角数据面板，显示关卡 / 剩余箭头 / 剩余失误（红心）
    · 按钮统一深灰绿 (47, 79, 79)，鼠标悬停时颜色变浅
    · 箭头使用四种柔和色：薄荷绿 / 浅琥珀 / 天蓝 / 珊瑚粉
============================================================
"""

import sys
import math
import pygame


# ============================================================
# 一、初始化 Pygame
# ============================================================

pygame.init()
pygame.display.set_caption("一箭又一箭")


# ============================================================
# 二、窗口与布局参数
# ============================================================

WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 700
FPS = 60

GRID_SIZE = 10                              # 棋盘为 10 × 10
CELL_SIZE = 56                              # 每个格子方块的边长
CELL_GAP = 3                                # 格子之间的间距（像素）
CELL_STEP = CELL_SIZE + CELL_GAP            # 一个格子占用的总步长 = 59
BOARD_PIXEL = GRID_SIZE * CELL_STEP - CELL_GAP   # 棋盘总宽度 = 587

BOARD_X = 40                                # 棋盘左上角 x 坐标
BOARD_Y = 57                                # 棋盘左上角 y 坐标

PANEL_X = 670                               # 右侧数据面板左上角 x
PANEL_Y = 57                                # 右侧数据面板左上角 y
PANEL_W = 290                               # 面板宽度
PANEL_H = 587                               # 面板高度（与棋盘等高）

# 创建窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# 帧率控制时钟
clock = pygame.time.Clock()


# ============================================================
# 三、配色方案（现代极简 / 小清新）
# ============================================================

BG_COLOR = (249, 249, 246)                  # 整体米白背景
EMPTY_CELL_COLOR = (238, 237, 232)          # 空格子：非常浅的灰
PANEL_COLOR = (238, 237, 231)               # 右侧面板底色：浅灰
CARD_COLOR = (255, 255, 255)                # 面板里的白色卡片

TEXT_DARK = (47, 79, 79)                    # 主文字：深灰绿
TEXT_MAIN = (62, 62, 60)                    # 正文文字
TEXT_SUB = (152, 150, 144)                  # 次要文字（浅灰）

BTN_COLOR = (47, 79, 79)                    # 按钮默认色：深灰绿
BTN_HOVER_COLOR = (78, 122, 114)            # 按钮悬停色：变浅
BTN_TEXT_COLOR = (255, 255, 255)            # 按钮文字颜色

HEART_COLOR = (226, 106, 106)               # 剩余失误：红心
HEART_EMPTY_COLOR = (222, 220, 214)         # 已失去的失误：空心灰

BLOCKED_COLOR = (232, 122, 122)             # 被阻挡时的浅红色

# 四种箭头对应的柔和色
ARROW_COLORS = {
    1: (142, 208, 166),     # ↑ 薄荷绿
    2: (247, 215, 138),     # ↓ 浅琥珀
    3: (126, 176, 230),     # ← 天蓝
    4: (233, 154, 154),     # → 珊瑚粉
}

# 各方向的单位位移向量
DIR_VEC = {
    1: (0, -1),
    2: (0, 1),
    3: (-1, 0),
    4: (1, 0),
}


# ============================================================
# 四、字体（统一使用微软雅黑）
# ============================================================

def load_font(size, bold=False):
    """
    加载微软雅黑字体。
    若系统找不到该字体，Pygame 会自动回退到默认字体。
    """
    return pygame.font.SysFont("microsoftyahei", size, bold=bold)


TITLE_FONT = load_font(72, bold=True)       # 开始界面大标题
SUBTITLE_FONT = load_font(24)               # 开始界面副标题
PAGE_TITLE_FONT = load_font(56, bold=True)  # 失败 / 通关界面标题
VALUE_FONT = load_font(32, bold=True)       # 面板卡片里的数值
LABEL_FONT = load_font(20)                  # 面板卡片里的标签
BODY_FONT = load_font(22)                   # 正文
SMALL_FONT = load_font(18)                  # 小字提示
BUTTON_FONT = load_font(26, bold=True)      # 大按钮文字
PANEL_BTN_FONT = load_font(22, bold=True)   # 面板按钮文字


# ============================================================
# 五、按钮区域（全局定义，方便事件检测与绘制复用）
# ============================================================

# 开始 / 失败 / 通关界面共用的居中主按钮
MAIN_BTN_RECT = pygame.Rect(370, 416, 260, 68)

# 游戏中右侧面板底部的两个按钮
RESTART_BTN = pygame.Rect(
    PANEL_X + 24,
    PANEL_Y + PANEL_H - 140,
    PANEL_W - 48,
    52
)

HOME_BTN = pygame.Rect(
    PANEL_X + 24,
    PANEL_Y + PANEL_H - 140 + 52 + 14,
    PANEL_W - 48,
    52
)


# ============================================================
# 六、5 个关卡数据
# ============================================================

"""
数字含义：
    0 = 空格
    1 = ↑
    2 = ↓
    3 = ←
    4 = →

下面 5 个关卡都经过推演，存在完整通关顺序。
游戏运行时会复制一份数组，玩家点击不会修改原始数据。
"""


# ------------------------------------------------------------
# 第 1 关：基础入门
# ------------------------------------------------------------
level1 = [
    [0, 0, 0, 1, 0, 0, 1, 0, 2, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 4, 0],
    [0, 0, 0, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 4, 0, 0],
    [0, 2, 0, 0, 0, 0, 0, 4, 0, 0],
    [0, 0, 0, 0, 3, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 4, 0, 0, 0, 0, 0, 0, 0]
]


# ------------------------------------------------------------
# 第 2 关：简单组合
# ------------------------------------------------------------
level2 = [
    [4, 0, 0, 0, 0, 0, 4, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 2, 0],
    [3, 0, 0, 0, 2, 0, 0, 0, 0, 3],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 3, 2, 0, 0, 0, 0, 2],
    [0, 0, 0, 0, 0, 0, 0, 0, 3, 0]
]


# ------------------------------------------------------------
# 第 3 关：横纵组合
# ------------------------------------------------------------
level3 = [
    [0, 0, 0, 0, 4, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 4, 0, 0, 0, 1, 0, 0, 0, 1],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 3, 0, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 3, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 4],
    [0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
    [0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 4, 0, 0, 0]
]


# ------------------------------------------------------------
# 第 4 关：多方向组合
# ------------------------------------------------------------
level4 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [0, 0, 0, 0, 4, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 3, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 0, 0, 0, 0, 0],
    [1, 0, 0, 0, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 3],
    [0, 0, 0, 0, 2, 0, 0, 0, 3, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 1, 0, 0, 0]
]


# ------------------------------------------------------------
# 第 5 关：综合挑战
# ------------------------------------------------------------
level5 = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 2, 0, 0, 1, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 1, 0, 0, 0, 0, 4],
    [0, 1, 0, 0, 1, 0, 0, 0, 0, 4],
    [0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [0, 0, 0, 0, 0, 3, 0, 0, 0, 3],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
]


# 所有关卡统一存进列表
levels = [level1, level2, level3, level4, level5]
TOTAL_LEVELS = len(levels)


# ============================================================
# 七、游戏状态变量
# ============================================================

current_level = 1                           # 当前关卡编号（1 开始）
board = [row[:] for row in level1]          # 当前运行的棋盘
mistakes_left = 3                           # 剩余失误机会

game_state = "start"                        # start / playing / lose / win

flying_arrows = []                          # 正在飞出的箭头列表
blocked_fx = {}                             # 被阻挡的抖动动画：{(row, col): 起始时间}

FLY_SPEED = 15                              # 箭头每帧飞出速度（像素）
BLOCK_DURATION = 420                        # 被阻挡抖动持续时间（毫秒）


# ============================================================
# 八、通用绘制工具
# ============================================================

def draw_button(rect, text, font, radius=15):
    """
    绘制一个圆角按钮。

    鼠标悬停在按钮上时，颜色由深灰绿变为较浅的灰绿，
    给玩家清晰的“可点击”反馈。
    """
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    color = BTN_HOVER_COLOR if hovered else BTN_COLOR

    # 按钮主体（圆角矩形）
    pygame.draw.rect(screen, color, rect, border_radius=radius)

    # 按钮文字（居中）
    text_surface = font.render(text, True, BTN_TEXT_COLOR)
    screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_arrow_icon(surface, cx, cy, direction, color, scale=1.0):
    """
    在指定位置绘制一个箭头图形（默认白色）。

    实现思路：
        先定义“向上箭头”的 7 个顶点相对坐标，
        再根据方向做旋转，得到最终的顶点坐标，
        最后用 draw.polygon 一次性绘制出来。

    参数：
        surface  : 绘制目标 Surface
        cx, cy   : 箭头中心坐标
        direction: 1=上  2=下  3=左  4=右
        color    : 箭头颜色
        scale    : 缩放比例
    """
    L = 16 * scale          # 中心到箭尖的距离
    HL = 14 * scale         # 箭头三角头的长度
    HW = 13 * scale         # 箭头三角头的半宽
    SW = 5.5 * scale        # 箭杆的半宽

    # 以“向上箭头”为原型，记录 7 个顶点相对中心的偏移
    base_points = [
        (0, -L),            # 箭尖
        (HW, -L + HL),      # 三角头右下角
        (SW, -L + HL),      # 箭杆右上
        (SW, L),            # 箭杆右下
        (-SW, L),           # 箭杆左下
        (-SW, -L + HL),     # 箭杆左上
        (-HW, -L + HL),     # 三角头左下角
    ]

    points = []
    for dx, dy in base_points:
        if direction == 1:          # 向上：不旋转
            rx, ry = dx, dy
        elif direction == 2:        # 向下：旋转 180°
            rx, ry = -dx, -dy
        elif direction == 3:        # 向左：逆时针旋转 90°
            rx, ry = dy, -dx
        else:                       # 向右：顺时针旋转 90°
            rx, ry = -dy, dx
        points.append((cx + rx, cy + ry))

    pygame.draw.polygon(surface, color, points)


def draw_heart(surface, cx, cy, size, color):
    """
    用两个圆 + 一个三角形拼出一个爱心。
    用于表示“剩余失误机会”。
    """
    r = size * 0.27

    # 左右两个圆
    pygame.draw.circle(
        surface, color,
        (int(cx - size * 0.22), int(cy - size * 0.14)),
        int(r)
    )
    pygame.draw.circle(
        surface, color,
        (int(cx + size * 0.22), int(cy - size * 0.14)),
        int(r)
    )

    # 下方三角形
    pygame.draw.polygon(
        surface, color,
        [
            (cx - size * 0.47, cy - size * 0.06),
            (cx + size * 0.47, cy - size * 0.06),
            (cx, cy + size * 0.48),
        ]
    )


# ============================================================
# 九、关卡加载与状态切换
# ============================================================

def load_level(level_number):
    """
    加载指定关卡：
        · 复制一份关卡数据，避免破坏原始数组
        · 重置失误次数、抖动动画、飞行动画
        · 把游戏状态切换到 playing
    """
    global current_level, board, mistakes_left, game_state

    level_number = max(1, min(level_number, TOTAL_LEVELS))
    current_level = level_number

    # 深拷贝二维数组
    board = [row[:] for row in levels[current_level - 1]]

    mistakes_left = 3
    blocked_fx.clear()
    flying_arrows.clear()

    game_state = "playing"


def start_new_game():
    """从第 1 关开始一整局新游戏。"""
    load_level(1)


def restart_current_level():
    """重新加载当前关卡（失败后使用）。"""
    load_level(current_level)


def go_to_next_level():
    """
    通关后的“下一关”逻辑：
        第 1～4 关 → 进入下一关
        第 5 关    → 全部通关，回到第 1 关
    """
    if current_level < TOTAL_LEVELS:
        load_level(current_level + 1)
    else:
        start_new_game()


# ============================================================
# 十、游戏逻辑：统计与判定
# ============================================================

def count_arrows():
    """
    统计还没有完全飞出屏幕的箭头总数。

    包含：
        1. 仍在棋盘上的箭头
        2. 正在飞行动画中的箭头

    只有两者同时为 0，才算真正通关。
    """
    count = 0

    for row in board:
        for cell in row:
            if cell != 0:
                count += 1

    count += len(flying_arrows)
    return count


def can_arrow_leave(row, col):
    """
    判断 (row, col) 处的箭头前方是否有其他箭头阻挡。

    返回 True  → 前方畅通，可以飞出
    返回 False → 前方有箭头，不能飞出
    """
    direction = board[row][col]

    # ↑：检查同一列上方
    if direction == 1:
        for r in range(row - 1, -1, -1):
            if board[r][col] != 0:
                return False

    # ↓：检查同一列下方
    elif direction == 2:
        for r in range(row + 1, GRID_SIZE):
            if board[r][col] != 0:
                return False

    # ←：检查同一行左侧
    elif direction == 3:
        for c in range(col - 1, -1, -1):
            if board[row][c] != 0:
                return False

    # →：检查同一行右侧
    elif direction == 4:
        for c in range(col + 1, GRID_SIZE):
            if board[row][c] != 0:
                return False

    return True


# ============================================================
# 十一、飞行动画更新
# ============================================================

def update_flying_arrows():
    """
    每帧更新所有正在飞出的箭头：

        · 沿自身方向移动
        · 随着飞行距离增加逐渐变淡
        · 完全离开窗口后从列表中移除
    """
    for arrow in flying_arrows[:]:

        dx, dy = DIR_VEC[arrow["direction"]]
        arrow["x"] += dx * FLY_SPEED
        arrow["y"] += dy * FLY_SPEED
        arrow["dist"] += FLY_SPEED

        # 越飞越透明（最低保留 60 的不透明度，避免突兀消失）
        arrow["alpha"] = max(60.0, 255.0 - arrow["dist"] * 0.36)

        # 判断是否已经完全飞出窗口
        margin = CELL_SIZE
        out = (
            arrow["x"] < -margin
            or arrow["x"] > WINDOW_WIDTH + margin
            or arrow["y"] < -margin
            or arrow["y"] > WINDOW_HEIGHT + margin
        )
        if out:
            flying_arrows.remove(arrow)


# ============================================================
# 十二、开始界面
# ============================================================

def draw_start_screen():
    """
    开始界面：
        · 顶部四个彩色箭头方块作为装饰
        · 居中大标题 + 副标题
        · 深灰绿圆角“开始游戏”按钮
    """
    screen.fill(BG_COLOR)

    # --------------------------------------------------------
    # 装饰：一排四个彩色箭头方块
    # --------------------------------------------------------
    deco_size = 64
    deco_gap = 20
    total_w = 4 * deco_size + 3 * deco_gap
    start_x = (WINDOW_WIDTH - total_w) // 2
    deco_y = 110

    for i, direction in enumerate([1, 3, 4, 2]):
        x = start_x + i * (deco_size + deco_gap)
        rect = pygame.Rect(x, deco_y, deco_size, deco_size)

        pygame.draw.rect(
            screen, ARROW_COLORS[direction], rect, border_radius=16
        )
        draw_arrow_icon(
            screen, rect.centerx, rect.centery,
            direction, (255, 255, 255)
        )

    # --------------------------------------------------------
    # 大标题
    # --------------------------------------------------------
    title = TITLE_FONT.render("一箭又一箭", True, TEXT_DARK)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 258)))

    # --------------------------------------------------------
    # 副标题
    # --------------------------------------------------------
    subtitle = SUBTITLE_FONT.render(
        "点击箭头，让它们依次飞出棋盘", True, TEXT_SUB
    )
    screen.blit(
        subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 330))
    )

    # --------------------------------------------------------
    # 开始游戏按钮
    # --------------------------------------------------------
    draw_button(MAIN_BTN_RECT, "开始游戏", BUTTON_FONT)

    # --------------------------------------------------------
    # 底部小字提示
    # --------------------------------------------------------
    tip = SMALL_FONT.render(
        f"共 {TOTAL_LEVELS} 个关卡  ·  每关 3 次失误机会", True, TEXT_SUB
    )
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 560)))


# ============================================================
# 十三、游戏界面：棋盘
# ============================================================

def cell_topleft(row, col):
    """返回第 row 行第 col 列格子的左上角像素坐标。"""
    return BOARD_X + col * CELL_STEP, BOARD_Y + row * CELL_STEP


def draw_board():
    """
    绘制左侧 10 × 10 棋盘。

    每个格子都是一块带圆角的方块：
        · 空格子     → 非常浅的灰色
        · 有箭头格子 → 对应方向的柔和色 + 白色箭头
        · 被阻挡格子 → 浅红色 + 左右抖动
    """
    now = pygame.time.get_ticks()

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            x, y = cell_topleft(row, col)
            direction = board[row][col]
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # ---------- 空格子 ----------
            if direction == 0:
                pygame.draw.rect(
                    screen, EMPTY_CELL_COLOR, rect, border_radius=14
                )
                continue

            # ---------- 判断是否处于“被阻挡”反馈中 ----------
            blocked = False
            offset_x = 0

            start_time = blocked_fx.get((row, col))
            if start_time is not None:
                elapsed = now - start_time
                if elapsed < BLOCK_DURATION:
                    blocked = True
                    progress = elapsed / BLOCK_DURATION
                    # 衰减正弦波：左右摆动幅度逐渐减小
                    offset_x = (
                        math.sin(progress * math.pi * 6)
                        * 7
                        * (1 - progress)
                    )
                else:
                    # 动画结束，清除记录
                    del blocked_fx[(row, col)]

            # ---------- 绘制方块 ----------
            color = BLOCKED_COLOR if blocked else ARROW_COLORS[direction]
            rect.x += int(offset_x)

            pygame.draw.rect(screen, color, rect, border_radius=14)

            # ---------- 绘制白色箭头 ----------
            draw_arrow_icon(
                screen, rect.centerx, rect.centery,
                direction, (255, 255, 255)
            )

    # --------------------------------------------------------
    # 绘制正在飞出的箭头（带淡出效果）
    # --------------------------------------------------------
    for arrow in flying_arrows:
        draw_flying_arrow(arrow)


def draw_flying_arrow(arrow):
    """
    绘制一个正在飞出的箭头。

    使用一块带 Alpha 通道的临时 Surface 先画好
    “圆角方块 + 白色箭头”，再整体设置透明度并贴到屏幕上，
    从而实现平滑的淡出效果。
    """
    surf = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)

    color = ARROW_COLORS[arrow["direction"]]
    pygame.draw.rect(
        surf, color, (0, 0, CELL_SIZE, CELL_SIZE), border_radius=14
    )
    draw_arrow_icon(
        surf, CELL_SIZE // 2, CELL_SIZE // 2,
        arrow["direction"], (255, 255, 255)
    )

    surf.set_alpha(int(arrow["alpha"]))
    screen.blit(
        surf,
        (arrow["x"] - CELL_SIZE // 2, arrow["y"] - CELL_SIZE // 2)
    )


# ============================================================
# 十四、游戏界面：右侧数据面板
# ============================================================

def draw_info_card(y, label, value):
    """
    绘制一张白色信息卡片。

    参数：
        y     : 卡片顶部 y 坐标
        label : 小号灰色标签文字
        value : 大号深灰绿数值文字
    """
    rect = pygame.Rect(PANEL_X + 24, y, PANEL_W - 48, 105)
    pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=18)

    # 标签
    label_surf = LABEL_FONT.render(label, True, TEXT_SUB)
    screen.blit(label_surf, (rect.x + 20, rect.y + 16))

    # 数值
    value_surf = VALUE_FONT.render(value, True, TEXT_DARK)
    screen.blit(value_surf, (rect.x + 20, rect.y + 52))


def draw_hearts_card(y, label, hearts):
    """
    绘制“剩余失误”卡片，用红心表示剩余次数。
    """
    rect = pygame.Rect(PANEL_X + 24, y, PANEL_W - 48, 105)
    pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=18)

    # 标签
    label_surf = LABEL_FONT.render(label, True, TEXT_SUB)
    screen.blit(label_surf, (rect.x + 20, rect.y + 16))

    # 三颗心，剩几颗就点亮几颗
    for i in range(3):
        cx = rect.x + 36 + i * 44
        cy = rect.y + 72
        color = HEART_COLOR if i < hearts else HEART_EMPTY_COLOR
        draw_heart(screen, cx, cy, 30, color)


def draw_panel():
    """
    绘制右侧浅灰圆角数据面板：
        · 当前关卡
        · 剩余箭头数
        · 剩余失误机会（红心）
        · 底部“重新开始”/“返回首页”按钮
    """
    # --------------------------------------------------------
    # 面板底板
    # --------------------------------------------------------
    panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=24)

    # --------------------------------------------------------
    # 三张信息卡片
    # --------------------------------------------------------
    card_y = PANEL_Y + 28

    draw_info_card(
        card_y,
        "当前关卡",
        f"{current_level} / {TOTAL_LEVELS}"
    )

    draw_info_card(
        card_y + 120,
        "剩余箭头",
        f"{count_arrows()}"
    )

    draw_hearts_card(
        card_y + 240,
        "剩余失误",
        mistakes_left
    )

    # --------------------------------------------------------
    # 中间小提示文字
    # --------------------------------------------------------
    tip1 = SMALL_FONT.render("点击箭头让它飞出棋盘", True, TEXT_SUB)
    tip2 = SMALL_FONT.render("前方有阻挡会扣除失误", True, TEXT_SUB)

    screen.blit(
        tip1, tip1.get_rect(center=(PANEL_X + PANEL_W // 2, 452))
    )
    screen.blit(
        tip2, tip2.get_rect(center=(PANEL_X + PANEL_W // 2, 478))
    )

    # --------------------------------------------------------
    # 底部按钮
    # --------------------------------------------------------
    draw_button(RESTART_BTN, "重新开始", PANEL_BTN_FONT)
    draw_button(HOME_BTN, "返回首页", PANEL_BTN_FONT)


def draw_game_screen():
    """绘制完整的游戏画面：左侧棋盘 + 右侧面板。"""
    screen.fill(BG_COLOR)
    draw_board()
    draw_panel()


# ============================================================
# 十五、失败界面
# ============================================================

def draw_lose_screen():
    """失败界面：柔和红标题 + 重新开始按钮。"""
    screen.fill(BG_COLOR)

    title = PAGE_TITLE_FONT.render("挑战失败", True, (226, 106, 106))
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 240)))

    tip = BODY_FONT.render(
        f"第 {current_level} 关的箭头挡住了你", True, TEXT_SUB
    )
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 320)))

    draw_button(MAIN_BTN_RECT, "重新开始", BUTTON_FONT)


# ============================================================
# 十六、通关界面
# ============================================================

def draw_win_screen():
    """
    通关界面：

    第 1～4 关 → “通关” + “下一关”按钮
    第 5 关    → “全部通关” + “重新开始”按钮
    """
    screen.fill(BG_COLOR)

    # --------------------------------------------------------
    # 标题
    # --------------------------------------------------------
    if current_level < TOTAL_LEVELS:
        title_text = "通关！"
        title_color = (95, 170, 120)
    else:
        title_text = "全部通关！"
        title_color = (95, 170, 120)

    title = PAGE_TITLE_FONT.render(title_text, True, title_color)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 240)))

    # --------------------------------------------------------
    # 提示文字
    # --------------------------------------------------------
    if current_level < TOTAL_LEVELS:
        tip_text = f"恭喜完成第 {current_level} 关"
        btn_text = "下一关"
    else:
        tip_text = f"你完成了全部 {TOTAL_LEVELS} 个关卡"
        btn_text = "重新开始"

    tip = BODY_FONT.render(tip_text, True, TEXT_SUB)
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 320)))

    # --------------------------------------------------------
    # 按钮
    # --------------------------------------------------------
    draw_button(MAIN_BTN_RECT, btn_text, BUTTON_FONT)


# ============================================================
# 十七、事件处理
# ============================================================

def handle_board_click(mx, my):
    """
    处理玩家点击棋盘的操作。

    可以飞出  → 生成一个飞行动画对象，并从逻辑棋盘上移除该箭头
    被阻挡   → 记录抖动动画，失误次数 -1
    """
    global mistakes_left, game_state

    # 点击位置必须落在棋盘范围内
    if not (BOARD_X <= mx < BOARD_X + BOARD_PIXEL and
            BOARD_Y <= my < BOARD_Y + BOARD_PIXEL):
        return

    # 换算成行列坐标
    col = (mx - BOARD_X) // CELL_STEP
    row = (my - BOARD_Y) // CELL_STEP

    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return

    direction = board[row][col]

    # 点击空格，不处理
    if direction == 0:
        return

    # --------------------------------------------------------
    # 情况一：前方畅通，箭头飞出
    # --------------------------------------------------------
    if can_arrow_leave(row, col):

        cx = BOARD_X + col * CELL_STEP + CELL_SIZE // 2
        cy = BOARD_Y + row * CELL_STEP + CELL_SIZE // 2

        flying_arrows.append({
            "x": float(cx),
            "y": float(cy),
            "direction": direction,
            "alpha": 255.0,
            "dist": 0.0,
        })

        # 从逻辑棋盘移除，避免重复点击
        board[row][col] = 0

        # 同时清除该格子上可能残留的抖动动画
        blocked_fx.pop((row, col), None)

    # --------------------------------------------------------
    # 情况二：前方有阻挡，扣一次失误
    # --------------------------------------------------------
    else:
        blocked_fx[(row, col)] = pygame.time.get_ticks()

        mistakes_left -= 1
        if mistakes_left <= 0:
            mistakes_left = 0
            game_state = "lose"


def handle_menu_click(mx, my):
    """处理开始 / 失败 / 通关界面上的按钮点击。"""
    global game_state

    # ---------- 开始界面 ----------
    if game_state == "start":
        if MAIN_BTN_RECT.collidepoint(mx, my):
            start_new_game()

    # ---------- 失败界面 ----------
    elif game_state == "lose":
        if MAIN_BTN_RECT.collidepoint(mx, my):
            restart_current_level()

    # ---------- 通关界面 ----------
    elif game_state == "win":
        if MAIN_BTN_RECT.collidepoint(mx, my):
            go_to_next_level()


# ============================================================
# 十八、主循环
# ============================================================

def main():
    """
    游戏主循环。

    状态流转：

        start  ──开始游戏──▶  playing
                                │
                    失败 ◀──────┼──────▶ 通关
                     │                   │
                重新开始            下一关 / 重新开始
                     │                   │
                     ▼                   ▼
                  playing             playing / start
    """
    global game_state

    while True:

        # ====================================================
        # 1. 事件处理
        # ====================================================
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                if game_state == "playing":
                    # 优先检测右侧面板按钮
                    if RESTART_BTN.collidepoint(mx, my):
                        restart_current_level()
                    elif HOME_BTN.collidepoint(mx, my):
                        game_state = "start"
                    else:
                        handle_board_click(mx, my)
                else:
                    handle_menu_click(mx, my)

        # ====================================================
        # 2. 逻辑更新
        # ====================================================
        if game_state == "playing":
            update_flying_arrows()

            # 棋盘和飞行动画里都没有箭头了 → 通关
            if count_arrows() == 0:
                game_state = "win"

        # ====================================================
        # 3. 画面绘制
        # ====================================================
        if game_state == "start":
            draw_start_screen()
        elif game_state == "playing":
            draw_game_screen()
        elif game_state == "lose":
            draw_lose_screen()
        elif game_state == "win":
            draw_win_screen()

        # ====================================================
        # 4. 刷新屏幕
        # ====================================================
        pygame.display.flip()
        clock.tick(FPS)


# ============================================================
# 十九、程序入口
# ============================================================

if __name__ == "__main__":
    main()