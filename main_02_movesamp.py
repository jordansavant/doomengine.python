screen = [1, 1, 2, 2, 2, 1]
print(screen)

screen[3] = 8
print(screen)

playerpos = 2
screen[playerpos] = 8
print(screen)

print('---')

background = [1, 1, 2, 2, 2, 1]
screen = [0]*6
for i in range(6):
    screen[i] = background[i]
print(screen)

playerpos = 3
screen[playerpos] = 8
print(screen)