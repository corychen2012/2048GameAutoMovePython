try:
    import pygame, os, time
except:
    print('cmd run: pip3 install pygame -i https://mirrors.aliyun.com/pypi/simple')
    exit()
from pygame.locals import *
from game import Game
from ai import Ai
from config import *

# config = Development()
config = SupperFast()

FPS = config.FPS
SIZE = config.SIZE
DEBUG = config.DEBUG
colors = config.COLORS
GAME_WH = config.GAME_WH
WINDOW_W = config.WINDOW_W
WINDOW_H = config.WINDOW_H

# 格子中的字体
font_h_w = 2 / 1
g_w = GAME_WH / SIZE * 0.9


# font = pygame.font.SysFont('microsoftyahei', 20)

class Main():
    def __init__(self):
        global FPS
        pygame.init()
        os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (100, 50)
        self.set_win_wh(WINDOW_W, WINDOW_H, title='2048')
        self.state = 'start'
        self.fps = FPS
        self.catch_n = 0
        self.clock = pygame.time.Clock()
        self.game = Game(SIZE)
        self.ai = Ai()
        self.step_time = config.STEP_TIME
        self.next_f = ''
        self.last_time = time.time()
        self.jm = -1
        self.xy = -1

    def start(self):
        # 加载按钮
        self.button_list = [
            Button('start', '重新开始', (GAME_WH + 50, 150)),
            Button('ai', 'AI自动', (GAME_WH + 50, 250)),
            Button('m-ai','AI辅助',(GAME_WH+50,350)),
        ]
        self.input_cell = [
            InputBox(pygame.Rect(GAME_WH + 50, 450,100,50)),
        ]
        self.run()

    def run(self):
        while self.state != 'exit':
            if self.game.state in ['over', 'win']:
                self.state = self.game.state
            self.my_event()
            # 有下一步操作建议且在手动运行状态或AI托管状态,则按照建议进行操作
            if self.next_f != '' and (
                    self.state == 'run' or self.state == 'ai' and time.time() - self.last_time > self.step_time):
                self.game.run(self.next_f)
                self.input_cell[0].text = str(self.next_f)
                self.next_f = ''
                self.last_time = time.time()
            elif self.next_f != '' and (
                    self.state == 'run' or self.state == 'm-ai' and time.time() - self.last_time > self.step_time):
                self.game.run_m_ai(self.next_f)
                self.input_cell[0].text = str(self.next_f)                
                self.next_f = ''
                self.state = 'run'
                self.last_time = time.time()
            elif self.state == 'start':
                self.game.start()
                self.state = 'run'
            self.set_bg((210, 210, 210))
            self.draw_info()
            self.draw_button(self.button_list)
            self.draw_input(self.input_cell)
            self.draw_map()
            self.update()
        print('退出游戏')

    def draw_map(self):
        for y in range(SIZE):
            for x in range(SIZE):
                self.draw_block((x, y), self.game.grid.tiles[y][x])
        if self.state == 'over':
            pygame.draw.rect(self.screen, (0, 0, 0, 0.5),
                             (0, 0, GAME_WH, GAME_WH))
            self.draw_text('游戏结束！', (GAME_WH / 2, GAME_WH / 2), size=25, center='center')
        elif self.state == 'win':
            pygame.draw.rect(self.screen, (0, 0, 0, 0.5),
                             (0, 0, GAME_WH, GAME_WH))
            self.draw_text('胜利！', (GAME_WH / 2, GAME_WH / 2), size=25, center='center')

    # 画一个方格
    def draw_block(self, xy, number):
        one_size = GAME_WH / SIZE
        dx = one_size * 0.05
        x, y = xy[0] * one_size, xy[1] * one_size
        # print(colors[str(int(number))])
        color = colors[str(int(number))] if number <= 2048 else (0, 0, 255)
        pygame.draw.rect(self.screen, color,
                         (x + dx, y + dx, one_size - 2 * dx, one_size - 2 * dx))
        color = (20, 20, 20) if number <= 4 else (250, 250, 250)
        if number != 0:
            ln = len(str(number))
            if ln == 1:
                size = one_size * 1.2 / 2
            elif ln <= 3:
                size = one_size * 1.2 / ln
            else:
                size = one_size * 1.5 / ln

            self.draw_text(str(int(number)), (x + one_size * 0.5, y + one_size * 0.5 - size / 2), color, size, 'center')

    def draw_info(self):
        self.draw_text('分数：{}'.format(self.game.score), (GAME_WH + 50, 40))
        if self.state == 'ai':
            self.draw_text('间隔：{}'.format(self.step_time), (GAME_WH + 50, 60))
            self.draw_text('评分：{}'.format(self.jm), (GAME_WH + 50, 80))
        # self.draw_text('xy：{}'.format(self.xy), (GAME_WH + 50, 90))

    def set_bg(self, color=(255, 255, 255)):
        self.screen.fill(color)

    def catch(self, filename=None):
        if filename is None:
            filename = "./catch/catch-{:04d}.png".format(self.catch_n)
        pygame.image.save(self.screen, filename)
        self.catch_n += 1

    def draw_button(self, buttons):
        for b in buttons:
            if b.is_show:
                pygame.draw.rect(self.screen, (180, 180, 200),
                                 (b.x, b.y, b.w, b.h))
                self.draw_text(b.text, (b.x + b.w / 2, b.y + 9), size=18, center='center')

    def draw_input(self,inputs):
        for i in inputs:
            # i.dealEvent(event)
            i.draw(self.screen)

    def draw_text(self, text, xy, color=(0, 0, 0), size=18, center=None):
        font = pygame.font.SysFont('simhei', round(size))
        text_obj = font.render(text, 1, color)
        text_rect = text_obj.get_rect()
        if center == 'center':
            text_rect.move_ip(xy[0] - text_rect.w // 2, xy[1])
        else:
            text_rect.move_ip(xy[0], xy[1])
        # print('画文字：',text,text_rect)
        self.screen.blit(text_obj, text_rect)

    # 设置窗口大小
    def set_win_wh(self, w, h, title='python游戏'):
        self.screen2 = pygame.display.set_mode((w, h), pygame.DOUBLEBUF, 32)
        self.screen = self.screen2.convert_alpha()
        pygame.display.set_caption(title)

    def update(self):
        self.screen2.blit(self.screen, (0, 0))
        # 刷新画面
        # pygame.display.update()
        pygame.display.flip()
        time_passed = self.clock.tick(self.fps)

    # 侦听事件
    def my_event(self):
        if self.state == 'ai' and self.next_f == '':
            self.next_f, self.jm = self.ai.get_next(self.game.grid.tiles)
        if self.state == 'm-ai' and self.next_f == '':
            self.next_f, self.jm = self.ai.get_next(self.game.grid.tiles)
        for event in pygame.event.get():
            if event.type == QUIT:
                self.state = 'exit'
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.state = 'exit'
                elif event.key in [K_LEFT, K_a] and self.state == 'run':
                    self.next_f = 'L'
                elif event.key in [K_RIGHT, K_d] and self.state == 'run':
                    self.next_f = 'R'
                elif event.key in [K_DOWN, K_s] and self.state == 'run':
                    self.next_f = 'D'
                elif event.key in [K_UP, K_w] and self.state == 'run':
                    self.next_f = 'U'
                #  k 快,l 慢  ai模式时调整移动快慢
                elif event.key in [K_k, K_l] and self.state == 'ai':
                    if event.key == K_k and self.step_time > 0:
                        self.step_time *= 0.9
                    if event.key == K_l and self.step_time < 10:
                        if self.step_time != 0:
                            self.step_time *= 1.1
                        else:
                            self.step_time = 0.01
                    if self.step_time < 0:
                        self.step_time = 0
                for i in self.input_cell:
                    if(i.active):
                        if(event.key == pygame.K_RETURN):
                            print(i.text)
                            # self.text=''
                        elif(event.key == pygame.K_BACKSPACE):
                            i.text = i.text[:-1]
                        else:
                            i.text += event.unicode
            # if event.type == MOUSEMOTION:
            if event.type == MOUSEBUTTONDOWN:
                self.xy = str(event.pos)
                self.game.grid.xy = event.pos
                self.game.grid.add_manual_tile(event.pos)
                for i in self.button_list:
                    if i.is_click(event.pos):
                        self.state = i.name
                        if i.name == 'ai':
                            i.name = 'run'
                            i.text = '取消托管'
                        elif i.name == 'run':
                            i.name = 'ai'
                            i.text = '电脑托管'
                        elif i.name == 'm-ai':
                            self.state = 'm-ai'
                            i.text = '下一步'
                        
                # for i in self.block:

                for i in self.input_cell:
                    if(i.boxBody.collidepoint(event.pos)):  # 若按下鼠标且位置在文本框
                        i.active = not i.active
                    else:
                        i.active = False
                    i.color = i.color_active if(i.active) else i.color_inactive        
                break                
                                

def run():
    Main().start()


# 按钮类
class Button(pygame.sprite.Sprite):
    def __init__(self, name, text, xy, size=(100, 50)):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.text = text
        self.x, self.y = xy[0], xy[1]
        self.w, self.h = size
        self.is_show = True

    def is_click(self, xy):
        return (self.is_show and
                self.x <= xy[0] <= self.x + self.w and
                self.y <= xy[1] <= self.y + self.h)


class InputBox:
    def __init__(self, rect: pygame.Rect = pygame.Rect(100, 100, 140, 32)) -> None:
        self.boxBody: pygame.Rect = rect
        self.color_inactive = pygame.Color('lightskyblue3')  # 未被选中的颜色
        self.color_active = pygame.Color('dodgerblue2')  # 被选中的颜色
        self.color = self.color_inactive  # 当前颜色，初始为未激活颜色
        self.active = False
        self.text = ''
        self.done = False
        self.font = pygame.font.Font(None, 32)
    
    def dealEvent(self, event: pygame.event.Event):
        if(event.type == pygame.MOUSEBUTTONDOWN):
            if(self.boxBody.collidepoint(event.pos)):  # 若按下鼠标且位置在文本框
                self.active = not self.active
            else:
                self.active = False
            self.color = self.color_active if(
                self.active) else self.color_inactive
        if(event.type == pygame.KEYDOWN):  # 键盘输入响应
            if(self.active):
                if(event.key == pygame.K_RETURN):
                    print(self.text)
                    # self.text=''
                elif(event.key == pygame.K_BACKSPACE):
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode
    
    def draw(self, screen: pygame.surface.Surface):
        txtSurface = self.font.render(
            self.text, True, self.color)  # 文字转换为图片
        width = max(120, txtSurface.get_width()+10)  # 当文字过长时，延长文本框
        self.boxBody.w = width
        screen.blit(txtSurface, (self.boxBody.x+5, self.boxBody.y+5))
        pygame.draw.rect(screen, self.color, self.boxBody, 2)

if __name__ == '__main__':
    run()
