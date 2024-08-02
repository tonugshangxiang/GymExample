import time

import gymnasium as gym
import pygame
import numpy as np
from gymnasium import spaces
from tetris import Piece, create_grid, get_shape, draw_window, clear_rows, valid_space, check_lost, convert_shape_format
from gymnasium.utils import seeding
from typing import Tuple


class TetrisEnv(gym.Env):
    metadata = {'render_modes': ['human', 'rgb_array']}

    def __init__(self, render_mode=None):
        super(TetrisEnv, self).__init__()

        # 定义屏幕和游戏区的尺寸
        self.screen_width = 300
        self.screen_height = 600
        self.play_width = 200
        self.play_height = 400
        self.block_size = 20

        # 计算游戏区左上角的坐标
        self.top_left_x = (self.screen_width - self.play_width) // 2
        self.top_left_y = self.screen_height - self.play_height

        # 定义动作空间：左、右、旋转、下
        self.action_space = spaces.Discrete(4)
        # 定义观测空间：屏幕的RGB图像
        self.observation_space = spaces.Box(low=0, high=255, shape=(self.screen_height, self.screen_width, 3),
                                            dtype=np.uint8)

        # 初始化实例属性
        self.locked_positions = None
        self.grid = None
        self.current_piece = None
        self.next_piece = None
        self.score = None
        self.change_piece = None
        self.run = None
        self.fall_time = None
        self.level_time = None
        self.fall_speed = None
        self.clock = None
        self.win = None
        self.render_mode = render_mode

        self.seed()
        self.reset()

    def seed(self, seed=None):
        self.np_random, seed = seeding.np_random(seed)
        return [seed]

    def reset(self, *, seed: int = None, options: dict = None) -> Tuple[np.ndarray, dict]:
        super().reset(seed=seed)

        # 重置游戏状态
        self.locked_positions = {}  # 存储已锁定方块的位置
        self.grid = create_grid(self.locked_positions)  # 创建初始网格
        self.current_piece = get_shape()  # 获取当前方块
        self.next_piece = get_shape()  # 获取下一个方块
        self.score = 0  # 初始化得分
        self.change_piece = False  # 是否需要更换方块
        self.run = True  # 游戏是否进行中
        self.fall_time = 0  # 方块下落的时间
        self.level_time = 0  # 游戏等级的时间
        self.fall_speed = 0.27  # 初始下落速度
        self.clock = pygame.time.Clock()  # 初始化时钟

        # 创建游戏窗口
        if self.win is None and self.render_mode == 'human':
            self.win = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption('Tetris')


        return self.grid, {}

    def step(self, action):
        reward = 0
        terminated = False
        truncated = False

        self.fall_time += self.clock.get_rawtime()
        self.level_time += self.clock.get_rawtime()
        self.clock.tick()

        # 每经过5秒，增加游戏难度
        if self.level_time / 1000 > 5:
            self.level_time = 0
            if self.fall_speed > 0.12:
                self.fall_speed -= 0.005

        # 方块下落逻辑
        if self.fall_time / 1000 >= self.fall_speed:
            self.fall_time = 0
            self.current_piece.y += 1
            if not valid_space(self.current_piece, self.grid) and self.current_piece.y > 0:
                self.current_piece.y -= 1
                self.change_piece = True

        # 根据动作移动方块
        if action == 0:  # 左
            self.current_piece.x -= 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.x += 1
        elif action == 1:  # 右
            self.current_piece.x += 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.x -= 1
        elif action == 2:  # 旋转
            self.current_piece.rotation = (self.current_piece.rotation + 1) % len(self.current_piece.shape)
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.rotation = (self.current_piece.rotation - 1) % len(self.current_piece.shape)
            else:
                # 打印旋转后的形状位置
                shape_pos = convert_shape_format(self.current_piece)
                print("Rotated shape positions:", shape_pos)
        elif action == 3:  # 下
            self.current_piece.y += 1
            if not valid_space(self.current_piece, self.grid):
                self.current_piece.y -= 1

        # 获取方块的坐标位置
        shape_pos = convert_shape_format(self.current_piece)

        # 更新网格
        for i in range(len(shape_pos)):
            x, y = shape_pos[i]
            if y > -1:
                self.grid[y][x] = self.current_piece.color

        # 检查是否需要更换方块
        if self.change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                self.locked_positions[p] = self.current_piece.color
            self.current_piece = self.next_piece
            self.next_piece = get_shape()
            self.change_piece = False
            reward += clear_rows(self.grid, self.locked_positions) * 10

        # 检查游戏是否结束
        if check_lost(self.locked_positions):
            self.run = False
            reward -= 50
            terminated = True

        # 调试信息
        print("Action:", action)
        print("Current piece position:", self.current_piece.x, self.current_piece.y)
        print("------")

        return self.grid, reward, terminated, truncated, {}

    def render(self):
        if self.render_mode == 'human':
            if self.win is None:
                self.win = pygame.display.set_mode((self.screen_width, self.screen_height))
                pygame.display.set_caption('Tetris')
            draw_window(self.win, self.grid, self.score)
            pygame.display.update()
            time.sleep(1)
        elif self.render_mode == 'rgb_array':
            canvas = pygame.Surface((self.screen_width, self.screen_height))
            draw_window(canvas, self.grid, self.score)
            return np.transpose(
                np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
            )

    def close(self):
        pygame.quit()


if __name__ == "__main__":
    env = TetrisEnv(render_mode='human')
    done = False
    while not done:
        env.render()
        action = env.action_space.sample()
        state, reward, done, truncated, info = env.step(action)
        if done or truncated:
            print("Game over!")
    env.close()