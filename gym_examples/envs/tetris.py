import pygame
import random

# 初始化Pygame
pygame.init()

# 屏幕大小
screen_width = 300
screen_height = 600
play_width = 200  # 10 * 20块大小
play_height = 400  # 20 * 20块大小
block_size = 20

top_left_x = (screen_width - play_width) // 2
top_left_y = screen_height - play_height

# 形状格式
S = [['.....',
      '.....',
      '..00.',
      '.00..',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '...0.',
      '.....']]

Z = [['.....',
      '.....',
      '.00..',
      '..00.',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '.0...',
      '.....']]

I = [['.....',
      '..0..',
      '..0..',
      '..0..',
      '..0..'],
     ['.....',
      '0000.',
      '.....',
      '.....',
      '.....']]

O = [['.....',
      '.....',
      '.00..',
      '.00..',
      '.....']]

J = [['.....',
      '.0...',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..00.',
      '..0..',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '...0.',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '.00..',
      '.....']]

L = [['.....',
      '...0.',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..0..',
      '..00.',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '.0...',
      '.....'],
     ['.....',
      '.00..',
      '..0..',
      '..0..',
      '.....']]

T = [['.....',
      '..0..',
      '.000.',
      '.....',
      '.....'],
     ['.....',
      '..0..',
      '..00.',
      '..0..',
      '.....'],
     ['.....',
      '.....',
      '.000.',
      '..0..',
      '.....'],
     ['.....',
      '..0..',
      '.00..',
      '..0..',
      '.....']]

shapes = [S, Z, I, O, J, L, T]
shape_colors = [(0, 255, 0), (255, 0, 0), (0, 255, 255), (255, 255, 0), (255, 165, 0), (0, 0, 255), (128, 0, 128)]

# 定义形状类
class Piece:
    def __init__(self, x, y, shape):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = shape_colors[shapes.index(shape)]
        self.rotation = 0

# 创建网格
def create_grid(locked_positions={}):
    grid = [[(0, 0, 0) for _ in range(10)] for _ in range(20)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                color = locked_positions[(x, y)]
                grid[y][x] = color
    return grid

# 转换形状格式
def convert_shape_format(piece):
    positions = []
    format = piece.shape[piece.rotation % len(piece.shape)]

    for i, line in enumerate(format):
        row = list(line)
        for j, column in enumerate(row):
            if column == '0':
                positions.append((piece.x + j, piece.y + i))

    for i, pos in enumerate(positions):
        positions[i] = (pos[0] - 2, pos[1] - 4)

    return positions

def valid_space(piece, grid):
    accepted_positions = [[(j, i) for j in range(len(grid[0])) if grid[i][j] == (0, 0, 0)] for i in range(len(grid))]
    accepted_positions = [j for sub in accepted_positions for j in sub]

    formatted = convert_shape_format(piece)

    for pos in formatted:
        if pos not in accepted_positions:
            if pos[1] >= 0:
                return False
    return True

# 检查游戏结束
def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

# 获取随机形状
def get_shape():
    return Piece(5, 0, random.choice(shapes))

# 绘制文本
def draw_text_middle(text, size, color, surface):
    font = pygame.font.Font(pygame.font.get_default_font(), size, bold=True)
    label = font.render(text, 1, color)

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), top_left_y + play_height / 2 - (label.get_height() / 2)))

# 绘制网格
def draw_grid(surface, grid):
    sx = top_left_x
    sy = top_left_y

    for i in range(len(grid)):
        pygame.draw.line(surface, (128, 128, 128), (sx, sy + i * block_size), (sx + play_width, sy + i * block_size))
        for j in range(len(grid[i])):
            pygame.draw.line(surface, (128, 128, 128), (sx + j * block_size, sy), (sx + j * block_size, sy + play_height))

# 清除行
def clear_rows(grid, locked):
    increment = 0
    for i in range(len(grid) - 1, -1, -1):
        row = grid[i]
        if (0, 0, 0) not in row:
            increment += 1
            ind = i
            for j in range(len(row)):
                try:
                    del locked[(j, i)]
                except:
                    continue

    if increment > 0:
        for key in sorted(list(locked), key=lambda x: x[1])[::-1]:
            x, y = key
            if y < ind:
                newKey = (x, y + increment)
                locked[newKey] = locked.pop(key)

    return increment

# 绘制窗口
def draw_window(surface, grid, score=0):
    surface.fill((0, 0, 0))

    pygame.font.init()
    font = pygame.font.Font(pygame.font.get_default_font(), 30)
    label = font.render(f'Tetris', 1, (255, 255, 255))

    surface.blit(label, (top_left_x + play_width / 2 - (label.get_width() / 2), 30))

    font = pygame.font.Font(pygame.font.get_default_font(), 25)
    label = font.render(f'Score: {score}', 1, (255, 255, 255))

    sx = top_left_x + play_width + 50
    sy = top_left_y + play_height / 2 - 100

    surface.blit(label, (sx + 20, sy + 160))

    for i in range(len(grid)):
        for j in range(len(grid[i])):
            pygame.draw.rect(surface, grid[i][j], (top_left_x + j * block_size, top_left_y + i * block_size, block_size, block_size), 0)

    draw_grid(surface, grid)
    pygame.draw.rect(surface, (255, 0, 0), (top_left_x, top_left_y, play_width, play_height), 5)

    pygame.display.update()

# 主函数
# def main():
#     locked_positions = {}
#     grid = create_grid(locked_positions)
#
#     change_piece = False
#     run = True
#     current_piece = get_shape()
#     next_piece = get_shape()
#     clock = pygame.time.Clock()
#     fall_time = 0
#     level_time = 0
#     score = 0
#
#     while run:
#         grid = create_grid(locked_positions)
#         fall_speed = 0.27
#
#         fall_time += clock.get_rawtime()
#         level_time += clock.get_rawtime()
#         clock.tick()
#
#         if level_time / 1000 > 5:
#             level_time = 0
#             if fall_speed > 0.12:
#                 fall_speed -= 0.005
#
#         if fall_time / 1000 >= fall_speed:
#             fall_time = 0
#             current_piece.y += 1
#             if not (valid_space(current_piece, grid)) and current_piece.y > 0:
#                 current_piece.y -= 1
#                 change_piece = True
#
#         for event in pygame.event.get():
#             if event.type == pygame.QUIT:
#                 run = False
#                 pygame.display.quit()
#                 quit()
#
#             if event.type == pygame.KEYDOWN:
#                 if event.key == pygame.K_LEFT:
#                     current_piece.x -= 1
#                     if not valid_space(current_piece, grid):
#                         current_piece.x += 1
#                 if event.key == pygame.K_RIGHT:
#                     current_piece.x += 1
#                     if not valid_space(current_piece, grid):
#                         current_piece.x -= 1
#                 if event.key == pygame.K_DOWN:
#                     current_piece.y += 1
#                     if not valid_space(current_piece, grid):
#                         current_piece.y -= 1
#                 if event.key == pygame.K_UP:
#                     current_piece.rotation = current_piece.rotation + 1 % len(current_piece.shape)
#                     if not valid_space(current_piece, grid):
#                         current_piece.rotation = current_piece.rotation - 1 % len(current_piece.shape)
#
#         shape_pos = convert_shape_format(current_piece)
#
#         for i in range(len(shape_pos)):
#             x, y = shape_pos[i]
#             if y > -1:
#                 grid[y][x] = current_piece.color
#
#         if change_piece:
#             for pos in shape_pos:
#                 p = (pos[0], pos[1])
#                 locked_positions[p] = current_piece.color
#             current_piece = next_piece
#             next_piece = get_shape()
#             change_piece = False
#             score += clear_rows(grid, locked_positions) * 10
#
#         draw_window(win, grid, score)
#
#         if check_lost(locked_positions):
#             run = False
#
#     draw_text_middle("You Lost", 40, (255, 255, 255), win)
#     pygame.display.update()
#     pygame.time.delay(2000)
#     pygame.quit()

# 设置屏幕大小
# win = pygame.display.set_mode((screen_width, screen_height))
# pygame.display.set_caption('Tetris')
#
# main()