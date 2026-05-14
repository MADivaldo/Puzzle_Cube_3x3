"""
Protótipo Pygame – Cubo 3x3 Artefato/Chave v6

Correção estrutural:
- O cubo agora é representado por stickers em posições 3D reais.
- Cada rotação gira uma fatia/slice do cubo em torno de um eixo 3D.
- Isso remove o problema de "legado das faces", onde topo/baixo podiam parecer fixos
  porque a lógica anterior ainda dependia de faces nomeadas F/U/D/L/R.

Controles:
- WASD: navega entre peças da face atual.
- Ao sair por uma borda: troca para a face vizinha visualmente correta.
- Click + Mouse: gira apenas o preview visual.
- F: realinha a face atual de frente.
- Espaço: fixa/desfixa peça.
- Com peça fixada:
    W: gira coluna selecionada para cima.
    S: gira coluna selecionada para baixo.
    A: gira linha selecionada para esquerda.
    D: gira linha selecionada para direita.
    Q: gira face atual anti-horário.
    E: gira face atual horário.
- R ou botão Aleatorizar: embaralha.
- Botão Resetar faces: volta ao estado correto.
- Esc: sair.
"""

import math
import random
import sys
from dataclasses import dataclass

import pygame


WIDTH, HEIGHT = 1280, 760
FPS = 60

BG = (18, 18, 20)
PANEL = (35, 34, 38)
BUTTON = (62, 55, 45)
BUTTON_HOVER = (88, 72, 48)
TEXT = (240, 235, 225)
MUTED = (180, 174, 162)
GOLD = (255, 200, 55)
LOCK = (255, 235, 125)
GRID = (28, 28, 30)
BLACK = (10, 10, 12)

FACE_TO_VEC = {
    "F": (0, 0, 1),
    "B": (0, 0, -1),
    "U": (0, 1, 0),
    "D": (0, -1, 0),
    "R": (1, 0, 0),
    "L": (-1, 0, 0),
}

VEC_TO_FACE = {v: k for k, v in FACE_TO_VEC.items()}

FACE_COLORS = {
    "F": (242, 210, 45),    # amarelo
    "B": (238, 238, 230),   # branco
    "R": (55, 125, 230),    # azul
    "L": (235, 125, 35),    # laranja
    "U": (70, 185, 80),     # verde
    "D": (210, 55, 55),     # vermelho
}

FACE_NAMES = {
    "F": "Amarela",
    "B": "Branca",
    "R": "Azul",
    "L": "Laranja",
    "U": "Verde",
    "D": "Vermelha",
}


@dataclass
class Sticker:
    face_id: str
    color: tuple


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def neg(v):
    return (-v[0], -v[1], -v[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def mul(v, s):
    return (v[0] * s, v[1] * s, v[2] * s)


def face_from_vec(v):
    return VEC_TO_FACE[v]


def opposite_face(face):
    return face_from_vec(neg(FACE_TO_VEC[face]))


def shade(color, factor):
    return tuple(max(0, min(255, int(c * factor))) for c in color)


def rotate_vec_90(v, axis, sign):
    """
    Rotaciona vetor v em 90 graus ao redor do eixo axis.
    sign = +1 usa regra da mão direita.
    sign = -1 usa sentido contrário.
    Funciona para vetores/eixos ortogonais de cubo.
    """
    parallel = mul(axis, dot(v, axis))
    perpendicular = add(v, mul(parallel, -1))
    if perpendicular == (0, 0, 0):
        return v
    if sign == 1:
        return add(parallel, cross(axis, perpendicular))
    return add(parallel, cross(perpendicular, axis))


class Cube3D:
    """
    Cada sticker é armazenado por:
    - posição da peça/cubie: (x, y, z), com valores -1, 0, 1
    - normal da face visível: vetor unitário, ex: (0, 0, 1)

    Rotacionar uma linha/coluna/face significa:
    - pegar todos os stickers cujas peças estão na fatia selecionada
    - rotacionar tanto posição quanto normal
    """

    def __init__(self):
        self.reset()

    def reset(self):
        self.stickers = {}
        for face_id, normal in FACE_TO_VEC.items():
            color = FACE_COLORS[face_id]
            for a in [-1, 0, 1]:
                for b in [-1, 0, 1]:
                    pos = self.pos_from_face_coords(normal, a, b)
                    self.stickers[(pos, normal)] = Sticker(face_id, color)

    def pos_from_face_coords(self, normal, a, b):
        # a e b são coordenadas nos dois eixos livres da face.
        x, y, z = normal
        if normal in [(0, 0, 1), (0, 0, -1)]:
            return (a, b, z)
        if normal in [(0, 1, 0), (0, -1, 0)]:
            return (a, y, b)
        return (x, b, a)

    def rotate_slice(self, axis, layer_value, sign):
        """
        axis: vetor do eixo da rotação.
        layer_value: -1, 0 ou 1 em relação ao eixo.
        sign: +1 ou -1.
        """
        new_stickers = {}
        for (pos, normal), sticker in self.stickers.items():
            if dot(pos, axis) == layer_value:
                new_pos = rotate_vec_90(pos, axis, sign)
                new_normal = rotate_vec_90(normal, axis, sign)
                new_stickers[(new_pos, new_normal)] = sticker
            else:
                new_stickers[(pos, normal)] = sticker
        self.stickers = new_stickers

    def get_sticker(self, pos, normal):
        return self.stickers.get((pos, normal))

    def visible_face_grid(self, front_vec, up_vec, right_vec):
        grid = [[None for _ in range(3)] for _ in range(3)]
        for (pos, normal), sticker in self.stickers.items():
            if normal != front_vec:
                continue
            col = dot(pos, right_vec) + 1
            row = 1 - dot(pos, up_vec)
            if 0 <= row <= 2 and 0 <= col <= 2:
                grid[row][col] = sticker
        return grid

    def move_column(self, right_vec, up_vec, col, direction_up=True):
        layer = col - 1
        # Coluna para cima:
        # eixo = direita visual. O sentido negativo leva os stickers da frente para o topo.
        sign = -1 if direction_up else 1
        self.rotate_slice(right_vec, layer, sign)

    def move_row(self, up_vec, row, direction_right=True):
        layer = 1 - row
        # Linha para direita:
        # eixo = topo visual. O sentido positivo leva os stickers da frente para a direita.
        sign = 1 if direction_right else -1
        self.rotate_slice(up_vec, layer, sign)

    def move_face(self, front_vec, clockwise=True):
        # Face horário vista pelo jogador:
        # o topo da face deve ir para a direita visual.
        sign = -1 if clockwise else 1
        self.rotate_slice(front_vec, 1, sign)

    def shuffle(self, cam, n=30):
        for _ in range(n):
            front, up, right = cam.axes_vectors()
            op = random.choice(["col_up", "col_down", "row_left", "row_right", "face_cw", "face_ccw"])
            if op == "col_up":
                self.move_column(right, up, random.randrange(3), True)
            elif op == "col_down":
                self.move_column(right, up, random.randrange(3), False)
            elif op == "row_left":
                self.move_row(up, random.randrange(3), False)
            elif op == "row_right":
                self.move_row(up, random.randrange(3), True)
            elif op == "face_cw":
                self.move_face(front, True)
            elif op == "face_ccw":
                self.move_face(front, False)


class CameraOrientation:
    def __init__(self):
        self.front = "F"
        self.up = "U"

    def reset(self):
        self.front = "F"
        self.up = "U"

    def right_face(self):
        # Direita visual = up x front.
        # Essa relação mantém o preview, a navegação e os comandos no mesmo referencial:
        # W = topo da tela, S = baixo, A = esquerda, D = direita.
        return face_from_vec(cross(FACE_TO_VEC[self.up], FACE_TO_VEC[self.front]))

    def move_over_edge(self, direction):
        old_front = self.front
        old_up = self.up
        old_right = self.right_face()

        if direction == "up":
            self.front = old_up
            self.up = opposite_face(old_front)
        elif direction == "down":
            self.front = opposite_face(old_up)
            self.up = old_front
        elif direction == "left":
            self.front = opposite_face(old_right)
            self.up = old_up
        elif direction == "right":
            self.front = old_right
            self.up = old_up

    def axes_vectors(self):
        front_vec = FACE_TO_VEC[self.front]
        up_vec = FACE_TO_VEC[self.up]
        right_vec = FACE_TO_VEC[self.right_face()]
        return front_vec, up_vec, right_vec


class App:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Protótipo – Cubo 3x3 Artefato/Chave v9")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()

        self.font = pygame.font.SysFont("arial", 20)
        self.small = pygame.font.SysFont("arial", 16)
        self.big = pygame.font.SysFont("arial", 34, bold=True)

        self.cube = Cube3D()
        self.cam = CameraOrientation()

        self.sel_r = 1
        self.sel_c = 1
        self.locked = False

        self.dragging = False
        self.last_mouse = (0, 0)
        self.drag_yaw = 0.0
        self.drag_pitch = 0.0

        self.shuffle_button = pygame.Rect(970, 512, 230, 42)
        self.reset_button = pygame.Rect(970, 564, 230, 42)

        self.log = [
            "v9: sentidos de rotação corrigidos contra o preview.",
            "D agora puxa a lateral azul para a frente; A puxa a laranja.",
            "W/S e Q/E seguem a orientação visual da face atual."
        ]

    def add_log(self, msg):
        self.log.insert(0, msg)
        self.log = self.log[:7]

    def run(self):
        while True:
            self.handle_events()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if e.type == pygame.MOUSEBUTTONDOWN and e.button == 1:
                if self.shuffle_button.collidepoint(e.pos):
                    self.cube.shuffle(self.cam)
                    self.add_log("Botão: cubo aleatorizado.")
                    continue

                if self.reset_button.collidepoint(e.pos):
                    self.cube.reset()
                    self.cam.reset()
                    self.sel_r = 1
                    self.sel_c = 1
                    self.locked = False
                    self.drag_yaw = 0.0
                    self.drag_pitch = 0.0
                    self.add_log("Botão: cubo resetado para estado correto.")
                    continue

                self.dragging = True
                self.last_mouse = e.pos

            elif e.type == pygame.MOUSEBUTTONUP and e.button == 1:
                self.dragging = False

            elif e.type == pygame.MOUSEMOTION and self.dragging:
                dx = e.pos[0] - self.last_mouse[0]
                dy = e.pos[1] - self.last_mouse[1]
                self.drag_yaw += dx * 0.015
                self.drag_pitch += dy * 0.015
                self.drag_pitch = max(-1.25, min(1.25, self.drag_pitch))
                self.last_mouse = e.pos

            elif e.type == pygame.KEYDOWN:
                self.key(e.key)

    def key(self, key):
        if key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        if key == pygame.K_SPACE:
            self.locked = not self.locked
            self.add_log("Peça FIXADA." if self.locked else "Peça liberada.")
            return

        if key == pygame.K_f:
            self.drag_yaw = 0.0
            self.drag_pitch = 0.0
            self.add_log("F: face atual alinhada de frente.")
            return

        if key == pygame.K_r:
            self.cube.shuffle(self.cam)
            self.add_log("R: cubo aleatorizado.")
            return

        front, up, right = self.cam.axes_vectors()

        if self.locked:
            if key == pygame.K_w:
                self.cube.move_column(right, up, self.sel_c, True)
                self.add_log(f"W: coluna {self.sel_c + 1} para cima.")
            elif key == pygame.K_s:
                self.cube.move_column(right, up, self.sel_c, False)
                self.add_log(f"S: coluna {self.sel_c + 1} para baixo.")
            elif key == pygame.K_a:
                self.cube.move_row(up, self.sel_r, False)
                self.add_log(f"A: linha {self.sel_r + 1} para esquerda.")
            elif key == pygame.K_d:
                self.cube.move_row(up, self.sel_r, True)
                self.add_log(f"D: linha {self.sel_r + 1} para direita.")
            elif key == pygame.K_q:
                self.cube.move_face(front, False)
                self.add_log("Q: face atual anti-horário.")
            elif key == pygame.K_e:
                self.cube.move_face(front, True)
                self.add_log("E: face atual horário.")
        else:
            if key in [pygame.K_w, pygame.K_a, pygame.K_s, pygame.K_d]:
                self.move_selection(key)

    def move_selection(self, key):
        if key == pygame.K_w:
            self.sel_r -= 1
            if self.sel_r < 0:
                self.sel_r = 2
                self.cam.move_over_edge("up")
                self.drag_yaw = 0.0
                self.drag_pitch = 0.0
                self.add_log(f"Borda superior: face {FACE_NAMES[self.cam.front]} alinhada.")
        elif key == pygame.K_s:
            self.sel_r += 1
            if self.sel_r > 2:
                self.sel_r = 0
                self.cam.move_over_edge("down")
                self.drag_yaw = 0.0
                self.drag_pitch = 0.0
                self.add_log(f"Borda inferior: face {FACE_NAMES[self.cam.front]} alinhada.")
        elif key == pygame.K_a:
            self.sel_c -= 1
            if self.sel_c < 0:
                self.sel_c = 2
                self.cam.move_over_edge("left")
                self.drag_yaw = 0.0
                self.drag_pitch = 0.0
                self.add_log(f"Borda esquerda: face {FACE_NAMES[self.cam.front]} alinhada.")
        elif key == pygame.K_d:
            self.sel_c += 1
            if self.sel_c > 2:
                self.sel_c = 0
                self.cam.move_over_edge("right")
                self.drag_yaw = 0.0
                self.drag_pitch = 0.0
                self.add_log(f"Borda direita: face {FACE_NAMES[self.cam.front]} alinhada.")

    def text(self, s, x, y, color=TEXT, font=None):
        surf = (font or self.font).render(s, True, color)
        self.screen.blit(surf, (x, y))

    def draw(self):
        self.screen.fill(BG)
        self.draw_header()
        self.draw_cube_3d()
        self.draw_face_panel()
        self.draw_help()
        self.draw_log()
        pygame.display.flip()

    def draw_header(self):
        self.text("Cubo 3x3 – Artefato/Chave", 34, 24, TEXT, self.big)
        mode = "MODO GIRO DE LINHAS/COLUNAS/FACE" if self.locked else "MODO NAVEGAÇÃO ENTRE PEÇAS"
        self.text(mode, 38, 68, LOCK if self.locked else GOLD)
        self.text(f"Face atual: {FACE_NAMES[self.cam.front]} | Topo da tela: {FACE_NAMES[self.cam.up]} | F alinha face", 38, 98, MUTED, self.small)

    def draw_face_panel(self):
        pygame.draw.rect(self.screen, PANEL, (36, 140, 410, 430), border_radius=16)
        self.text("Face atual / jogável", 64, 164, TEXT)

        x0, y0 = 78, 210
        size = 102
        gap = 8

        front, up, right = self.cam.axes_vectors()
        grid = self.cube.visible_face_grid(front, up, right)

        for r in range(3):
            for c in range(3):
                rect = pygame.Rect(x0 + c * (size + gap), y0 + r * (size + gap), size, size)
                st = grid[r][c]
                color = st.color if st else (60, 60, 65)

                pygame.draw.rect(self.screen, color, rect, border_radius=8)
                pygame.draw.rect(self.screen, GRID, rect, 3, border_radius=8)

                if st:
                    self.text(st.face_id, rect.centerx - 10, rect.centery - 12, BLACK, self.font)

                if r == self.sel_r and c == self.sel_c:
                    pygame.draw.rect(self.screen, GOLD, rect.inflate(8, 8), 5, border_radius=10)
                    if self.locked:
                        pygame.draw.rect(self.screen, LOCK, rect.inflate(20, 20), 3, border_radius=14)

        if self.locked:
            col_rect = pygame.Rect(x0 + self.sel_c * (size + gap), y0, size, 3 * size + 2 * gap)
            row_rect = pygame.Rect(x0, y0 + self.sel_r * (size + gap), 3 * size + 2 * gap, size)
            pygame.draw.rect(self.screen, (70, 220, 100), col_rect.inflate(16, 16), 3, border_radius=12)
            pygame.draw.rect(self.screen, (255, 150, 45), row_rect.inflate(16, 16), 3, border_radius=12)
            self.text("Selecionada: W/S coluna | A/D linha | Q/E face", 64, 530, LOCK, self.small)
        else:
            self.text("Navegue com WASD. Bordas trocam a face atual.", 64, 530, MUTED, self.small)

    def draw_cube_3d(self):
        center = (720, 350)
        scale = 82

        quads = []
        for (pos, normal), sticker in self.cube.stickers.items():
            corners = self.sticker_corners(pos, normal)
            pts_cam = [self.world_to_camera(p) for p in corners]
            depth = sum(p[2] for p in pts_cam) / 4.0
            pts2 = [(center[0] + p[0] * scale, center[1] - p[1] * scale) for p in pts_cam]
            brightness = 0.88 + max(-0.22, min(0.22, depth * 0.07))
            quads.append((depth, pts2, shade(sticker.color, brightness), pos, normal))

        quads.sort(key=lambda x: x[0])

        self.text("Preview 3D", 610, 142, TEXT)
        self.text("Click + Mouse: gira visualmente | F: alinha a face", 610, 166, MUTED, self.small)

        front, up, right = self.cam.axes_vectors()
        selected_pos = add(add(front, mul(right, self.sel_c - 1)), mul(up, 1 - self.sel_r))

        for _, pts, color, pos, normal in quads:
            pygame.draw.polygon(self.screen, color, pts)
            pygame.draw.polygon(self.screen, GRID, pts, 2)

            if normal == front and pos == selected_pos:
                pygame.draw.polygon(self.screen, GOLD, pts, 5)
                if self.locked:
                    pygame.draw.polygon(self.screen, LOCK, pts, 8)

    def sticker_corners(self, pos, normal):
        # Cria um quadrado pequeno na superfície do sticker.
        # Como a posição é -1/0/1 e o sticker ocupa 1 unidade, cada canto é +/- 0.48 nos eixos tangentes.
        n = normal

        if n in [(0, 0, 1), (0, 0, -1)]:
            t1 = (1, 0, 0)
            t2 = (0, 1, 0)
        elif n in [(0, 1, 0), (0, -1, 0)]:
            t1 = (1, 0, 0)
            t2 = (0, 0, 1)
        else:
            t1 = (0, 0, 1)
            t2 = (0, 1, 0)

        # Centro visual do sticker:
        # pos é o centro lógico do cubie (-1, 0, 1).
        # A face desenhada precisa ficar na superfície externa do cubo,
        # então deslocamos meio bloco na direção da normal.
        center = add(mul(pos, 1.0), mul(normal, 0.5))

        half = 0.48
        return [
            add(add(center, mul(t1, -half)), mul(t2, -half)),
            add(add(center, mul(t1, half)), mul(t2, -half)),
            add(add(center, mul(t1, half)), mul(t2, half)),
            add(add(center, mul(t1, -half)), mul(t2, half)),
        ]

    def world_to_camera(self, p):
        front, up, right = self.cam.axes_vectors()

        x = dot(p, right)
        y = dot(p, up)
        z = dot(p, front)

        cy = math.cos(self.drag_yaw)
        sy = math.sin(self.drag_yaw)
        x, z = x * cy + z * sy, -x * sy + z * cy

        cp = math.cos(self.drag_pitch)
        sp = math.sin(self.drag_pitch)
        y, z = y * cp - z * sp, y * sp + z * cp

        return (x, y, z)

    def draw_help(self):
        pygame.draw.rect(self.screen, PANEL, (940, 140, 300, 430), border_radius=16)
        self.text("Controles", 970, 166, TEXT, self.big)

        lines = [
            ("Navegação", GOLD),
            ("WASD: mover entre quadrados", MUTED),
            ("Borda: troca para face vizinha", MUTED),
            ("", MUTED),
            ("Visual", GOLD),
            ("Click + Mouse: girar preview", MUTED),
            ("F: alinhar face atual", MUTED),
            ("", MUTED),
            ("Peça selecionada", GOLD),
            ("Espaço: fixar/liberar", MUTED),
            ("W/S: coluna cima/baixo", MUTED),
            ("A/D: linha esquerda/direita", MUTED),
            ("Q/E: girar face", MUTED),
            ("R: aleatorizar", MUTED),
        ]

        y = 220
        for s, color in lines:
            self.text(s, 970, y, color, self.small)
            y += 23

        mouse = pygame.mouse.get_pos()

        color = BUTTON_HOVER if self.shuffle_button.collidepoint(mouse) else BUTTON
        pygame.draw.rect(self.screen, color, self.shuffle_button, border_radius=10)
        pygame.draw.rect(self.screen, GOLD, self.shuffle_button, 2, border_radius=10)
        self.text("Aleatorizar peças", self.shuffle_button.x + 38, self.shuffle_button.y + 11, TEXT, self.small)

        reset_color = BUTTON_HOVER if self.reset_button.collidepoint(mouse) else BUTTON
        pygame.draw.rect(self.screen, reset_color, self.reset_button, border_radius=10)
        pygame.draw.rect(self.screen, (120, 255, 140), self.reset_button, 2, border_radius=10)
        self.text("Resetar faces", self.reset_button.x + 54, self.reset_button.y + 11, TEXT, self.small)

    def draw_log(self):
        pygame.draw.rect(self.screen, PANEL, (36, 600, 850, 125), border_radius=16)
        self.text("Log", 64, 622, TEXT)
        y = 654
        for entry in self.log:
            self.text("• " + entry, 64, y, MUTED, self.small)
            y += 20


if __name__ == "__main__":
    App().run()
