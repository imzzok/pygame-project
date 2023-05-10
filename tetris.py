""" tetris.py - Copyright 2016 Kenichiro Tanaka """
import sys # 프로그램 종료 함수 호출
from math import sqrt
from random import randint
import pygame
import time
from tkinter import messagebox

# 전역 변수
pygame.init() # 파이게임을 사용하겠다고 알려줌
pygame.display.set_caption('TETRIS GAME WINDOW') #파이게임 윈도우 이름
smallfont = pygame.font.SysFont(None, 36)
largefont = pygame.font.SysFont(None, 72)
pygame.init()
background_sound = pygame.mixer.Sound("C:\BGM Tetris Bradinsky.mp3") #추가기능: 배경음
background_sound.play(-1)
gameover_sound = pygame.mixer.Sound("C:\gameover.mp3") #추가기능: 게임오버 사운드


BLACK = (0,0,0)
pygame.key.set_repeat(30, 30)
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
WIDTH = 12 # 벽을 위한 10 + 2
HEIGHT = 21 # 20 + 1
INTERVAL = 40
# 필드 값 구현
FIELD = [[0 for _ in range(WIDTH)] for _ in range(HEIGHT) ]
COLORS = ((0, 0, 0), (255, 165, 0), (0, 0, 255), (0, 255, 255), \
          (0, 255, 0), (255, 0, 255), (255, 255, 0), (255, 0, 0), (128, 128, 128))
BLOCK = None
NEXT_BLOCK = None
PIECE_SIZE = 24 # 24 x 24
PIECE_GRID_SIZE = PIECE_SIZE+1 
BLOCK_DATA = (
    (
        (0, 0, 1, \
         1, 1, 1, \
         0, 0, 0),
        (0, 1, 0, \
         0, 1, 0, \
         0, 1, 1),
        (0, 0, 0, \
         1, 1, 1, \
         1, 0, 0),
        (1, 1, 0, \
         0, 1, 0, \
         0, 1, 0),
    ), (
        (2, 0, 0, \
         2, 2, 2, \
         0, 0, 0),
        (0, 2, 2, \
         0, 2, 0, \
         0, 2, 0),
        (0, 0, 0, \
         2, 2, 2, \
         0, 0, 2),
        (0, 2, 0, \
         0, 2, 0, \
         2, 2, 0)
    ), (
        (0, 3, 0, \
         3, 3, 3, \
         0, 0, 0),
        (0, 3, 0, \
         0, 3, 3, \
         0, 3, 0),
        (0, 0, 0, \
         3, 3, 3, \
         0, 3, 0),
        (0, 3, 0, \
         3, 3, 0, \
         0, 3, 0)
    ), (
        (4, 4, 0, \
         0, 4, 4, \
         0, 0, 0),
        (0, 0, 4, \
         0, 4, 4, \
         0, 4, 0),
        (0, 0, 0, \
         4, 4, 0, \
         0, 4, 4),
        (0, 4, 0, \
         4, 4, 0, \
         4, 0, 0)
    ), (
        (0, 5, 5, \
         5, 5, 0, \
         0, 0, 0),
        (0, 5, 0, \
         0, 5, 5, \
         0, 0, 5),
        (0, 0, 0, \
         0, 5, 5, \
         5, 5, 0),
        (5, 0, 0, \
         5, 5, 0, \
         0, 5, 0)
    ), (
        (6, 6, \
        6, 6),
        (6, 6, \
        6, 6),
        (6, 6, \
        6, 6),
        (6, 6, \
        6, 6)
    ), (
        (0, 7, 0, 0, \
         0, 7, 0, 0, \
         0, 7, 0, 0, \
         0, 7, 0, 0),
        (0, 0, 0, 0, \
         7, 7, 7, 7, \
         0, 0, 0, 0, \
         0, 0, 0, 0),
        (0, 0, 7, 0, \
         0, 0, 7, 0, \
         0, 0, 7, 0, \
         0, 0, 7, 0),
        (0, 0, 0, 0, \
         0, 0, 0, 0, \
         7, 7, 7, 7, \
         0, 0, 0, 0)
    )
)

                
class Block:
    """ 블록 모양을 랜덤으로 변경
        블록 모양이 다 정의되어 있으므로 블록 모양을 선택해주기만 하면 됨 """
    def __init__(self, count):
        self.turn = randint(0,3)
        self.type = BLOCK_DATA[randint(0, 6)]
        self.data = self.type[self.turn]
        self.size = int(sqrt(len(self.data)))
        self.xpos = randint(2, 8 - self.size)
        self.ypos = 1 - self.size
        self.fire = count + INTERVAL

    def update(self, count):
        """ 블록 상태 갱신 (소거한 단의 수를 반환한다) """
        # 아래로 충돌?
        erased = 0
        if is_overlapped(self.xpos, self.ypos + 1, self.turn):
            for y_offset in range(BLOCK.size):
                for x_offset in range(BLOCK.size):
                    index = y_offset * self.size + x_offset
                    val = BLOCK.data[index]
                    if 0 <= self.ypos+y_offset < HEIGHT and \
                       0 <= self.xpos+x_offset < WIDTH and val != 0:
                            FIELD[self.ypos+y_offset][self.xpos+x_offset] = val ## 값을 채우고, erase_line()을 통해 삭제되도록 한다.

            erased = erase_line()
            go_next_block(count)

        if self.fire < count:
            self.fire = count + INTERVAL
            self.ypos += 1
        return erased

    
    def draw(self):
        """ 블록을 그린다, 낙하 중인 현재 블록을 화면에 표현, self data는 1차원 데이터이고
        도형은 2차원이다. self.size 사용해 구현 """
        ## 블록의 조각의 데이터 구하기, 블록이 내려오는 시작점은 (self.xpos, self.ypos)
        for y_offset in range(self.size):
            for x_offset in range(self.size):
                index = y_offset * self.size + x_offset
                val = self.data[index]
                if 0 <= y_offset + self.ypos < HEIGHT and \
                   0 <= x_offset + self.xpos < WIDTH and val != 0:
                    ## f_xpos = filed에서의 xpos를 계산함
                    f_xpos = PIECE_GRID_SIZE + (x_offset + self.xpos) * PIECE_GRID_SIZE
                    f_ypos = PIECE_GRID_SIZE + (y_offset + self.ypos) * PIECE_GRID_SIZE
                    pygame.draw.rect(screen, COLORS[val],
                                    (f_xpos, 
                                    f_ypos, 
                                    PIECE_SIZE, 
                                    PIECE_SIZE))
                                    
def draw_current_block():
    BLOCK.draw()

def erase_line():
    """ 행이 꽉 채워진 줄은 지워짐,
        예: 그 줄의 값이 10이라면 10이 채워지면 지워짐, 10은 점수로 반환 """
    erased = 0
    erased = 0
    ypos = HEIGHT-2
    print(FIELD[ypos])
    while ypos >=0:
        if  all(FIELD[ypos]) == True:
            del FIELD[ypos]
            FIELD.insert(0, [8, 0,0,0,0,0,0,0,0,0,0 ,8])
            erased += 1
        else:
            ypos -= 1
    return erased
    return erased

def is_game_over():
    """ 필드의 최상단에 블록이 쌓이면 종료
        게임 종료 조건: 창을 끄지 않는 한 블록이 화면 윗까지 다 차면 오버,
        가장 최상단의 필드를 검사  """
    filled = 0
    for cell in FIELD[0]:
        if cell != 0:
            filled += 1
    return filled > 2 # 2 = 좌우의 벽 제외
    pass

def go_next_block(count):
    """ 블록을 생성하고, 다음 블록으로 전환한다 """
    global BLOCK, NEXT_BLOCK
    BLOCK = NEXT_BLOCK if NEXT_BLOCK != None else Block(count)
    NEXT_BLOCK = Block(count)

def is_overlapped(xpos, ypos, turn):
    """ 도형이 벽을 뚫고 밖으로 나가지 않게 하는 역할 """
    data = BLOCK.type[turn]
    for y_offset in range(BLOCK.size):
        for x_offset in range(BLOCK.size):
            index = y_offset * BLOCK.size + x_offset
            val = data[index]

            if 0 <= xpos+x_offset < WIDTH and \
                0 <= ypos+y_offset < HEIGHT:
                if val != 0 and \
                    FIELD[ypos+y_offset][xpos+x_offset] != 0:
                    return True
    return False
    pass

def set_game_field():
    """ 게임을 할 필드 표현, 필드 값 설정 """
    for i in range(HEIGHT-1):
        FIELD.insert(0, [8, 0,0,0,0,0,0,0,0,0,0 ,8])
    
    FIELD.insert(HEIGHT-1, [8, 8,8,8,8,8,8,8,8,8,8 ,8])
    #print(FIELD)
    pass

def draw_game_field():
    """ 설정된 필드를 화면에 출력  """
    for y_offset in range(HEIGHT):
        for x_offset in range(WIDTH):
            val = FIELD[y_offset][x_offset]
            color = COLORS[val]
            pygame.draw.rect(screen, 
                            color,
                            (PIECE_GRID_SIZE + x_offset*PIECE_GRID_SIZE, 
                            PIECE_GRID_SIZE + y_offset*PIECE_GRID_SIZE , 
                            PIECE_SIZE , 
                            PIECE_SIZE ))
    #pass
    pass

def draw_current_block():
        BLOCK.draw()
        pass

def draw_next_block():
    """ 다음 블록을 나타내는 함수 """
    ## 현재 블록을 나타낸 함수와 같이 조각 데이터를 구한다.
    for y_offset in range(NEXT_BLOCK.size):
        for x_offset in range(NEXT_BLOCK.size):
            index = y_offset * NEXT_BLOCK.size + x_offset
            val = NEXT_BLOCK.data[index]
            #if 0 <= y_offset + self.ypos < HEIGHT and \
            #   0 <= x_offset + self.xpos < WIDTH and 
            if val != 0: ## 이 조건은 중요함! 0까지 그림을 그린다면, 쌓인 블록이 순간적으로 검정색이 됨.
                ## f_xpos = filed에서의 xpos를 계산함
                f_xpos = 460 + (x_offset) * PIECE_GRID_SIZE
                f_ypos = 100 + (y_offset) * PIECE_GRID_SIZE
                pygame.draw.rect(screen, COLORS[val],
                                (f_xpos, 
                                f_ypos, 
                                PIECE_SIZE, 
                                PIECE_SIZE))
    pass

def draw_score(score):
    """ 점수를 표시하는 함수 (지워진 단의 숫자가 점수로 표현) """
    score_str = str(score).zfill(6)
    score_image = smallfont.render(score_str, True, (0, 255, 0))
    screen.blit(score_image, (500, 30))
    pass
        
def draw_gameover_message():
        # 게임오버 메시지_ 추가 기능
        message_over = largefont.render("GAME OVER!!", True, (255, 255, 255))
        message_rect = message_over.get_rect()
        message_rect.center = (300, 300)
        screen.blit(message_over, message_rect)
        pass

def runGame():
    """ 메인 루틴 """
    global INTERVAL
    count = 0
    score = 0
    game_over = False
    
    go_next_block(INTERVAL)

    set_game_field()

    while True:
        clock.tick(10)
        screen.fill(BLACK)

        key = None
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                key = event.key
            elif event.type == pygame.KEYUP:
                key = None

        game_over = is_game_over()
        if not game_over:
            count += 5 # 추가 구현 기능: 게임이 진행됨에 따라 블록 드롭 속도가 점점 빨라짐
            if count % 1000 == 0:
                INTERVAL = max(1, INTERVAL - 2)
            erased = BLOCK.update(count)

            if erased > 0:
                score += (2 ** erased) * 100

            # 키 이벤트 처리
            """ 객체 변수 xpos. ypos, turn, data 변경해 키 입력받아 블록 변경 """
            next_x, next_y, next_t = \
                BLOCK.xpos, BLOCK.ypos, BLOCK.turn
            if key == pygame.K_UP:
                next_t = (next_t + 1) % 4
            elif key == pygame.K_RIGHT:
                next_x += 1
            elif key == pygame.K_LEFT:
                next_x -= 1
            elif key == pygame.K_DOWN:
                next_y += 1
            if key == pygame.K_ESCAPE:# 추가 기능: esc를 누르면 게임 종료 
                pygame.quit()
                sys.exit()
            if key == pygame.K_p:
                time_duration = 5 # 추가 기능: p 버튼을 누르면 5초간 게임 일시정지
                time.sleep(time_duration)
            elif key == pygame.K_r:
                # 추가 기능: r 버튼을 누르면 메시지박스가 뜨고 다시 시도 누르면 게임 재시작, 취소 누르면 게임 종료
                if messagebox.askretrycancel("R 버튼을 누르셨습니다!",
                                             "다시 시도 버튼 또는 R을 한 번 더 누르면 게임이 재시작되며   취소 버튼을 누르면 게임이 종료됩니다.") == True:
                    runGame()

                else :
                    pygame.quit()
                

            if not is_overlapped(next_x, next_y, next_t):
                BLOCK.xpos = next_x
                BLOCK.ypos = next_y
                BLOCK.turn = next_t
                BLOCK.data = BLOCK.type[BLOCK.turn]



        # 게임필드 그리기
        draw_game_field()

        # 낙하 중인 블록 그리기
        draw_current_block()

        # 다음 블록 그리기
        draw_next_block()
        
        # 점수 나타내기
        draw_score(score)
        
        # 게임 오버 메시지 
        if game_over:
            draw_gameover_message()
            gameover_sound.play()
            background_sound.stop()
 
        pygame.display.update()

runGame()
pygame.quit()
