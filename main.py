# -*- coding: utf-8 -*-

"""
============================================================
《一箭又一箭》——鼠标点击解谜小游戏
============================================================

游戏规则：
1. 棋盘为 10 × 10 网格。
2. 每个箭头有固定方向：
      0 = 空格
      1 = ↑
      2 = ↓
      3 = ←
      4 = →
3. 只能使用鼠标点击，不需要键盘操作。
4. 点击箭头时：
      - 如果箭头前方没有其他箭头：开始飞出动画。
      - 如果箭头前方有其他箭头：无法飞出，并扣除 1 次失误。
5. 每关有 3 次失误机会。
6. 最后一个箭头完全飞出屏幕后，当前关卡通关。
7. 开始界面点击“开始游戏”进入第 1 关。
8. 失败界面点击“重新开始”会重新加载“当前关卡”。
9. 第 1～4 关通关后点击“下一关”进入下一关。
10. 第 5 关通关后显示“全部通关”，可以重新开始第 1 关。

游戏状态：
    start   = 开始界面
    playing = 游戏中
    lose    = 游戏失败
    win     = 当前关卡通关

本版本重点：
    1. 完整状态机流程
    2. 5 个已经推演过有解的关卡
    3. 鼠标按钮交互
    4. 箭头飞出动画
    5. 顶部显示关卡、剩余箭头、剩余失误
    6. 详细中文注释
============================================================
"""

import pygame
import sys


# ============================================================
# 一、初始化 Pygame
# ============================================================

pygame.init()


# ============================================================
# 二、游戏基本参数
# ============================================================

GRID_SIZE = 10
CELL_SIZE = 60

BOARD_SIZE = GRID_SIZE * CELL_SIZE

# 顶部信息栏高度
TOP_BAR_HEIGHT = 80

# 窗口大小：600 × 680
WINDOW_WIDTH = BOARD_SIZE
WINDOW_HEIGHT = BOARD_SIZE + TOP_BAR_HEIGHT

FPS = 60

# 创建窗口
screen = pygame.display.set_mode(
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

pygame.display.set_caption("一箭又一箭")


# ============================================================
# 三、颜色
# ============================================================

WHITE = (255, 255, 255)
BLACK = (30, 30, 30)

GRAY = (180, 180, 180)
LIGHT_GRAY = (245, 245, 245)

UP_COLOR = (70, 130, 255)
DOWN_COLOR = (80, 190, 100)
LEFT_COLOR = (180, 100, 220)
RIGHT_COLOR = (255, 150, 50)

RED = (230, 60, 60)
GREEN = (40, 170, 80)

BUTTON_COLOR = (70, 130, 255)
BUTTON_HOVER_COLOR = (50, 105, 220)
BUTTON_TEXT_COLOR = WHITE

START_BG = (240, 245, 255)
LOSE_BG = (35, 35, 45)
WIN_BG = (235, 250, 240)


# ============================================================
# 四、字体
# ============================================================

# 如果电脑没有 SimHei，可以改成 Microsoft YaHei。
FONT = pygame.font.SysFont("SimHei", 24)
SMALL_FONT = pygame.font.SysFont("SimHei", 18)
BIG_FONT = pygame.font.SysFont("SimHei", 42)
TITLE_FONT = pygame.font.SysFont("SimHei", 52)


# ============================================================
# 五、5 个关卡数据
# ============================================================

"""
数字含义：
    0 = 空格
    1 = ↑
    2 = ↓
    3 = ←
    4 = →

下面 5 个关卡按照当前“同一行/同一列前方有箭头就阻挡”的
规则设计，并进行了状态搜索验证，均存在完整通关顺序。

为了便于理解，这里把一组可行顺序也写在每关后面的注释中。
坐标采用“第几行、第几列”，从 1 开始。

注意：
游戏运行时会复制关卡数组，因此玩家点击不会修改原始关卡。
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

# 一组可行顺序：
# (1,4) → (1,7) → (2,9) → (1,9) → (5,8) → (6,2)
# → (6,8) → (3,8) → (7,5) → (8,10) → (9,1) → (10,3)


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

# 一组可行顺序：
# (1,7) → (1,1) → (2,1) → (5,1) → (7,10) → (9,4)
# → (9,5) → (5,5) → (5,10) → (9,10) → (10,9) → (4,9)


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

# 一组可行顺序：
# (1,5) → (3,6) → (3,10) → (3,2) → (5,2) → (5,6)
# → (6,4) → (6,8) → (7,10) → (8,8) → (9,4) → (10,7)


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

# 一组可行顺序：
# (1,10) → (2,10) → (3,5) → (4,1) → (4,6) → (5,3)
# → (6,1) → (6,7) → (7,10) → (8,5) → (8,9) → (10,7)


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

# 一组可行顺序：
# (2,3) → (2,6) → (4,5) → (4,10) → (5,2) → (5,5)
# → (5,10) → (6,4) → (7,7) → (9,6) → (9,10) → (8,10)


# 将 5 个关卡统一保存到列表中
levels = [
    level1,
    level2,
    level3,
    level4,
    level5
]

TOTAL_LEVELS = len(levels)


# ============================================================
# 六、游戏状态变量
# ============================================================

# 当前关卡编号
current_level = 1

# 当前真正运行的棋盘
board = [row[:] for row in level1]

# 每关 3 次失误机会
mistakes_left = 3

# 最近一次错误点击的位置
error_cell = None

# 错误提示开始时间
error_time = 0

# 当前游戏状态
game_state = "start"

# 正在飞出的箭头列表
flying_arrows = []

# 飞出速度：每帧移动 15 像素
FLY_SPEED = 15


# ============================================================
# 七、按钮区域
# ============================================================

START_BUTTON = pygame.Rect(
    180, 350, 240, 70
)

RESTART_BUTTON = pygame.Rect(
    180, 390, 240, 70
)

NEXT_BUTTON = pygame.Rect(
    180, 390, 240, 70
)


# ============================================================
# 八、关卡加载与状态切换
# ============================================================

def load_level(level_number):
    """
    加载指定关卡。

    这里会把原始关卡数组复制一份。
    因此玩家操作 board 时，不会破坏 levels 中的原始数据。
    """

    global current_level
    global board
    global mistakes_left
    global error_cell
    global error_time
    global flying_arrows
    global game_state

    # 限制关卡编号范围
    level_number = max(1, min(level_number, TOTAL_LEVELS))

    current_level = level_number

    # 复制二维数组
    board = [
        row[:]
        for row in levels[current_level - 1]
    ]

    # 每进入一个新关卡，都恢复 3 次失误
    mistakes_left = 3

    # 清除错误提示
    error_cell = None
    error_time = 0

    # 清除上一关可能存在的飞行动画
    flying_arrows.clear()

    # 进入游戏状态
    game_state = "playing"


def start_new_game():
    """
    从第 1 关开始一整局游戏。
    """

    load_level(1)


def restart_current_level():
    """
    失败后重新开始当前关卡。

    注意：
    本版本按照当前需求，失败后不会退回第 1 关，
    而是重新加载玩家刚刚失败的这一关。
    """

    load_level(current_level)


def go_to_next_level():
    """
    通关后的下一关逻辑。

    第 1～4 关：
        进入下一关。

    第 5 关：
        已经全部通关，重新开始时回到第 1 关。
    """

    if current_level < TOTAL_LEVELS:
        load_level(current_level + 1)
    else:
        start_new_game()


# ============================================================
# 九、统计剩余箭头
# ============================================================

def count_arrows():
    """
    统计当前还没有完全飞出屏幕的箭头。

    包括：
        1. 仍在棋盘上的箭头
        2. 正在飞行动画中的箭头

    只有两者都为 0，才真正通关。
    """

    count = 0

    # 统计棋盘上的箭头
    for row in board:
        for cell in row:
            if cell != 0:
                count += 1

    # 统计正在飞出的箭头
    count += len(flying_arrows)

    return count


# ============================================================
# 十、判断箭头能否飞出
# ============================================================

def can_arrow_leave(row, col):
    """
    判断指定位置的箭头前方有没有其他箭头。

    返回 True：
        没有阻挡，可以飞出。

    返回 False：
        前方有箭头，不能飞出。

    注意：
    已经开始飞出的箭头会从 board 中移除，
    所以它不会继续阻挡其他箭头。
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

    # ←：检查同一行左方
    elif direction == 3:
        for c in range(col - 1, -1, -1):
            if board[row][c] != 0:
                return False

    # →：检查同一行右方
    elif direction == 4:
        for c in range(col + 1, GRID_SIZE):
            if board[row][c] != 0:
                return False

    return True


# ============================================================
# 十一、获取箭头颜色
# ============================================================

def get_arrow_color(direction):
    """
    根据箭头方向返回对应颜色。
    """

    if direction == 1:
        return UP_COLOR

    if direction == 2:
        return DOWN_COLOR

    if direction == 3:
        return LEFT_COLOR

    return RIGHT_COLOR


# ============================================================
# 十二、绘制固定箭头
# ============================================================

def draw_arrow(row, col, direction, error=False):
    """
    绘制仍然位于棋盘格子中的箭头。
    """

    # 当前格子的左上角
    x = col * CELL_SIZE
    y = TOP_BAR_HEIGHT + row * CELL_SIZE

    # 当前格子的中心点
    center_x = x + CELL_SIZE // 2
    center_y = y + CELL_SIZE // 2

    # 错误点击时暂时显示红色
    if error:
        color = RED
    else:
        color = get_arrow_color(direction)

    head_size = 18
    body_width = 12
    body_length = 28

    # ↑
    if direction == 1:

        points = [
            (center_x, center_y - head_size),
            (center_x - head_size, center_y),
            (center_x + head_size, center_y)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                center_x - body_width // 2,
                center_y,
                body_width,
                body_length
            )
        )

    # ↓
    elif direction == 2:

        points = [
            (center_x, center_y + head_size),
            (center_x - head_size, center_y),
            (center_x + head_size, center_y)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                center_x - body_width // 2,
                center_y - body_length,
                body_width,
                body_length
            )
        )

    # ←
    elif direction == 3:

        points = [
            (center_x - head_size, center_y),
            (center_x, center_y - head_size),
            (center_x, center_y + head_size)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                center_x,
                center_y - body_width // 2,
                body_length,
                body_width
            )
        )

    # →
    elif direction == 4:

        points = [
            (center_x + head_size, center_y),
            (center_x, center_y - head_size),
            (center_x, center_y + head_size)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                center_x - body_length,
                center_y - body_width // 2,
                body_length,
                body_width
            )
        )


# ============================================================
# 十三、绘制飞行动画中的箭头
# ============================================================

def draw_flying_arrow(x, y, direction):
    """
    使用像素坐标绘制正在飞出的箭头。

    x、y 是箭头中心点，而不是棋盘行列。
    """

    color = get_arrow_color(direction)

    head_size = 18
    body_width = 12
    body_length = 28

    # ↑
    if direction == 1:

        points = [
            (x, y - head_size),
            (x - head_size, y),
            (x + head_size, y)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                x - body_width // 2,
                y,
                body_width,
                body_length
            )
        )

    # ↓
    elif direction == 2:

        points = [
            (x, y + head_size),
            (x - head_size, y),
            (x + head_size, y)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                x - body_width // 2,
                y - body_length,
                body_width,
                body_length
            )
        )

    # ←
    elif direction == 3:

        points = [
            (x - head_size, y),
            (x, y - head_size),
            (x, y + head_size)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                x,
                y - body_width // 2,
                body_length,
                body_width
            )
        )

    # →
    elif direction == 4:

        points = [
            (x + head_size, y),
            (x, y - head_size),
            (x, y + head_size)
        ]

        pygame.draw.polygon(
            screen,
            color,
            points
        )

        pygame.draw.rect(
            screen,
            color,
            (
                x - body_length,
                y - body_width // 2,
                body_length,
                body_width
            )
        )


# ============================================================
# 十四、更新飞出动画
# ============================================================

def update_flying_arrows():
    """
    每一帧更新所有飞行动画。

    箭头沿着自己的方向移动。
    当箭头完全离开游戏窗口后，
    才从 flying_arrows 列表中删除。
    """

    # 使用列表副本遍历，方便安全删除
    for arrow in flying_arrows[:]:

        # 只处理正在飞行的箭头
        if not arrow["is_flying"]:
            continue

        direction = arrow["direction"]
        speed = arrow["fly_speed"]

        # ↑
        if direction == 1:
            arrow["y"] -= speed

        # ↓
        elif direction == 2:
            arrow["y"] += speed

        # ←
        elif direction == 3:
            arrow["x"] -= speed

        # →
        elif direction == 4:
            arrow["x"] += speed

        # 箭头最大尺寸约为 18 像素。
        # 留出 25 像素边距后，再删除动画对象，
        # 可以保证视觉上整个箭头已经飞出窗口。
        margin = 25

        completely_out = (
            arrow["x"] < -margin
            or arrow["x"] > WINDOW_WIDTH + margin
            or arrow["y"] < TOP_BAR_HEIGHT - margin
            or arrow["y"] > WINDOW_HEIGHT + margin
        )

        if completely_out:
            flying_arrows.remove(arrow)


# ============================================================
# 十五、绘制按钮
# ============================================================

def draw_button(rect, text):
    """
    绘制圆角按钮。

    鼠标悬停在按钮上时改变颜色，
    让玩家能够直观看到按钮可以点击。
    """

    mouse_pos = pygame.mouse.get_pos()

    if rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER_COLOR
    else:
        color = BUTTON_COLOR

    # 按钮主体
    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=12
    )

    # 按钮文字
    text_surface = FONT.render(
        text,
        True,
        BUTTON_TEXT_COLOR
    )

    text_rect = text_surface.get_rect(
        center=rect.center
    )

    screen.blit(
        text_surface,
        text_rect
    )


# ============================================================
# 十六、绘制开始界面
# ============================================================

def draw_start_screen():
    """
    开始界面：
        标题
        游戏说明
        开始游戏按钮
    """

    screen.fill(START_BG)

    # 游戏标题
    title = TITLE_FONT.render(
        "一箭又一箭",
        True,
        BLACK
    )

    screen.blit(
        title,
        title.get_rect(
            center=(WINDOW_WIDTH // 2, 145)
        )
    )

    # 副标题
    subtitle = FONT.render(
        "点击箭头，让它们依次飞出棋盘",
        True,
        (80, 80, 80)
    )

    screen.blit(
        subtitle,
        subtitle.get_rect(
            center=(WINDOW_WIDTH // 2, 210)
        )
    )

    # 游戏说明
    rule1 = SMALL_FONT.render(
        "鼠标点击操作，不需要键盘",
        True,
        (90, 90, 90)
    )

    rule2 = SMALL_FONT.render(
        "前方有箭头会被挡住，错误点击会扣除失误次数",
        True,
        (90, 90, 90)
    )

    screen.blit(
        rule1,
        rule1.get_rect(
            center=(WINDOW_WIDTH // 2, 260)
        )
    )

    screen.blit(
        rule2,
        rule2.get_rect(
            center=(WINDOW_WIDTH // 2, 290)
        )
    )

    # 关卡提示
    level_tip = SMALL_FONT.render(
        f"本游戏共有 {TOTAL_LEVELS} 个关卡",
        True,
        (90, 90, 90)
    )

    screen.blit(
        level_tip,
        level_tip.get_rect(
            center=(WINDOW_WIDTH // 2, 320)
        )
    )

    # 开始按钮
    draw_button(
        START_BUTTON,
        "开始游戏"
    )


# ============================================================
# 十七、绘制游戏棋盘
# ============================================================

def draw_board():
    """
    绘制游戏中的完整画面。
    """

    screen.fill(WHITE)

    # --------------------------------------------------------
    # 顶部信息栏
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        LIGHT_GRAY,
        (0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT)
    )

    # 当前关卡
    level_text = FONT.render(
        f"第 {current_level} 关 / 共 {TOTAL_LEVELS} 关",
        True,
        BLACK
    )

    screen.blit(
        level_text,
        (20, 12)
    )

    # 剩余箭头
    arrow_text = FONT.render(
        f"剩余箭头：{count_arrows()}",
        True,
        BLACK
    )

    screen.blit(
        arrow_text,
        (230, 12)
    )

    # 剩余失误
    mistake_color = (
        RED
        if mistakes_left <= 1
        else BLACK
    )

    mistake_text = FONT.render(
        f"剩余失误：{mistakes_left}",
        True,
        mistake_color
    )

    screen.blit(
        mistake_text,
        (430, 12)
    )

    # 操作提示
    tip_text = SMALL_FONT.render(
        "鼠标点击箭头即可操作",
        True,
        (100, 100, 100)
    )

    screen.blit(
        tip_text,
        (20, 48)
    )

    # --------------------------------------------------------
    # 绘制 10 × 10 网格
    # --------------------------------------------------------

    for i in range(GRID_SIZE + 1):

        # 垂直线
        x = i * CELL_SIZE

        pygame.draw.line(
            screen,
            GRAY,
            (x, TOP_BAR_HEIGHT),
            (x, WINDOW_HEIGHT),
            1
        )

        # 水平线
        y = TOP_BAR_HEIGHT + i * CELL_SIZE

        pygame.draw.line(
            screen,
            GRAY,
            (0, y),
            (WINDOW_WIDTH, y),
            1
        )

    # --------------------------------------------------------
    # 绘制仍然位于棋盘中的箭头
    # --------------------------------------------------------

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            direction = board[row][col]

            if direction == 0:
                continue

            # 最近一次错误点击后，
            # 在 300 毫秒内显示红色。
            is_error = (
                error_cell == (row, col)
                and pygame.time.get_ticks() - error_time < 300
            )

            draw_arrow(
                row,
                col,
                direction,
                error=is_error
            )

    # --------------------------------------------------------
    # 绘制正在飞出的箭头
    # --------------------------------------------------------

    for arrow in flying_arrows:

        draw_flying_arrow(
            arrow["x"],
            arrow["y"],
            arrow["direction"]
        )


# ============================================================
# 十八、处理游戏中的棋盘点击
# ============================================================

def handle_board_click(mouse_x, mouse_y):
    """
    处理玩家点击棋盘的行为。

    成功：
        生成一个飞行动画对象，
        再从 board 逻辑数组中删除箭头。

    失败：
        箭头不动，
        失误次数减 1。
    """

    global mistakes_left
    global error_cell
    global error_time
    global game_state

    if game_state != "playing":
        return

    # 点击顶部信息栏，不处理
    if mouse_y < TOP_BAR_HEIGHT:
        return

    # 根据鼠标位置计算行列
    col = mouse_x // CELL_SIZE
    row = (mouse_y - TOP_BAR_HEIGHT) // CELL_SIZE

    # 防止越界
    if row < 0 or row >= GRID_SIZE:
        return

    if col < 0 or col >= GRID_SIZE:
        return

    direction = board[row][col]

    # 点击空格，不处理
    if direction == 0:
        return

    # --------------------------------------------------------
    # 情况一：前方没有阻挡
    # --------------------------------------------------------

    if can_arrow_leave(row, col):

        # 计算箭头中心的像素坐标
        start_x = (
            col * CELL_SIZE
            + CELL_SIZE // 2
        )

        start_y = (
            TOP_BAR_HEIGHT
            + row * CELL_SIZE
            + CELL_SIZE // 2
        )

        # 创建飞行动画对象
        flying_arrows.append({
            "x": start_x,
            "y": start_y,
            "direction": direction,

            # 是否正在飞行
            "is_flying": True,

            # 飞行速度
            "fly_speed": FLY_SPEED
        })

        # 从逻辑棋盘中移除。
        # 注意：视觉上的箭头不会立即消失，
        # 因为它已经被加入 flying_arrows。
        board[row][col] = 0

        error_cell = None

    # --------------------------------------------------------
    # 情况二：前方有阻挡
    # --------------------------------------------------------

    else:

        # 记录错误位置
        error_cell = (row, col)

        # 记录错误时间
        error_time = pygame.time.get_ticks()

        # 扣除一次失误
        mistakes_left -= 1

        if mistakes_left < 0:
            mistakes_left = 0

        # 失误次数用完，进入失败状态
        if mistakes_left == 0:
            game_state = "lose"


# ============================================================
# 十九、绘制失败界面
# ============================================================

def draw_lose_screen():
    """
    失败界面显示：
        失败
        当前失败关卡
        重新开始按钮
    """

    screen.fill(LOSE_BG)

    # “失败”
    title = TITLE_FONT.render(
        "失败",
        True,
        RED
    )

    screen.blit(
        title,
        title.get_rect(
            center=(WINDOW_WIDTH // 2, 180)
        )
    )

    # 当前关卡
    tip = FONT.render(
        f"第 {current_level} 关挑战失败",
        True,
        WHITE
    )

    screen.blit(
        tip,
        tip.get_rect(
            center=(WINDOW_WIDTH // 2, 250)
        )
    )

    # 说明
    small_tip = SMALL_FONT.render(
        "重新开始后会重新加载当前关卡",
        True,
        (210, 210, 210)
    )

    screen.blit(
        small_tip,
        small_tip.get_rect(
            center=(WINDOW_WIDTH // 2, 315)
        )
    )

    # 重新开始按钮
    draw_button(
        RESTART_BUTTON,
        "重新开始"
    )


# ============================================================
# 二十、绘制通关界面
# ============================================================

def draw_win_screen():
    """
    通关界面：

    第 1～4 关：
        显示“通关”和“下一关”。

    第 5 关：
        显示“全部通关”和“重新开始”。
    """

    screen.fill(WIN_BG)

    # --------------------------------------------------------
    # 标题
    # --------------------------------------------------------

    if current_level < TOTAL_LEVELS:
        title_text = "通关"
    else:
        title_text = "全部通关！"

    title = TITLE_FONT.render(
        title_text,
        True,
        GREEN
    )

    screen.blit(
        title,
        title.get_rect(
            center=(WINDOW_WIDTH // 2, 180)
        )
    )

    # --------------------------------------------------------
    # 提示文字
    # --------------------------------------------------------

    if current_level < TOTAL_LEVELS:

        tip_text = (
            f"恭喜完成第 {current_level} 关！"
        )

        small_text = "点击“下一关”继续挑战"

    else:

        tip_text = (
            f"恭喜你完成全部 {TOTAL_LEVELS} 个关卡！"
        )

        small_text = "点击“重新开始”可以再次挑战"

    tip = FONT.render(
        tip_text,
        True,
        BLACK
    )

    screen.blit(
        tip,
        tip.get_rect(
            center=(WINDOW_WIDTH // 2, 250)
        )
    )

    small_tip = SMALL_FONT.render(
        small_text,
        True,
        (90, 90, 90)
    )

    screen.blit(
        small_tip,
        small_tip.get_rect(
            center=(WINDOW_WIDTH // 2, 310)
        )
    )

    # --------------------------------------------------------
    # 按钮
    # --------------------------------------------------------

    if current_level < TOTAL_LEVELS:

        draw_button(
            NEXT_BUTTON,
            "下一关"
        )

    else:

        draw_button(
            NEXT_BUTTON,
            "重新开始"
        )


# ============================================================
# 二十一、处理菜单按钮点击
# ============================================================

def handle_menu_click(mouse_x, mouse_y):
    """
    根据当前状态处理按钮。

    start：
        开始游戏 → 第 1 关

    lose：
        重新开始 → 当前关卡

    win：
        第 1～4 关 → 下一关
        第 5 关 → 第 1 关重新开始
    """

    # --------------------------------------------------------
    # 开始界面
    # --------------------------------------------------------

    if game_state == "start":

        if START_BUTTON.collidepoint(
            mouse_x,
            mouse_y
        ):
            start_new_game()

    # --------------------------------------------------------
    # 失败界面
    # --------------------------------------------------------

    elif game_state == "lose":

        if RESTART_BUTTON.collidepoint(
            mouse_x,
            mouse_y
        ):
            restart_current_level()

    # --------------------------------------------------------
    # 通关界面
    # --------------------------------------------------------

    elif game_state == "win":

        if NEXT_BUTTON.collidepoint(
            mouse_x,
            mouse_y
        ):
            go_to_next_level()


# ============================================================
# 二十二、游戏主循环
# ============================================================

def main():
    """
    游戏主循环。

    状态流程：

                  ┌──────────────┐
                  │   start      │
                  │   开始界面    │
                  └──────┬───────┘
                         │ 开始游戏
                         ↓
                  ┌──────────────┐
              ┌──→│   playing    │←──┐
              │   │   游戏中      │   │
              │   └──────┬───────┘   │
              │          │            │
          重新开始      通关           │
              │          ↓            │
              │   ┌──────────────┐   │
              │   │     win      │───┘ 下一关
              │   │    通关界面    │
              │   └──────────────┘
              │
              │ 失败
              ↓
       ┌──────────────┐
       │     lose     │
       │    失败界面   │
       └──────────────┘

    第 5 关通关后：
        win → 重新开始 → 第 1 关
    """

    global game_state

    clock = pygame.time.Clock()

    while True:

        # ====================================================
        # 1. 处理所有事件
        # ====================================================

        for event in pygame.event.get():

            # 点击窗口关闭按钮
            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            # 鼠标左键点击
            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                mouse_x, mouse_y = event.pos

                # 游戏中：处理棋盘点击
                if game_state == "playing":

                    handle_board_click(
                        mouse_x,
                        mouse_y
                    )

                # 其他状态：处理按钮点击
                else:

                    handle_menu_click(
                        mouse_x,
                        mouse_y
                    )

        # ====================================================
        # 2. 更新游戏逻辑
        # ====================================================

        if game_state == "playing":

            # 更新所有飞行动画
            update_flying_arrows()

            # 只有棋盘和飞行动画中都没有箭头时，
            # 才真正进入通关状态。
            if count_arrows() == 0:

                game_state = "win"

        # ====================================================
        # 3. 根据状态绘制对应画面
        # ====================================================

        if game_state == "start":

            draw_start_screen()

        elif game_state == "playing":

            draw_board()

        elif game_state == "lose":

            draw_lose_screen()

        elif game_state == "win":

            draw_win_screen()

        # ====================================================
        # 4. 更新屏幕
        # ====================================================

        pygame.display.flip()

        # 控制游戏帧率
        clock.tick(FPS)


# ============================================================
# 二十三、程序入口
# ============================================================

if __name__ == "__main__":
    main()
