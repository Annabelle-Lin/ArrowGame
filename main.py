# -*- coding: utf-8 -*-

"""
============================================================
《一箭又一箭》——点击解谜小游戏
============================================================

游戏规则：
1. 棋盘为 10 × 10 网格。
2. 每个箭头都有一个固定方向。
3. 玩家只能使用鼠标点击箭头，不能使用键盘操作。
4. 点击箭头后：
   - 如果箭头前方没有其他箭头，它会进入飞出动画。
   - 如果箭头前方有其他箭头挡住，它不能消除，并扣除 1 次失误。
5. 初始拥有 3 次失误机会。
6. 最后一个箭头完全飞出屏幕后，游戏胜利。
7. 失误次数变成 0 后，游戏失败。

数字代表方向：
0 = 空格
1 = ↑ 上
2 = ↓ 下
3 = ← 左
4 = → 右
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
TOP_BAR_HEIGHT = 80

WINDOW_WIDTH = BOARD_SIZE
WINDOW_HEIGHT = BOARD_SIZE + TOP_BAR_HEIGHT

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("一箭又一箭")


# ============================================================
# 三、颜色
# ============================================================

WHITE = (255, 255, 255)
GRAY = (180, 180, 180)
BLACK = (30, 30, 30)

UP_COLOR = (70, 130, 255)
DOWN_COLOR = (80, 190, 100)
LEFT_COLOR = (180, 100, 220)
RIGHT_COLOR = (255, 150, 50)

RED = (230, 60, 60)
GREEN = (40, 170, 80)


# ============================================================
# 四、字体
# ============================================================

FONT = pygame.font.SysFont("SimHei", 24)
SMALL_FONT = pygame.font.SysFont("SimHei", 18)
BIG_FONT = pygame.font.SysFont("SimHei", 42)


# ============================================================
# 五、基础关卡地图
# ============================================================

# 0 = 空格
# 1 = ↑
# 2 = ↓
# 3 = ←
# 4 = →

# 第1关：基础入门
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

# 第2关：简单组合
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

# 第3关：横纵组合
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

# 第4关：多方向组合
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

# 第5关：综合基础关
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


# ============================================================
# 六、游戏变量
# ============================================================

current_level = 1

# 当前默认使用第1关。
# 使用 copy()，避免后面修改 board 时直接修改原始关卡数据。
board = [row[:] for row in level1]

mistakes_left = 3

# 最近一次错误点击的位置
error_cell = None

# 错误提示开始的时间
error_time = 0

# 游戏状态：
# playing = 游戏进行中
# win     = 胜利
# lose    = 失败
game_state = "playing"

# 正在飞出棋盘的箭头。
# 每个元素保存：
# x、y、direction、is_flying、fly_speed
flying_arrows = []

# 箭头飞出速度：15 像素/帧
fly_speed = 15


# ============================================================
# 七、计算剩余箭头数量
# ============================================================

def count_arrows():
    """统计棋盘中和正在飞出的所有箭头数量。"""

    count = 0

    # 棋盘中还没有开始飞出的箭头
    for row in board:
        for cell in row:
            if cell != 0:
                count += 1

    # 正在飞出的箭头也算作“剩余箭头”
    count += len(flying_arrows)

    return count


# ============================================================
# 八、判断箭头能否飞出
# ============================================================

def can_arrow_leave(row, col):
    """
    判断指定位置的箭头前方是否存在其他箭头。

    True  = 没有阻挡，可以飞出
    False = 有阻挡，不能飞出
    """

    direction = board[row][col]

    # 向上
    if direction == 1:
        for r in range(row - 1, -1, -1):
            if board[r][col] != 0:
                return False

    # 向下
    elif direction == 2:
        for r in range(row + 1, GRID_SIZE):
            if board[r][col] != 0:
                return False

    # 向左
    elif direction == 3:
        for c in range(col - 1, -1, -1):
            if board[row][c] != 0:
                return False

    # 向右
    elif direction == 4:
        for c in range(col + 1, GRID_SIZE):
            if board[row][c] != 0:
                return False

    return True


# ============================================================
# 九、绘制固定在棋盘上的箭头
# ============================================================

def draw_arrow(row, col, direction, error=False):
    """按照网格行列位置绘制箭头。"""

    x = col * CELL_SIZE
    y = TOP_BAR_HEIGHT + row * CELL_SIZE

    center_x = x + CELL_SIZE // 2
    center_y = y + CELL_SIZE // 2

    # 错误点击时临时显示红色
    if error:
        color = RED
    elif direction == 1:
        color = UP_COLOR
    elif direction == 2:
        color = DOWN_COLOR
    elif direction == 3:
        color = LEFT_COLOR
    else:
        color = RIGHT_COLOR

    head_size = 18
    body_width = 12
    body_length = 28

    # 向上
    if direction == 1:
        points = [
            (center_x, center_y - head_size),
            (center_x - head_size, center_y),
            (center_x + head_size, center_y)
        ]
        pygame.draw.polygon(screen, color, points)

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

    # 向下
    elif direction == 2:
        points = [
            (center_x, center_y + head_size),
            (center_x - head_size, center_y),
            (center_x + head_size, center_y)
        ]
        pygame.draw.polygon(screen, color, points)

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

    # 向左
    elif direction == 3:
        points = [
            (center_x - head_size, center_y),
            (center_x, center_y - head_size),
            (center_x, center_y + head_size)
        ]
        pygame.draw.polygon(screen, color, points)

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

    # 向右
    elif direction == 4:
        points = [
            (center_x + head_size, center_y),
            (center_x, center_y - head_size),
            (center_x, center_y + head_size)
        ]
        pygame.draw.polygon(screen, color, points)

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
# 十、绘制正在飞出的箭头
# ============================================================

def draw_flying_arrow(x, y, direction):
    """
    根据像素坐标绘制正在飞行的箭头。
    与普通箭头保持相同的形状和颜色。
    """

    if direction == 1:
        color = UP_COLOR
    elif direction == 2:
        color = DOWN_COLOR
    elif direction == 3:
        color = LEFT_COLOR
    else:
        color = RIGHT_COLOR

    head_size = 18
    body_width = 12
    body_length = 28

    # 向上
    if direction == 1:
        points = [
            (x, y - head_size),
            (x - head_size, y),
            (x + head_size, y)
        ]
        pygame.draw.polygon(screen, color, points)

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

    # 向下
    elif direction == 2:
        points = [
            (x, y + head_size),
            (x - head_size, y),
            (x + head_size, y)
        ]
        pygame.draw.polygon(screen, color, points)

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

    # 向左
    elif direction == 3:
        points = [
            (x - head_size, y),
            (x, y - head_size),
            (x, y + head_size)
        ]
        pygame.draw.polygon(screen, color, points)

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

    # 向右
    elif direction == 4:
        points = [
            (x + head_size, y),
            (x, y - head_size),
            (x, y + head_size)
        ]
        pygame.draw.polygon(screen, color, points)

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
# 十一、更新飞出动画
# ============================================================

def update_flying_arrows():
    """
    更新所有正在飞出的箭头。

    每一帧：
    1. 根据 direction 沿对应方向移动。
    2. 移动速度使用每个箭头自己的 fly_speed。
    3. 箭头完全飞出窗口后，从 flying_arrows 删除。
    """

    # 使用 flying_arrows[:] 遍历副本，
    # 这样循环过程中删除原列表元素不会出错。
    for arrow in flying_arrows[:]:

        # 只处理正在飞行的箭头
        if not arrow["is_flying"]:
            continue

        direction = arrow["direction"]
        speed = arrow["fly_speed"]

        # 向上
        if direction == 1:
            arrow["y"] -= speed

        # 向下
        elif direction == 2:
            arrow["y"] += speed

        # 向左
        elif direction == 3:
            arrow["x"] -= speed

        # 向右
        elif direction == 4:
            arrow["x"] += speed

        # 箭头图形最大尺寸大约为 18 像素，
        # 因此中心点离开窗口一定距离后再删除，
        # 保证整个箭头已经看不见。
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
# 十二、绘制棋盘
# ============================================================

def draw_board():
    """绘制背景、信息栏、网格、固定箭头和飞行箭头。"""

    # --------------------------------------------------------
    # 1. 白色背景
    # --------------------------------------------------------

    screen.fill(WHITE)

    # --------------------------------------------------------
    # 2. 顶部信息栏
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        (245, 245, 245),
        (0, 0, WINDOW_WIDTH, TOP_BAR_HEIGHT)
    )

    # 当前关卡
    level_text = FONT.render(
        f"第 {current_level} 关",
        True,
        BLACK
    )
    screen.blit(level_text, (20, 12))

    # 剩余箭头数量
    arrow_text = FONT.render(
        f"剩余箭头：{count_arrows()}",
        True,
        BLACK
    )
    screen.blit(arrow_text, (180, 12))

    # 剩余失误次数
    mistake_text = FONT.render(
        f"剩余失误：{mistakes_left}",
        True,
        RED if mistakes_left <= 1 else BLACK
    )
    screen.blit(mistake_text, (390, 12))

    # 操作提示
    tip_text = SMALL_FONT.render(
        "鼠标点击箭头即可操作",
        True,
        (100, 100, 100)
    )
    screen.blit(tip_text, (20, 48))

    # --------------------------------------------------------
    # 3. 绘制网格
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
    # 4. 绘制还留在棋盘中的箭头
    # --------------------------------------------------------

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            direction = board[row][col]

            if direction == 0:
                continue

            # 错误点击后的 300 毫秒内显示红色
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
    # 5. 绘制正在飞出的箭头
    # --------------------------------------------------------

    for arrow in flying_arrows:
        draw_flying_arrow(
            arrow["x"],
            arrow["y"],
            arrow["direction"]
        )


# ============================================================
# 十三、处理鼠标点击
# ============================================================

def handle_click(mouse_x, mouse_y):
    """
    处理鼠标左键点击。

    点击成功：
        箭头进入 flying_arrows，开始飞行动画。

    点击失败：
        箭头保持原位置，并扣除一次失误。
    """

    global mistakes_left
    global error_cell
    global error_time
    global game_state

    # 游戏结束后不再接受点击
    if game_state != "playing":
        return

    # 点击顶部信息栏不处理
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

    # 获取点击位置的箭头方向
    direction = board[row][col]

    # 点击空格不做任何操作
    if direction == 0:
        return

    # --------------------------------------------------------
    # 情况一：没有阻挡，可以飞出
    # --------------------------------------------------------

    if can_arrow_leave(row, col):

        # 计算箭头的初始像素中心
        start_x = col * CELL_SIZE + CELL_SIZE // 2
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

            # 按照要求增加 is_flying 状态
            "is_flying": True,

            # 按照要求使用 fly_speed = 15
            "fly_speed": 15
        })

        # 逻辑上从棋盘删除。
        # 注意：画面上的箭头不会立即消失，
        # 因为它现在由 flying_arrows 负责绘制。
        board[row][col] = 0

        # 清除之前的错误提示
        error_cell = None

    # --------------------------------------------------------
    # 情况二：有其他箭头阻挡
    # --------------------------------------------------------

    else:

        # 记录错误位置
        error_cell = (row, col)

        # 记录错误发生时间
        error_time = pygame.time.get_ticks()

        # 失误次数减 1
        mistakes_left -= 1

        # 失误次数用完，游戏失败
        if mistakes_left <= 0:
            mistakes_left = 0
            game_state = "lose"

    # 注意：
    # 这里不直接判断 win。
    # 必须等最后一个箭头真正飞出屏幕，
    # 从 flying_arrows 中删除以后，
    # 主循环才会把 game_state 设置成 win。


# ============================================================
# 十四、绘制游戏结束界面
# ============================================================

def draw_game_over():
    """绘制胜利或失败的半透明结束界面。"""

    # 半透明黑色遮罩
    overlay = pygame.Surface(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 120))

    screen.blit(overlay, (0, 0))

    # --------------------------------------------------------
    # 胜利
    # --------------------------------------------------------

    if game_state == "win":

        text = BIG_FONT.render(
            "恭喜通关！",
            True,
            GREEN
        )

        tip = FONT.render(
            f"第 {current_level} 关全部箭头已经消除",
            True,
            WHITE
        )

    # --------------------------------------------------------
    # 失败
    # --------------------------------------------------------

    else:

        text = BIG_FONT.render(
            "游戏失败",
            True,
            RED
        )

        tip = FONT.render(
            "失误次数已经用完",
            True,
            WHITE
        )

    # 居中显示
    text_rect = text.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 - 30
        )
    )

    tip_rect = tip.get_rect(
        center=(
            WINDOW_WIDTH // 2,
            WINDOW_HEIGHT // 2 + 30
        )
    )

    screen.blit(text, text_rect)
    screen.blit(tip, tip_rect)


# ============================================================
# 十五、游戏主循环
# ============================================================

def main():

    # 非常重要：
    # main() 会修改全局变量 game_state，
    # 所以必须声明 global game_state。
    global game_state

    # 游戏时钟
    clock = pygame.time.Clock()

    # 主循环
    while True:

        # ----------------------------------------------------
        # 1. 处理 Pygame 事件
        # ----------------------------------------------------

        for event in pygame.event.get():

            # 点击窗口关闭按钮
            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            # 鼠标按下
            if event.type == pygame.MOUSEBUTTONDOWN:

                # 只处理鼠标左键
                if event.button == 1:

                    mouse_x, mouse_y = event.pos

                    handle_click(
                        mouse_x,
                        mouse_y
                    )

        # ----------------------------------------------------
        # 2. 更新飞出动画
        # ----------------------------------------------------

        update_flying_arrows()

        # ----------------------------------------------------
        # 3. 判断胜利
        # ----------------------------------------------------
        #
        # 这里非常重要：
        # count_arrows() 同时统计：
        #   棋盘上的箭头
        #   正在飞行中的箭头
        #
        # 因此最后一个箭头必须先飞出屏幕，
        # 然后从 flying_arrows 中删除，
        # count_arrows() 才会变成 0。
        #

        if count_arrows() == 0 and game_state == "playing":
            game_state = "win"

        # ----------------------------------------------------
        # 4. 绘制游戏画面
        # ----------------------------------------------------

        draw_board()

        # ----------------------------------------------------
        # 5. 绘制结束界面
        # ----------------------------------------------------

        if game_state != "playing":
            draw_game_over()

        # ----------------------------------------------------
        # 6. 更新屏幕
        # ----------------------------------------------------

        pygame.display.flip()

        # 控制帧率为 60 FPS
        clock.tick(60)


# ============================================================
# 十六、程序入口
# ============================================================

if __name__ == "__main__":
    main()
