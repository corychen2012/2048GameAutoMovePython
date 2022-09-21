import random
import numpy as np


class Grid:
    size = 4
    tiles = []
    max_tile = 0
    

    def __init__(self, size=4):
        self.size = size
        self.score = 0
        self.tiles = np.zeros((size, size)).astype(np.int32)
        self.xy = -1

    def is_zero(self, x, y):
        return self.tiles[y][x] == 0

    def is_full(self):
        return 0 not in self.tiles

    # 设置瓷砖
    def set_tiles(self, xy, number):
        if(xy[1]<0 or xy[0]<0):
            return
        self.tiles[xy[1]][xy[0]] = number

    # 获取一个随机的空坐标
    def get_random_xy(self):
        if not self.is_full():
            while 1:
                x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
                if self.is_zero(x, y):
                    return x, y
        return -1, -1

    def get_manual_xy(self,posxy):
        """
        获取鼠标点击瓷砖位置的数值
        """
        xy=self.pos_to_xy(posxy)
        return self.tiles[xy[1]][xy[0]]


    # 初始设置瓷砖,由于增加了ai辅助,取消设置默认瓷砖,默认瓷砖需手工添加
    def add_tile_init(self):
        # self.add_random_tile()
        # self.add_random_tile()
        pass

    # 添加一个随机的瓷砖
    def add_random_tile(self):
        if not self.is_full():
            # 产生2的概率为0.9
            # q = 0.9
            # for i in range(1,50):
            #     if random.random() < q or i==50-1:
            #         value = 2**i
            #         break
            value = 2 if random.random() < 0.9 else 4
            self.set_tiles(self.get_random_xy(), value)

    def add_manual_tile(self,posxy):
        """
        在鼠标点击位置添加一片瓷砖,点击一次翻一倍
        """
        value = 2 if self.get_manual_xy(posxy)==0 else self.get_manual_xy(posxy)*2
        self.set_tiles(self.pos_to_xy(posxy),value)

    def pos_to_xy(self,posxy):
        """
        坐标转换为瓷片位置
        """
        x,y = -1,-1
        if(0<posxy[0]<125):
            x = 0
        elif(125<posxy[0]<250):
            x = 1
        elif(250<posxy[0]<375):
            x=2
        elif(375<posxy[0]<500):
            x=3
        if(0<posxy[1]<125):
            y = 0
        elif(125<posxy[1]<250):
            y = 1
        elif(250<posxy[1]<375):
            y=2
        elif(375<posxy[1]<500):
            y=3
        return x,y
        

    def run(self, direction, is_fake=False):
        """
        按照传入的方向参数,移动表盘,返回移动后评分
        """
        if isinstance(direction, int):
            direction = nmap[direction]
        self.score = 0
        if is_fake:
            t = self.tiles.copy()
        else:
            t = self.tiles
        if direction == 'U':
            for i in range(self.size):
                self.move_hl(t[:, i])
        elif direction == 'D':
            for i in range(self.size):
                self.move_hl(t[::-1, i])
        elif direction == 'L':
            for i in range(self.size):
                self.move_hl(t[i, :])
        elif direction == 'R':
            for i in range(self.size):
                self.move_hl(t[i, ::-1])
        return self.score

    # 移动某一行或某一列
    def move_hl(self, hl):
        '''
        移动某一行或某一列
        对于hl,从大往小移动
        :return: 移动后的列表
        '''
        len_hl = len(hl)
        for i in range(len_hl - 1):
            if hl[i] == 0:
                for j in range(i + 1, len_hl):
                    if hl[j] != 0:
                        hl[i] = hl[j]
                        hl[j] = 0
                        self.score += 1
                        break
            if hl[i] == 0:
                break
            for j in range(i + 1, len_hl):
                if hl[j] == hl[i]:
                    hl[i] += hl[j]
                    self.score += hl[j]
                    hl[j] = 0
                    break
                if hl[j] != 0:
                    break
        return hl

    # 判断是否结束
    def is_over(self):
        if not self.is_full():
            return False
        for y in range(self.size - 1):
            for x in range(self.size - 1):
                if self.tiles[y][x] == self.tiles[y][x + 1] or self.tiles[y][x] == self.tiles[y + 1][x]:
                    return False
        return True

    # 判断是否胜利
    def is_win(self):
        if self.max_tile > 0:
            return self.max_tile in self.tiles
        else:
            return False

    def __str__(self):
        str_ = '====================\n'
        for row in self.tiles:
            str_ += '-' * (5 * self.size + 1) + '\n'
            for i in row:
                str_ += '|{:4d}'.format(int(i))
            str_ += '|\n'
        str_ += '-' * (5 * self.size + 1) + '\n'
        str_ += '==================\n'
        return str_


nmap = {0: 'U', 1: 'R', 2: 'D', 3: 'L'}
fmap = dict([val, key] for key, val in nmap.items())


class Game:
    score = 0
    env = 'testing'
    state = 'start'
    grid = None

    def __init__(self, grid_size=4, env='production'):
        self.env = env
        self.grid_size = grid_size
        self.start()

    # 开始或重新开始
    def start(self):
        self.grid = Grid(self.grid_size)
        if self.env == 'production':
            self.grid.add_tile_init()
        self.state = 'run'

    # 运行一步
    def run(self, direction):
        if self.state in ['over', 'win']:
            return None
        if isinstance(direction, int):
            direction = nmap[direction]

        self.grid.run(direction)
        self.score += self.grid.score

        if self.grid.is_over():
            self.state = 'over'

        if self.grid.is_win():
            self.state = 'win'

        # 产生新方块
        if self.env == 'production':
            self.grid.add_random_tile()
        return self.grid

    def run_m_ai(self, direction):
        """
        在ai辅助模式运行一步,执行后不再自动生成随机块,需人工点击生成
        """
        if self.state in ['over', 'win']:
            return None
        if isinstance(direction, int):
            direction = nmap[direction]

        self.grid.run(direction)
        self.score += self.grid.score

        if self.grid.is_over():
            self.state = 'over'

        if self.grid.is_win():
            self.state = 'win'

        
        return self.grid

    def printf(self):
        print(self.grid)


if __name__ == '__main__':
    game = Game(env='testing')
    game.grid.set_tiles((0,0),2)
    print(game.grid)
    print(game.run('D'))
    print(game.grid.move_hl([0, 0, 0, 2]))
    print()
