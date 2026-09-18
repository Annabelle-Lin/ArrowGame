# -*- coding: utf-8 -*-

"""
============================================================
《一箭又一箭》—— 现代极简风 UI 版本（粒子 + 音效 + 过渡版）
============================================================

玩法回顾：
    1. 10 × 10 棋盘，格子里放着箭头。
    2. 方向编码：0 = 空，1 = ↑，2 = ↓，3 = ←，4 = →。
    3. 鼠标点击箭头：
         · 前方同行 / 同列没有其他箭头 → 箭头飞出棋盘 + 粒子爆开 + "嗖"音效。
         · 前方有箭头阻挡             → 方块变红并抖动，失误 -1 + "咚"音效。
    4. 失误次数扣完 → 失败。
    5. 所有箭头全部飞出屏幕 → 单关通关；若已是最后一关 → 全部通关。

UI 设计要点：
    · 窗口 1000 × 700，背景米白 (249, 249, 246)
    · 背景叠加超大号棋盘格纹理（极浅灰），只增加质感不喧宾夺主
    · 左侧 10 × 10 棋盘，格子是带圆角的浅色方块，格间留 3px
    · 鼠标悬停在箭头格子上时：底色略变暗 + 箭头放大 1.05 倍
    · 右侧浅灰圆角数据面板，显示关卡 / 剩余箭头 / 剩余失误（红心）
    · 按钮统一深灰绿 (47, 79, 79)，鼠标悬停时颜色变浅并轻微放大
    · 箭头使用四种柔和色：薄荷绿 / 浅琥珀 / 天蓝 / 珊瑚粉

粒子系统：
    · 点击成功时，在箭头格子中心爆出 10 个与箭头同色的小粒子
    · 粒子随机向四周飞散，半径逐渐变小、透明度逐渐降低
    · 约 0.5 秒后消失

音效系统：
    · 使用 Python 标准库在内存中合成波形，无需任何外部音频文件
    · 成功飞出 → 400Hz→1200Hz 短促上升扫频 "嗖"
    · 被阻挡   → 200Hz 低频指数衰减 "咚"
    · 若系统无法初始化 mixer，游戏会自动静音运行，不会崩溃

屏幕淡入过渡：
    · 从“游戏中”切换到“失败 / 通关 / 全部通关”时，
      叠一层黑色遮罩，0.3 秒内由全黑渐渐消失。
    · 新增“全部通关”（complete）状态：第 5 关清空所有箭头后进入。
============================================================
"""

import sys
import math
import random
import io
import wave
import array

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
BG_CHECK_COLOR = (243, 243, 239)            # 背景棋盘格：更浅的灰（仅作纹理）
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

# “全部通关”界面的“返回首页”按钮（位置比主按钮更靠下）
COMPLETE_BTN = pygame.Rect(370, 500, 260, 68)

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

# 状态机：start / playing / lose / win / complete
game_state = "start"

flying_arrows = []                          # 正在飞出的箭头列表
blocked_fx = {}                             # 被阻挡的抖动动画：{(row, col): 起始时间}

FLY_SPEED = 15                              # 箭头每帧飞出速度（像素）
BLOCK_DURATION = 420                        # 被阻挡抖动持续时间（毫秒）

# ---------- 粒子系统 ----------
particles = []                              # 当前存活的所有粒子

# ---------- 屏幕淡入过渡 ----------
# transition_alpha：黑色遮罩的不透明度（0~255），255 = 全黑
# transition_start：遮罩开始淡出的时间戳（毫秒）
TRANSITION_DURATION = 300                   # 过渡总时长：0.3 秒
transition_alpha = 0.0
transition_start = 0
_transition_surface = None                  # 复用的黑色遮罩 Surface


# ============================================================
# 八、屏幕淡入过渡
# ============================================================

def start_transition():
    """
    启动一次“屏幕淡入”过渡。

    做法：状态切换的瞬间，让一层黑色遮罩从全黑（alpha=255）
    慢慢消失到全透明。视觉上就像新界面从黑色里浮现出来。
    """
    global transition_alpha, transition_start
    transition_alpha = 255.0
    transition_start = pygame.time.get_ticks()


def update_transition():
    """
    每帧更新遮罩透明度。

    用线性插值：elapsed 从 0 走到 TRANSITION_DURATION 时，
    alpha 从 255 线性降到 0。
    """
    global transition_alpha

    if transition_alpha <= 0.0:
        return

    elapsed = pygame.time.get_ticks() - transition_start
    if elapsed >= TRANSITION_DURATION:
        transition_alpha = 0.0
    else:
        transition_alpha = 255.0 * (1.0 - elapsed / TRANSITION_DURATION)


def draw_transition_overlay():
    """
    把黑色遮罩叠在所有 UI 之上。

    遮罩 Surface 只在第一次使用时创建，之后每帧仅调整 alpha，
    避免重复创建 Surface 造成的性能开销。
    """
    global _transition_surface

    if transition_alpha <= 0.5:
        return

    if _transition_surface is None:
        _transition_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        _transition_surface.fill((0, 0, 0))

    _transition_surface.set_alpha(int(transition_alpha))
    screen.blit(_transition_surface, (0, 0))


# ============================================================
# 九、音效系统（内存合成，无需外部文件）
# ============================================================

# 两个全局 Sound 对象；如果 mixer 初始化失败会保持为 None
sfx_fly = None
sfx_hit = None


def _synthesize_wav(samples, sample_rate, channels=1):
    """
    把 -1.0 ~ 1.0 的浮点采样打包成 16 位 PCM 的 WAV 字节流。
    """
    buf = io.BytesIO()

    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(channels)
        wav.setsampwidth(2)             # 16 位 = 2 字节
        wav.setframerate(sample_rate)

        pcm = array.array('h')
        for s in samples:
            if s > 1.0:
                s = 1.0
            elif s < -1.0:
                s = -1.0
            v = int(s * 32767)
            pcm.append(v)
            if channels == 2:
                pcm.append(v)

        wav.writeframes(pcm.tobytes())

    buf.seek(0)
    return buf


def _generate_sine_sweep(f_start, f_end, duration,
                         sample_rate, volume=0.4):
    """生成一段频率线性扫变的“嗖”音效。"""
    n = int(sample_rate * duration)
    samples = []
    phase = 0.0

    for i in range(n):
        t = i / n
        freq = f_start + (f_end - f_start) * t
        phase += 2.0 * math.pi * freq / sample_rate

        # 淡入淡出包络，避免爆音
        attack = 0.02
        release = 0.35
        if t < attack:
            env = t / attack
        elif t > 1.0 - release:
            env = (1.0 - t) / release
        else:
            env = 1.0

        samples.append(math.sin(phase) * env * volume)

    return samples


def _generate_hit(freq, duration, sample_rate, volume=0.55):
    """生成一段低频“咚”的撞击音效。"""
    n = int(sample_rate * duration)
    samples = []
    phase = 0.0

    for i in range(n):
        t = i / n
        f = freq * (1.0 - 0.4 * t)
        phase += 2.0 * math.pi * f / sample_rate

        wave_val = math.sin(phase) * 0.85 + math.sin(phase * 2.0) * 0.15
        env = math.exp(-t * 8.0) * (1.0 - t)
        samples.append(wave_val * env * volume)

    return samples


def init_sounds():
    """
    初始化音效系统：
        · 尝试初始化 mixer
        · 查询 mixer 实际采样率与声道
        · 合成“嗖”与“咚”两个 Sound
    失败时自动转为静音模式，不崩溃。
    """
    global sfx_fly, sfx_hit

    try:
        if pygame.mixer.get_init() is None:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512,
            )
    except pygame.error as e:
        print(f"[音效] 音频设备初始化失败，将以静音模式运行：{e}")
        return

    got = pygame.mixer.get_init()
    if got is None:
        print("[音效] mixer 未初始化，将以静音模式运行。")
        return

    sample_rate, _, channels = got

    # ---------- 1. 飞出音效：400Hz → 1200Hz，0.15 秒 ----------
    sweep_samples = _generate_sine_sweep(
        f_start=400.0,
        f_end=1200.0,
        duration=0.15,
        sample_rate=sample_rate,
        volume=0.35,
    )
    sweep_buf = _synthesize_wav(sweep_samples, sample_rate, channels)
    sfx_fly = pygame.mixer.Sound(file=sweep_buf)

    # ---------- 2. 撞击音效：200Hz 指数衰减，0.22 秒 ----------
    hit_samples = _generate_hit(
        freq=200.0,
        duration=0.22,
        sample_rate=sample_rate,
        volume=0.55,
    )
    hit_buf = _synthesize_wav(hit_samples, sample_rate, channels)
    sfx_hit = pygame.mixer.Sound(file=hit_buf)


def play_sfx(sound):
    """安全播放音效；sound 为 None 时静默忽略。"""
    if sound is not None:
        sound.play()


# 立即初始化音效
init_sounds()


# ============================================================
# 十、粒子系统
# ============================================================

class Particle:
    """
    单个小粒子。

    使用位置、速度、半径、透明度和年龄等简单属性来描述，
    每帧根据 dt（帧间隔秒数）进行物理更新：

        · 位置       → 按速度 × dt 位移
        · 速度       → 每帧轻微衰减（阻尼），使飞散更柔和
        · 半径       → 从初始半径线性收缩到 0
        · 透明度     → 从 255 线性衰减到 0
        · 存活时间   → 超过 lifetime 秒后自动标记死亡
    """

    def __init__(self, x, y, color):
        self.x = float(x)
        self.y = float(y)
        self.color = color

        # 随机方向 + 随机初速度（像素/秒）
        angle = random.uniform(0.0, math.tau)
        speed = random.uniform(90.0, 200.0)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed

        # 随机初始半径
        self.start_radius = random.uniform(2.5, 5.0)
        self.radius = self.start_radius

        # 生命周期：约 0.5 秒
        self.age = 0.0
        self.lifetime = 0.5
        self.alpha = 255.0
        self.alive = True

    def update(self, dt):
        """根据帧间隔 dt（秒）更新粒子状态。"""
        if not self.alive:
            return

        self.age += dt
        if self.age >= self.lifetime:
            self.alive = False
            return

        self.x += self.vx * dt
        self.y += self.vy * dt

        # 与帧率无关的阻尼
        damping = 0.90 ** (dt * 60.0)
        self.vx *= damping
        self.vy *= damping

        t = self.age / self.lifetime
        self.radius = self.start_radius * (1.0 - t)
        self.alpha = 255.0 * (1.0 - t)

    def draw(self, surface):
        """把粒子画到目标 Surface 上（带透明度）。"""
        r = int(round(self.radius))
        a = int(self.alpha)
        if r < 1 or a <= 0:
            return

        size = r * 2 + 2
        temp = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(
            temp,
            (self.color[0], self.color[1], self.color[2], a),
            (size // 2, size // 2),
            r
        )
        surface.blit(temp, (self.x - size // 2, self.y - size // 2))


def spawn_particles(x, y, color, count=10):
    """在指定位置生成若干个粒子。"""
    for _ in range(count):
        particles.append(Particle(x, y, color))


def update_particles(dt):
    """每帧更新所有粒子，并移除已经死亡的粒子。"""
    for p in particles[:]:
        p.update(dt)
        if not p.alive:
            particles.remove(p)


def draw_particles():
    """把所有存活的粒子绘制到屏幕上。"""
    for p in particles:
        p.draw(screen)


# ============================================================
# 十一、通用绘制工具
# ============================================================

# 背景棋盘格纹理缓存
_bg_surface = None


def draw_background():
    """
    绘制整体背景：米白色底 + 超大号棋盘格纹理。
    纹理一次性绘制到离屏 Surface 并缓存复用。
    """
    global _bg_surface

    if _bg_surface is None:
        _bg_surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        _bg_surface.fill(BG_COLOR)

        tile = 80
        rows = WINDOW_HEIGHT // tile + 2
        cols = WINDOW_WIDTH // tile + 2

        for r in range(rows):
            for c in range(cols):
                if (r + c) % 2 == 0:
                    pygame.draw.rect(
                        _bg_surface,
                        BG_CHECK_COLOR,
                        (c * tile, r * tile, tile, tile)
                    )

    screen.blit(_bg_surface, (0, 0))


def darken(color, factor=0.88):
    """将颜色按比例变暗。"""
    return (
        max(0, int(color[0] * factor)),
        max(0, int(color[1] * factor)),
        max(0, int(color[2] * factor)),
    )


def draw_button(rect, text, font, radius=15):
    """
    绘制一个圆角按钮，带两种悬停反馈：
        · 颜色：深灰绿 → 较浅灰绿
        · 大小：整体轻微放大 1.05 倍（smoothscale 平滑缩放）
    """
    hovered = rect.collidepoint(pygame.mouse.get_pos())
    color = BTN_HOVER_COLOR if hovered else BTN_COLOR

    if hovered:
        scale = 1.05
        w = int(rect.width * scale)
        h = int(rect.height * scale)

        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0, 0, w, h), border_radius=radius)

        text_surface = font.render(text, True, BTN_TEXT_COLOR)
        surf.blit(text_surface, text_surface.get_rect(center=(w // 2, h // 2)))

        surf = pygame.transform.smoothscale(surf, (w, h))
        screen.blit(surf, surf.get_rect(center=rect.center))
    else:
        pygame.draw.rect(screen, color, rect, border_radius=radius)
        text_surface = font.render(text, True, BTN_TEXT_COLOR)
        screen.blit(text_surface, text_surface.get_rect(center=rect.center))


def draw_arrow_icon(surface, cx, cy, direction, color, scale=1.0):
    """
    在指定位置绘制一个箭头图形。
    先用“向上箭头”的 7 个顶点做原型，再根据方向旋转。
    """
    L = 16 * scale
    HL = 14 * scale
    HW = 13 * scale
    SW = 5.5 * scale

    base_points = [
        (0, -L),
        (HW, -L + HL),
        (SW, -L + HL),
        (SW, L),
        (-SW, L),
        (-SW, -L + HL),
        (-HW, -L + HL),
    ]

    points = []
    for dx, dy in base_points:
        if direction == 1:
            rx, ry = dx, dy
        elif direction == 2:
            rx, ry = -dx, -dy
        elif direction == 3:
            rx, ry = dy, -dx
        else:
            rx, ry = -dy, dx
        points.append((cx + rx, cy + ry))

    pygame.draw.polygon(surface, color, points)


def draw_heart(surface, cx, cy, size, color):
    """用两个圆 + 一个三角形拼出一个爱心。"""
    r = size * 0.27

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

    pygame.draw.polygon(
        surface, color,
        [
            (cx - size * 0.47, cy - size * 0.06),
            (cx + size * 0.47, cy - size * 0.06),
            (cx, cy + size * 0.48),
        ]
    )


# ============================================================
# 十二、关卡加载与状态切换
# ============================================================

def load_level(level_number):
    """
    加载指定关卡：
        · 复制一份关卡数据，避免破坏原始数组
        · 重置失误次数、抖动动画、飞行动画、粒子、过渡遮罩
        · 把游戏状态切换到 playing
    """
    global current_level, board, mistakes_left, game_state
    global transition_alpha

    level_number = max(1, min(level_number, TOTAL_LEVELS))
    current_level = level_number

    board = [row[:] for row in levels[current_level - 1]]

    mistakes_left = 3
    blocked_fx.clear()
    flying_arrows.clear()
    particles.clear()
    transition_alpha = 0.0          # 进入新关卡时清空遮罩

    game_state = "playing"


def start_new_game():
    """从第 1 关开始一整局新游戏。"""
    load_level(1)


def restart_current_level():
    """重新加载当前关卡（失败后使用）。"""
    load_level(current_level)


def go_to_next_level():
    """通关后的“下一关”逻辑：第 1～4 关进入下一关。"""
    if current_level < TOTAL_LEVELS:
        load_level(current_level + 1)
    else:
        start_new_game()


# ============================================================
# 十三、游戏逻辑：统计与判定
# ============================================================

def count_arrows():
    """统计还没完全飞出屏幕的箭头总数。"""
    count = 0
    for row in board:
        for cell in row:
            if cell != 0:
                count += 1
    count += len(flying_arrows)
    return count


def can_arrow_leave(row, col):
    """判断 (row, col) 处的箭头前方是否有其他箭头阻挡。"""
    direction = board[row][col]

    if direction == 1:
        for r in range(row - 1, -1, -1):
            if board[r][col] != 0:
                return False
    elif direction == 2:
        for r in range(row + 1, GRID_SIZE):
            if board[r][col] != 0:
                return False
    elif direction == 3:
        for c in range(col - 1, -1, -1):
            if board[row][c] != 0:
                return False
    elif direction == 4:
        for c in range(col + 1, GRID_SIZE):
            if board[row][c] != 0:
                return False

    return True


# ============================================================
# 十四、飞行动画更新
# ============================================================

def update_flying_arrows():
    """每帧更新所有正在飞出的箭头。"""
    for arrow in flying_arrows[:]:
        dx, dy = DIR_VEC[arrow["direction"]]
        arrow["x"] += dx * FLY_SPEED
        arrow["y"] += dy * FLY_SPEED
        arrow["dist"] += FLY_SPEED

        arrow["alpha"] = max(60.0, 255.0 - arrow["dist"] * 0.36)

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
# 十五、开始界面
# ============================================================

def draw_start_screen():
    """开始界面：装饰箭头 + 大标题 + 副标题 + 开始按钮。"""
    draw_background()

    # 装饰：一排四个彩色箭头方块
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

    title = TITLE_FONT.render("一箭又一箭", True, TEXT_DARK)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 258)))

    subtitle = SUBTITLE_FONT.render(
        "点击箭头，让它们依次飞出棋盘", True, TEXT_SUB
    )
    screen.blit(
        subtitle, subtitle.get_rect(center=(WINDOW_WIDTH // 2, 330))
    )

    draw_button(MAIN_BTN_RECT, "开始游戏", BUTTON_FONT)

    tip = SMALL_FONT.render(
        f"共 {TOTAL_LEVELS} 个关卡  ·  每关 3 次失误机会", True, TEXT_SUB
    )
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 560)))


# ============================================================
# 十六、游戏界面：棋盘
# ============================================================

def cell_topleft(row, col):
    """返回第 row 行第 col 列格子的左上角像素坐标。"""
    return BOARD_X + col * CELL_STEP, BOARD_Y + row * CELL_STEP


def draw_board():
    """绘制左侧 10 × 10 棋盘。"""
    now = pygame.time.get_ticks()

    # 计算鼠标当前悬停的格子
    mx, my = pygame.mouse.get_pos()
    hover_row, hover_col = -1, -1
    if (BOARD_X <= mx < BOARD_X + BOARD_PIXEL and
            BOARD_Y <= my < BOARD_Y + BOARD_PIXEL):
        hover_col = (mx - BOARD_X) // CELL_STEP
        hover_row = (my - BOARD_Y) // CELL_STEP

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):

            x, y = cell_topleft(row, col)
            direction = board[row][col]
            rect = pygame.Rect(x, y, CELL_SIZE, CELL_SIZE)

            # 空格子
            if direction == 0:
                pygame.draw.rect(
                    screen, EMPTY_CELL_COLOR, rect, border_radius=14
                )
                continue

            # 被阻挡抖动
            blocked = False
            offset_x = 0

            start_time = blocked_fx.get((row, col))
            if start_time is not None:
                elapsed = now - start_time
                if elapsed < BLOCK_DURATION:
                    blocked = True
                    progress = elapsed / BLOCK_DURATION
                    offset_x = (
                        math.sin(progress * math.pi * 6)
                        * 7
                        * (1 - progress)
                    )
                else:
                    del blocked_fx[(row, col)]

            # 鼠标悬停
            is_hover = (
                not blocked
                and row == hover_row
                and col == hover_col
            )

            # 方块颜色
            if blocked:
                color = BLOCKED_COLOR
            elif is_hover:
                color = darken(ARROW_COLORS[direction], 0.86)
            else:
                color = ARROW_COLORS[direction]

            rect.x += int(offset_x)
            pygame.draw.rect(screen, color, rect, border_radius=14)

            # 白色箭头（悬停放大 1.05 倍）
            arrow_scale = 1.05 if is_hover else 1.0
            draw_arrow_icon(
                screen, rect.centerx, rect.centery,
                direction, (255, 255, 255),
                scale=arrow_scale
            )

    # 飞出箭头
    for arrow in flying_arrows:
        draw_flying_arrow(arrow)


def draw_flying_arrow(arrow):
    """绘制一个正在飞出的箭头（带淡出效果）。"""
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
# 十七、游戏界面：右侧数据面板
# ============================================================

def draw_info_card(y, label, value):
    """绘制一张白色信息卡片（标签 + 数值）。"""
    rect = pygame.Rect(PANEL_X + 24, y, PANEL_W - 48, 105)
    pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=18)

    label_surf = LABEL_FONT.render(label, True, TEXT_SUB)
    screen.blit(label_surf, (rect.x + 20, rect.y + 16))

    value_surf = VALUE_FONT.render(value, True, TEXT_DARK)
    screen.blit(value_surf, (rect.x + 20, rect.y + 52))


def draw_hearts_card(y, label, hearts):
    """绘制“剩余失误”卡片（红心数量表示剩余机会）。"""
    rect = pygame.Rect(PANEL_X + 24, y, PANEL_W - 48, 105)
    pygame.draw.rect(screen, CARD_COLOR, rect, border_radius=18)

    label_surf = LABEL_FONT.render(label, True, TEXT_SUB)
    screen.blit(label_surf, (rect.x + 20, rect.y + 16))

    for i in range(3):
        cx = rect.x + 36 + i * 44
        cy = rect.y + 72
        color = HEART_COLOR if i < hearts else HEART_EMPTY_COLOR
        draw_heart(screen, cx, cy, 30, color)


def draw_panel():
    """绘制右侧浅灰圆角数据面板。"""
    panel_rect = pygame.Rect(PANEL_X, PANEL_Y, PANEL_W, PANEL_H)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=24)

    card_y = PANEL_Y + 28

    draw_info_card(card_y, "当前关卡", f"{current_level} / {TOTAL_LEVELS}")
    draw_info_card(card_y + 120, "剩余箭头", f"{count_arrows()}")
    draw_hearts_card(card_y + 240, "剩余失误", mistakes_left)

    tip1 = SMALL_FONT.render("点击箭头让它飞出棋盘", True, TEXT_SUB)
    tip2 = SMALL_FONT.render("前方有阻挡会扣除失误", True, TEXT_SUB)

    screen.blit(tip1, tip1.get_rect(center=(PANEL_X + PANEL_W // 2, 452)))
    screen.blit(tip2, tip2.get_rect(center=(PANEL_X + PANEL_W // 2, 478)))

    draw_button(RESTART_BTN, "重新开始", PANEL_BTN_FONT)
    draw_button(HOME_BTN, "返回首页", PANEL_BTN_FONT)


def draw_game_screen():
    """完整游戏画面：背景 → 棋盘 → 粒子 → 右侧面板。"""
    draw_background()
    draw_board()
    draw_particles()
    draw_panel()


# ============================================================
# 十八、失败界面
# ============================================================

def draw_lose_screen():
    """
    失败界面（已去掉图标）：
        · 柔和红标题
        · 提示文字
        · 重新开始按钮
    """
    draw_background()

    title = PAGE_TITLE_FONT.render("挑战失败", True, (226, 106, 106))
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 240)))

    tip = BODY_FONT.render(
        f"第 {current_level} 关的箭头挡住了你", True, TEXT_SUB
    )
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 320)))

    draw_button(MAIN_BTN_RECT, "重新开始", BUTTON_FONT)


# ============================================================
# 十九、单关通关界面
# ============================================================

def draw_win_screen():
    """
    单关通关界面（第 1～4 关，已去掉图标）：
        · “通关！” 标题
        · “恭喜完成第 N 关”提示
        · “下一关”按钮
    """
    draw_background()

    title = PAGE_TITLE_FONT.render("通关！", True, (95, 170, 120))
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 240)))

    tip_text = f"恭喜完成第 {current_level} 关"
    tip = BODY_FONT.render(tip_text, True, TEXT_SUB)
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 320)))

    draw_button(MAIN_BTN_RECT, "下一关", BUTTON_FONT)


# ============================================================
# 二十、全部通关界面（状态：complete）
# ============================================================

def draw_complete_screen():
    """
    全部通关界面（已去掉图标）：
        · “恭喜通关！” 大标题
        · “你完成了所有挑战！” 副标题
        · “返回首页”按钮
    """
    draw_background()

    title = PAGE_TITLE_FONT.render("恭喜通关！", True, TEXT_DARK)
    screen.blit(title, title.get_rect(center=(WINDOW_WIDTH // 2, 240)))

    tip = BODY_FONT.render(
        "你完成了所有挑战！", True, TEXT_SUB
    )
    screen.blit(tip, tip.get_rect(center=(WINDOW_WIDTH // 2, 320)))

    draw_button(COMPLETE_BTN, "返回首页", BUTTON_FONT)


# ============================================================
# 二十一、事件处理
# ============================================================

def handle_board_click(mx, my):
    """
    处理玩家点击棋盘的操作。

    可以飞出  → 播放“嗖”音效 + 生成飞行动画 + 爆出同色粒子
    被阻挡   → 播放“咚”音效 + 记录抖动动画，失误次数 -1
               失误次数扣完 → 进入失败状态，同时启动淡入过渡
    """
    global mistakes_left, game_state

    if not (BOARD_X <= mx < BOARD_X + BOARD_PIXEL and
            BOARD_Y <= my < BOARD_Y + BOARD_PIXEL):
        return

    col = (mx - BOARD_X) // CELL_STEP
    row = (my - BOARD_Y) // CELL_STEP

    if not (0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE):
        return

    direction = board[row][col]
    if direction == 0:
        return

    # ---------- 情况一：前方畅通，箭头飞出 ----------
    if can_arrow_leave(row, col):
        cx = BOARD_X + col * CELL_STEP + CELL_SIZE // 2
        cy = BOARD_Y + row * CELL_STEP + CELL_SIZE // 2

        play_sfx(sfx_fly)
        spawn_particles(cx, cy, ARROW_COLORS[direction], count=10)

        flying_arrows.append({
            "x": float(cx),
            "y": float(cy),
            "direction": direction,
            "alpha": 255.0,
            "dist": 0.0,
        })

        board[row][col] = 0
        blocked_fx.pop((row, col), None)

    # ---------- 情况二：前方有阻挡，扣一次失误 ----------
    else:
        play_sfx(sfx_hit)
        blocked_fx[(row, col)] = pygame.time.get_ticks()

        mistakes_left -= 1
        if mistakes_left <= 0:
            mistakes_left = 0
            game_state = "lose"
            start_transition()      # 从“游戏中”到“失败”的屏幕淡入


def handle_menu_click(mx, my):
    """处理开始 / 失败 / 通关 / 全部通关界面上的按钮点击。"""
    global game_state

    # ---------- 开始界面 ----------
    if game_state == "start":
        if MAIN_BTN_RECT.collidepoint(mx, my):
            start_new_game()

    # ---------- 失败界面 ----------
    elif game_state == "lose":
        if MAIN_BTN_RECT.collidepoint(mx, my):
            restart_current_level()

    # ---------- 单关通关界面 ----------
    elif game_state == "win":
        if MAIN_BTN_RECT.collidepoint(mx, my):
            go_to_next_level()

    # ---------- 全部通关界面 ----------
    elif game_state == "complete":
        if COMPLETE_BTN.collidepoint(mx, my):
            # 重置一切并回到首页
            load_level(1)
            game_state = "start"


# ============================================================
# 二十二、主循环
# ============================================================

def main():
    """
    游戏主循环。

    状态流转：

        start  ──开始游戏──▶  playing
                                │
                失败 ◀──────────┼──────────▶ 通关 / 全部通关
                 │              │              │
            重新开始        （清空所有箭头）  下一关 / 返回首页
                 │                             │
                 ▼                             ▼
              playing                    playing / start / complete

    每当从 playing 切换到 lose / win / complete，
    调用 start_transition() 启动屏幕淡入。
    """
    global game_state

    while True:

        # 帧间隔（秒），用于粒子的时间相关更新
        dt = clock.tick(FPS) / 1000.0

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
                    if RESTART_BTN.collidepoint(mx, my):
                        restart_current_level()
                    elif HOME_BTN.collidepoint(mx, my):
                        # 回首页时清理所有动画 / 粒子，避免残留
                        game_state = "start"
                        flying_arrows.clear()
                        particles.clear()
                        blocked_fx.clear()
                    else:
                        handle_board_click(mx, my)
                else:
                    handle_menu_click(mx, my)

        # ====================================================
        # 2. 逻辑更新
        # ====================================================
        # 粒子在所有状态下都继续更新，这样即使切到胜利 / 失败界面，
        # 残留的粒子也能自然淡出消失。
        update_particles(dt)

        if game_state == "playing":
            update_flying_arrows()

            # 棋盘和飞行动画里都没有箭头了 → 通关
            if count_arrows() == 0:
                if current_level < TOTAL_LEVELS:
                    game_state = "win"
                else:
                    game_state = "complete"
                start_transition()      # 从“游戏中”到“通关/全部通关”的屏幕淡入

        # 更新过渡遮罩透明度（任何状态都执行）
        update_transition()

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
        elif game_state == "complete":
            draw_complete_screen()

        # ====================================================
        # 4. 过渡遮罩画在最上层（覆盖所有 UI）
        # ====================================================
        draw_transition_overlay()

        # ====================================================
        # 5. 刷新屏幕
        # ====================================================
        pygame.display.flip()


# ============================================================
# 二十三、程序入口
# ============================================================

if __name__ == "__main__":
    main()