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
   - 如果箭头前方没有其他箭头，它就可以飞出棋盘并消失。
   - 如果箭头前方有其他箭头挡住，它不能消除，并扣除 1 次失误。
5. 初始拥有 3 次失误机会。
6. 所有箭头消除后，游戏胜利。
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

# 棋盘大小
GRID_SIZE = 10

# 每个格子的像素大小
CELL_SIZE = 60

# 棋盘总大小
BOARD_SIZE = GRID_SIZE * CELL_SIZE

# 顶部信息栏高度
TOP_BAR_HEIGHT = 80

# 游戏窗口大小
WINDOW_WIDTH = BOARD_SIZE
WINDOW_HEIGHT = BOARD_SIZE + TOP_BAR_HEIGHT

# 创建游戏窗口
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# 设置窗口标题
pygame.display.set_caption("一箭又一箭")


# ============================================================
# 三、颜色
# ============================================================

# 背景颜色：白色
WHITE = (255, 255, 255)

# 网格颜色：灰色
GRAY = (180, 180, 180)

# 文字颜色
BLACK = (30, 30, 30)

# 不同方向箭头的颜色
UP_COLOR = (70, 130, 255)       # 蓝色：上
DOWN_COLOR = (80, 190, 100)     # 绿色：下
LEFT_COLOR = (180, 100, 220)    # 紫色：左
RIGHT_COLOR = (255, 150, 50)    # 橙色：右

# 点击失败时的提示颜色
RED = (230, 60, 60)

# 成功提示颜色
GREEN = (40, 170, 80)


# ============================================================
# 四、字体
# ============================================================

# 使用系统字体。
# 如果你的电脑没有 SimHei，可以改成 Microsoft YaHei。
FONT = pygame.font.SysFont("SimHei", 24)
SMALL_FONT = pygame.font.SysFont("SimHei", 18)
BIG_FONT = pygame.font.SysFont("SimHei", 42)


# ============================================================
# 五、第1关地图
# ============================================================

"""
二维数组：

0 = 空格
1 = ↑
2 = ↓
3 = ←
4 = →

设计思路：
每一个箭头最终都可以通过鼠标点击让它飞出棋盘。

例如：

→ → → → 
这些箭头如果右侧没有其他箭头，
就可以从右边飞出去。

玩家需要根据箭头之间的遮挡关系，
寻找一个合适的消除顺序。

下面是第1关的初始布局。
"""

level1 = [
    [0, 0, 0, 0, 4, 0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0, 0, 0, 2, 0, 0],
    [0, 0, 0, 0, 0, 4, 0, 0, 0, 0],
    [0, 3, 0, 0, 0, 0, 0, 0, 0, 2],
    [0, 0, 0, 1, 0, 0, 0, 0, 3, 0],
    [0, 0, 4, 0, 0, 0, 2, 0, 0, 0],
    [0, 0, 0, 0, 3, 0, 0, 1, 0, 0],
    [0, 2, 0, 0, 0, 0, 4, 0, 0, 0],
    [0, 0, 0, 3, 0, 0, 0, 0, 1, 0],
    [0, 0, 4, 0, 0, 0, 0, 2, 0, 0]
]


# ============================================================
# 六、游戏变量
# ============================================================

# 当前关卡
current_level = 1

# 当前地图
board = level1

# 初始失误次数
mistakes_left = 3

# 点击失败后，用于让箭头短暂变红
error_cell = None

# 记录错误提示开始的时间
error_time = 0

# 游戏状态
# "playing" = 游戏中
# "win" = 胜利
# "lose" = 失败
game_state = "playing"


# ============================================================
# 七、计算剩余箭头数量
# ============================================================

def count_arrows():
    """
    统计当前棋盘中还剩多少个箭头。

    遍历二维数组：
    如果不是 0，就说明这一格有箭头。
    """

    count = 0

    for row in board:
        for cell in row:
            if cell != 0:
                count += 1

    return count


# ============================================================
# 八、判断某个箭头前方是否有阻挡
# ============================================================

def can_arrow_leave(row, col):
    """
    判断指定位置的箭头能不能飞出棋盘。

    参数：
        row：箭头所在的行
        col：箭头所在的列

    返回：
        True  ：前方没有箭头，可以飞出
        False ：前方存在箭头，被挡住

    核心思想：

    ↑：
    检查同一列上方的格子

    ↓：
    检查同一列下方的格子

    ←：
    检查同一行左边的格子

    →：
    检查同一行右边的格子
    """

    direction = board[row][col]

    # --------------------------------------------------------
    # 1 = 向上
    # --------------------------------------------------------

    if direction == 1:

        # 从当前行的上一行开始检查
        for r in range(row - 1, -1, -1):

            # 如果发现其他箭头
            if board[r][col] != 0:
                return False

    # --------------------------------------------------------
    # 2 = 向下
    # --------------------------------------------------------

    elif direction == 2:

        # 从当前行的下一行开始检查
        for r in range(row + 1, GRID_SIZE):

            if board[r][col] != 0:
                return False

    # --------------------------------------------------------
    # 3 = 向左
    # --------------------------------------------------------

    elif direction == 3:

        # 从当前列的左边开始检查
        for c in range(col - 1, -1, -1):

            if board[row][c] != 0:
                return False

    # --------------------------------------------------------
    # 4 = 向右
    # --------------------------------------------------------

    elif direction == 4:

        # 从当前列的右边开始检查
        for c in range(col + 1, GRID_SIZE):

            if board[row][c] != 0:
                return False

    # 如果整个方向都没有找到箭头
    return True


# ============================================================
# 九、绘制箭头
# ============================================================

def draw_arrow(row, col, direction, error=False):
    """
    在指定的网格位置绘制一个箭头。

    row：
        箭头所在行

    col：
        箭头所在列

    direction：
        1 = 上
        2 = 下
        3 = 左
        4 = 右

    error：
        如果为 True，则使用红色表示点击失败。
    """

    # 计算这个格子的左上角坐标
    x = col * CELL_SIZE
    y = TOP_BAR_HEIGHT + row * CELL_SIZE

    # 箭头中心点
    center_x = x + CELL_SIZE // 2
    center_y = y + CELL_SIZE // 2

    # 如果刚刚点击失败，则显示红色
    if error:
        color = RED

    else:

        # 根据方向选择颜色
        if direction == 1:
            color = UP_COLOR

        elif direction == 2:
            color = DOWN_COLOR

        elif direction == 3:
            color = LEFT_COLOR

        else:
            color = RIGHT_COLOR

    # --------------------------------------------------------
    # 箭头大小
    # --------------------------------------------------------

    head_size = 18
    body_width = 12
    body_length = 28

    # --------------------------------------------------------
    # 向上箭头
    # --------------------------------------------------------

    if direction == 1:

        # 三角形箭头头部
        points = [
            (center_x, center_y - head_size),
            (center_x - head_size, center_y),
            (center_x + head_size, center_y)
        ]

        pygame.draw.polygon(screen, color, points)

        # 箭身
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

    # --------------------------------------------------------
    # 向下箭头
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 向左箭头
    # --------------------------------------------------------

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

    # --------------------------------------------------------
    # 向右箭头
    # --------------------------------------------------------

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
# 十、绘制棋盘
# ============================================================

def draw_board():
    """
    绘制整个游戏画面。

    包括：
    1. 白色背景
    2. 顶部信息栏
    3. 10 × 10 网格
    4. 所有箭头
    """

    # --------------------------------------------------------
    # 1. 绘制白色背景
    # --------------------------------------------------------

    screen.fill(WHITE)

    # --------------------------------------------------------
    # 2. 绘制顶部信息栏
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

    screen.blit(
        level_text,
        (20, 12)
    )

    # 剩余箭头数量
    arrow_text = FONT.render(
        f"剩余箭头：{count_arrows()}",
        True,
        BLACK
    )

    screen.blit(
        arrow_text,
        (180, 12)
    )

    # 剩余失误次数
    mistake_text = FONT.render(
        f"剩余失误：{mistakes_left}",
        True,
        RED if mistakes_left <= 1 else BLACK
    )

    screen.blit(
        mistake_text,
        (390, 12)
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
    # 3. 绘制网格线
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
    # 4. 绘制所有箭头
    # --------------------------------------------------------

    for row in range(GRID_SIZE):

        for col in range(GRID_SIZE):

            direction = board[row][col]

            # 0 代表空格，不需要绘制
            if direction == 0:
                continue

            # 判断当前箭头是否正在显示错误状态
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


# ============================================================
# 十一、处理鼠标点击
# ============================================================

def handle_click(mouse_x, mouse_y):
    """
    处理玩家的鼠标点击。

    鼠标坐标：
        mouse_x：鼠标横坐标
        mouse_y：鼠标纵坐标

    根据坐标计算玩家点击的是第几行、第几列。
    """

    global mistakes_left
    global error_cell
    global error_time
    global game_state

    # --------------------------------------------------------
    # 如果游戏已经结束，就不再处理点击
    # --------------------------------------------------------

    if game_state != "playing":
        return

    # --------------------------------------------------------
    # 如果点击的是顶部信息栏，也不处理
    # --------------------------------------------------------

    if mouse_y < TOP_BAR_HEIGHT:
        return

    # --------------------------------------------------------
    # 根据鼠标坐标计算网格位置
    # --------------------------------------------------------

    col = mouse_x // CELL_SIZE

    row = (mouse_y - TOP_BAR_HEIGHT) // CELL_SIZE

    # 防止坐标超出棋盘
    if row < 0 or row >= GRID_SIZE:
        return

    if col < 0 or col >= GRID_SIZE:
        return

    # --------------------------------------------------------
    # 获取玩家点击的格子
    # --------------------------------------------------------

    direction = board[row][col]

    # 如果点击的是空格，什么都不做
    if direction == 0:
        return

    # --------------------------------------------------------
    # 判断箭头前方是否有阻挡
    # --------------------------------------------------------

    if can_arrow_leave(row, col):

        # ====================================================
        # 情况一：前方没有箭头
        # ====================================================

        # 直接把二维数组中的箭头变成 0
        #
        # 这就相当于：
        # “箭头飞出了棋盘”
        #
        # 因为绘制函数遇到 0 就不会绘制。
        board[row][col] = 0

        # 清除错误状态
        error_cell = None

    else:

        # ====================================================
        # 情况二：前方有箭头阻挡
        # ====================================================

        # 记录当前错误位置
        error_cell = (row, col)

        # 记录错误发生的时间
        error_time = pygame.time.get_ticks()

        # 失误次数 -1
        mistakes_left -= 1

        # 如果失误次数已经用完
        if mistakes_left <= 0:
            game_state = "lose"


    # ========================================================
    # 检查是否已经消除所有箭头
    # ========================================================

    if count_arrows() == 0:
        game_state = "win"


# ============================================================
# 十二、绘制游戏结束界面
# ============================================================

def draw_game_over():
    """
    游戏结束后显示胜利或失败信息。
    """

    # 创建半透明遮罩
    overlay = pygame.Surface(
        (WINDOW_WIDTH, WINDOW_HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 120))

    screen.blit(
        overlay,
        (0, 0)
    )

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
            "第 1 关全部箭头已经消除",
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
        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 30)
    )

    tip_rect = tip.get_rect(
        center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 30)
    )

    screen.blit(text, text_rect)

    screen.blit(tip, tip_rect)


# ============================================================
# 十三、游戏主循环
# ============================================================

def main():

    # 游戏时钟
    clock = pygame.time.Clock()

    # 主循环
    while True:

        # ----------------------------------------------------
        # 处理所有 Pygame 事件
        # ----------------------------------------------------

        for event in pygame.event.get():

            # 点击窗口右上角关闭按钮
            if event.type == pygame.QUIT:

                pygame.quit()

                sys.exit()

            # 鼠标左键点击
            if event.type == pygame.MOUSEBUTTONDOWN:

                # 只处理鼠标左键
                if event.button == 1:

                    # 获取鼠标当前位置
                    mouse_x, mouse_y = event.pos

                    # 处理点击
                    handle_click(
                        mouse_x,
                        mouse_y
                    )

        # ----------------------------------------------------
        # 绘制游戏画面
        # ----------------------------------------------------

        draw_board()

        # ----------------------------------------------------
        # 如果游戏结束，绘制结束界面
        # ----------------------------------------------------

        if game_state != "playing":

            draw_game_over()

        # ----------------------------------------------------
        # 更新屏幕
        # ----------------------------------------------------

        pygame.display.flip()

        # 控制游戏帧率为 60 FPS
        clock.tick(60)


# ============================================================
# 十四、程序入口
# ============================================================

if __name__ == "__main__":

    main()

