import gym
from gym import spaces
import pygame
import numpy as np

# 定义一个GridWorldEnv类，继承自gym.Env
class GridWorldEnv(gym.Env):
    # 环境的元数据，包括渲染模式和帧率
    metadata = {"render_modes": ["human", "rgb_array"], "render_fps": 4}

    # 初始化环境
    def __init__(self, render_mode=None, size=5):
        self.size = size  # 方格世界的大小
        self.window_size = 512  # PyGame窗口的大小

        # 观察空间，包含了智能体和目标的位置
        self.observation_space = spaces.Dict(
            {
                "agent": spaces.Box(0, size - 1, shape=(2,), dtype=int),  # 智能体的位置
                "target": spaces.Box(0, size - 1, shape=(2,), dtype=int),  # 目标的位置
            }
        )

        # 动作空间，有4个动作，分别对应“右”、“上”、“左”、“下”
        self.action_space = spaces.Discrete(4)

        # 将动作映射到方向
        self._action_to_direction = {
            0: np.array([1, 0]),  # 右
            1: np.array([0, 1]),  # 上
            2: np.array([-1, 0]),  # 左
            3: np.array([0, -1]),  # 下
        }

        # 确保render_mode是可接受的值
        assert render_mode is None or render_mode in self.metadata["render_modes"]
        self.render_mode = render_mode

        # 如果使用人类渲染模式，self.window和self.clock将用于确保正确的帧率
        self.window = None
        self.clock = None

    # 获取当前的观察
    def _get_obs(self):
        return {"agent": self._agent_location, "target": self._target_location}

    # 获取当前的信息
    def _get_info(self):
        return {
            "distance": np.linalg.norm(
                self._agent_location - self._target_location, ord=1
            )  # 计算曼哈顿距离
        }

    # 重置环境
    def reset(self, seed=None, options=None):
        # 需要这行代码来设置随机种子
        super().reset(seed=seed)

        # 随机选择智能体的位置
        self._agent_location = self.np_random.integers(0, self.size, size=2, dtype=int)

        # 随机选择目标的位置，直到它与智能体的位置不同
        self._target_location = self._agent_location
        while np.array_equal(self._target_location, self._agent_location):
            self._target_location = self.np_random.integers(
                0, self.size, size=2, dtype=int
            )

        observation = self._get_obs()
        info = self._get_info()

        # 如果渲染模式是“human”，则渲染当前帧
        if self.render_mode == "human":
            self._render_frame()

        return observation, info

    # 执行动作
    def step(self, action):
        # 将动作映射到方向
        direction = self._action_to_direction[action]
        # 使用np.clip确保智能体不会离开网格
        self._agent_location = np.clip(
            self._agent_location + direction, 0, self.size - 1
        )
        # 当且仅当智能体到达目标时，episode结束
        terminated = np.array_equal(self._agent_location, self._target_location)
        reward = 1 if terminated else 0  # 二进制稀疏奖励
        observation = self._get_obs()
        info = self._get_info()

        # 如果渲染模式是“human”，则渲染当前帧
        if self.render_mode == "human":
            self._render_frame()

        return observation, reward, terminated, False, info

# 添加渲染方法到GridWorldEnv类中
def render(self):
    # 如果渲染模式是"rgb_array"，则返回当前帧的渲染
    if self.render_mode == "rgb_array":
        return self._render_frame()

# 私有方法，用于渲染当前帧
def _render_frame(self):
    # 如果渲染模式是"human"且窗口尚未初始化，则初始化PyGame窗口
    if self.window is None and self.render_mode == "human":
        pygame.init()
        pygame.display.init()
        self.window = pygame.display.set_mode((self.window_size, self.window_size))
    # 如果渲染模式是"human"且时钟尚未初始化，则初始化时钟
    if self.clock is None and self.render_mode == "human":
        self.clock = pygame.time.Clock()

    # 创建一个画布，填充为白色
    canvas = pygame.Surface((self.window_size, self.window_size))
    canvas.fill((255, 255, 255))
    pix_square_size = (
            self.window_size / self.size
    )  # 单个网格方块的像素大小

    # 首先绘制目标
    pygame.draw.rect(
        canvas,
        (255, 0, 0),  # 红色
        pygame.Rect(
            pix_square_size * self._target_location,
            (pix_square_size, pix_square_size),
            ),
    )
    # 然后绘制智能体
    pygame.draw.circle(
        canvas,
        (0, 0, 255),  # 蓝色
        (self._agent_location + 0.5) * pix_square_size,
        pix_square_size / 3,
        )

    # 最后，添加网格线
    for x in range(self.size + 1):
        pygame.draw.line(
            canvas,
            0,  # 黑色
            (0, pix_square_size * x),
            (self.window_size, pix_square_size * x),
            width=3,
        )
        pygame.draw.line(
            canvas,
            0,  # 黑色
            (pix_square_size * x, 0),
            (pix_square_size * x, self.window_size),
            width=3,
        )

    if self.render_mode == "human":
        # 将画布上的内容复制到可见窗口
        self.window.blit(canvas, canvas.get_rect())
        pygame.event.pump()
        pygame.display.update()

        # 确保人类渲染按照预定义的帧率进行
        self.clock.tick(self.metadata["render_fps"])
    else:  # rgb_array模式
        return np.transpose(
            np.array(pygame.surfarray.pixels3d(canvas)), axes=(1, 0, 2)
        )

# 添加关闭方法到GridWorldEnv类中
def close(self):
    # 如果窗口不为空，则退出PyGame显示并关闭PyGame
    if self.window is not None:
        pygame.display.quit()
        pygame.quit()