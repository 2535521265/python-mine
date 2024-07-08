import os
import pygame
import random

# 绘制游戏窗口的边框
def drawFrame():
    frame_color = pygame.Color('black') #边框颜色
    # 外部边框
    pygame.draw.line(screen, frame_color, (0, 0), (164, 0), 3)
    pygame.draw.line(screen, frame_color, (164, 0), (164, 217), 3)
    pygame.draw.line(screen, frame_color, (164, 217), (0, 217), 3)
    pygame.draw.line(screen, frame_color, (0, 217), (0, 0), 3)
    # 内部边框
    pygame.draw.line(screen, frame_color, (10, 10), (154, 10), 3)
    pygame.draw.line(screen, frame_color, (154, 10), (154, 53), 3)
    pygame.draw.line(screen, frame_color, (154, 53), (10, 53), 3)
    pygame.draw.line(screen, frame_color, (10, 53), (10, 10), 3)
    pygame.draw.line(screen, frame_color, (10, 63), (154, 63), 3)
    pygame.draw.line(screen, frame_color, (154, 63), (154, 207), 3)
    pygame.draw.line(screen, frame_color, (154, 207), (10, 207), 3)
    pygame.draw.line(screen, frame_color, (10, 207), (10, 63), 3)


# 初始化地雷与数字的数据结构
def initBlock():
    global block_bitset
    #[False, False, False, 9]，分别表示是否翻开、是否标记、是否是地雷以及周围地雷的数量
    block_bitset = [[[False, False, False, 9] for i in range(9)] for i in range(9)]

    random_pos = [] #存储随机生成的地雷位置的空列表
    for remain in range(10, 0, -1): #剩余未生成的地雷数量
        pos = random.randint(1, 81 - remain) #生成的随机位置要在范围内
        if pos not in random_pos: #如果该位置未被使用，将其添加到random_pos列表中
            random_pos.append(pos)
        else:
            random_pos.append(81 - remain)

    for pos in random_pos:
        x = pos // 9 #计算地雷在二维数组中的行、列坐标
        y = pos % 9
        block_bitset[x][y][1] = True #将地雷位置的 "是否标记" 设置为 True
        block_bitset[x][y][3] = 10 #将地雷位置的 "周围地雷数量" 设置为 10

    # 计算每个方块周围的地雷数量
    for i in range(9):#遍历所有方块的行、列
        for j in range(9):
            counts_of_mine_surround = 0 #初始化当前方块周围地雷数量的计数
            if block_bitset[i][j][1] == True: #如果当前方块是地雷，直接跳过
                continue
            for deltax in range(-1, 2, 1): #遍历周围的方块
                for deltay in range(-1, 2, 1):
                    x = i + deltax
                    y = j + deltay
                    if x < 0 or x > 8 or y < 0 or y > 8:# 超出边界就跳过
                        continue
                    if block_bitset[x][y][1] == True: # 如果相邻方块是地雷，增加计数
                        counts_of_mine_surround += 1
            block_bitset[i][j][3] = counts_of_mine_surround


# 绘制游戏中未翻开的方块
def drawBlocks():
    for i in range(9):
        for j in range(9):
            if block_bitset[i][j][2] == 0 and block_bitset[i][j][0] == False:#没有被标记或翻开，就绘制未翻开的方块图片
                screen.blit(blocks[9], (10 + 16 * i, 63 + 16 * j)) #10是起始位置，16是每个方块的宽度
            elif block_bitset[i][j][2] == 1: #标记为旗子
                screen.blit(blocks[13], (10 + 16 * i, 63 + 16 * j))
            elif block_bitset[i][j][2] == 2: #标记为问号
                screen.blit(blocks[14], (10 + 16 * i, 63 + 16 * j))
            elif block_bitset[i][j][0] == False: #未被翻开
                screen.blit(blocks[9], (10 + 16 * i, 63 + 16 * j))
            else: #翻开的方块,根据方块周围的雷的数量显示数字
                screen.blit(blocks[block_bitset[i][j][3]], (10 + 16 * i, 63 + 16 * j))

# 绘制游戏成功的状态
def drawSuccess():
    for i in range(9):
        for j in range(9):
            if block_bitset[i][j][1] == True: #地雷
                screen.blit(blocks[10], (10 + 16 * i, 63 + 16 * j))
            else: #数字
                screen.blit(blocks[block_bitset[i][j][3]], (10 + 16 * i, 63 + 16 * j))

# 绘制游戏失败的状态
def drawFail(x, y):
    for i in range(9):
        for j in range(9):
            flag_mine = block_bitset[i][j][1] #地雷
            flag_marked = block_bitset[i][j][2] #标记
            if i == x and j == y: #如果当前方块的坐标与游戏失败的位置匹配,绘制标红的雷
                screen.blit(blocks[12], (10 + 16 * i, 63 + 16 * j))
                continue
            if flag_mine == False and flag_marked == True:#如果当前方块不是地雷且被标记为地雷,绘制错误标记的方块的图像
                screen.blit(blocks[11], (10 + 16 * i, 63 + 16 * j))
            elif flag_mine == True: #显示地雷
                screen.blit(blocks[10], (10 + 16 * i, 63 + 16 * j))
            else:#数字
                screen.blit(blocks[block_bitset[i][j][3]], (10 + 16 * i, 63 + 16 * j))


# 扩展空白区域，即点击空白方块后展开相邻的空白方块
def expandBlank(x, y):
    global remain_blocks_count #未被翻开的方块数量
    position_queue = [(x, y)]
    for position in position_queue:
        for deltax in range(-1, 2, 1): #在当前方块周围的行\列进行遍历
            for deltay in range(-1, 2, 1):
                new_x = position[0] + deltax #行坐标
                new_y = position[1] + deltay #列坐标
                if new_x == x and new_y == y:
                    continue
                if new_x < 0 or new_x > 8 or new_y < 0 or new_y > 8:
                    continue
                if block_bitset[new_x][new_y][0] == True: #如果相邻方块已经被翻开，则跳过
                    continue

                block_bitset[new_x][new_y][0] = True #将相邻方块标记为已翻开
                block_bitset[new_x][new_y][2] = 0 #将相邻方块的标记状态重置为未标记
                remain_blocks_count -= 1
                if block_bitset[new_x][new_y][3] == 0:#如果相邻方块是空白方块（周围没有地雷），则将其坐标加入队列，以进一步展开
                    position_queue.append((new_x, new_y))


# 处理鼠标点击事件
def handleClick(position, right):
    global running
    global mines_count #地雷数量
    global remain_blocks_count #剩余未被翻开的方块数量

    x = int((position[0] - 10) / 16)
    y = int((position[1] - 63) / 16)
    # 检查坐标是否合法
    if x < 0 or x > 8 or y < 0 or y > 8:
        return

    if block_bitset[x][y][0] == True: #如果方块已经被翻开，就不处理该方块
        return

    # 鼠标右键点击
    if not right:
        if block_bitset[x][y][2] == 0: #如果方块未被标记，将其标记为地雷
            block_bitset[x][y][2] = 1
        elif block_bitset[x][y][2] == 1: #如果方块已经标记为地雷，将其标记为问号
            block_bitset[x][y][2] = 2
        else: #如果方块已经标记为问号，将其标记还原为未标记状态
            block_bitset[x][y][2] = 0
        return

    # 鼠标左键点击
    if block_bitset[x][y][1] == True:#点到雷则显示红雷,游戏结束
        drawFail(x, y)
        running = False
        return
    remain_blocks_count -= 1
    block_bitset[x][y][0] = True #将点击的方块标记为已翻开
    block_bitset[x][y][2] = 0 #将点击的方块的标记状态重置为未标记
    if block_bitset[x][y][3] == 0: #点到空白则展开
        expandBlank(x, y)
    if remain_blocks_count == mines_count: #未翻开的方块数量等于地雷数量，则成功
        drawSuccess()
        running = False

# 绘制计数器中的数字
def drawNumber(number, time):
    #雷的数量
    number0 = int(number / 100 % 10) #百位
    number1 = int(number / 10 % 10) #十位
    number2 = int(number % 10) #个位
    #时间秒数
    time0 = int(time / 100 % 10)
    time1 = int(time / 10 % 10)
    time2 = int(time % 10)

    screen.blit(number_blocks[number0], (20, 20))
    screen.blit(number_blocks[number1], (33, 20))
    screen.blit(number_blocks[number2], (46, 20))

    screen.blit(number_blocks[time0], (105, 20))
    screen.blit(number_blocks[time1], (118, 20))
    screen.blit(number_blocks[time2], (131, 20))


pygame.init()
pygame.display.set_icon(pygame.image.load(os.path.join("resources", "images", "10.ico")))#窗口图标
width, height = 164, 217
screen = pygame.display.set_mode((width, height)) #窗口宽高
pygame.display.set_caption('扫雷')
white_color = pygame.Color('white') #背景颜色

# 载入游戏方块和数字图片
block_names = [os.path.join("resources", "images", str(x) + ".ico") for x in range(15)]
blocks = [pygame.image.load(block_name) for block_name in block_names]

number_block_names = [os.path.join("resources", "images", "d" + str(x) + ".ico") for x in range(10)]
number_blocks = [pygame.image.load(number_block_name) for number_block_name in number_block_names]

# 初始化游戏变量
current_second = 0 #初始化当前秒数
last_second = current_second #初始化上一秒的秒数
block_bitset = []
mines_count = 10
remain_blocks_count = 9 * 9
running = True
initBlock() #初始游戏方块状态

while running: #更新游戏状态、绘制游戏界面
    screen.fill('white') #窗口填充白色
    drawFrame()
    drawNumber(mines_count, current_second)
    drawBlocks()
    pygame.display.flip()
    current_second = pygame.time.get_ticks() / 1000 #获取当前的游戏时间
    if current_second != last_second:
        last_second = current_second #变化就一直更新时间
    else:
        current_second = last_second

    for event in pygame.event.get():#鼠标操作
        if event.type == pygame.QUIT:#退出
            pygame.quit()
            exit(0)
        if event.type == pygame.MOUSEBUTTONDOWN:
            right = pygame.mouse.get_pressed()[0]#鼠标右键
            left = pygame.mouse.get_pressed()[2]#鼠标左键
            position = pygame.mouse.get_pos()#点击的位置
            if right:
                handleClick(position, True)
            elif left:
                handleClick(position, False)

# 游戏结束后等待用户关闭窗口
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit(0)
    pygame.display.flip() #更新屏幕显示


