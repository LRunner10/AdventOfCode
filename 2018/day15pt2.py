from typing import List

data = open('text.txt').readlines()

lenX = len(data[0])
lenY = len(data)


class Character:
    def __init__(self, isGob, x, y, elf_attack):
        self.is_goblin = isGob
        self.hit_points = 200
        self.attack = 3 if isGob else elf_attack
        self.x = x
        self.y = y
        self.move_count = 0
    
    def attack_action(self, chars: dict):
        min_char_enemy: Character = None
        for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
            if chars.get((self.x+dx, self.y+dy)) is not None and chars[(self.x+dx, self.y+dy)].is_goblin != self.is_goblin:
                if min_char_enemy is None:
                    min_char_enemy = chars[(self.x+dx, self.y+dy)]
                elif min_char_enemy.hit_points>chars[(self.x+dx, self.y+dy)].hit_points:
                    min_char_enemy = chars[(self.x+dx, self.y+dy)]
                elif min_char_enemy.hit_points==chars[(self.x+dx, self.y+dy)].hit_points and min_char_enemy.y>self.y+dy:
                    min_char_enemy = chars[(self.x+dx, self.y+dy)]
                elif min_char_enemy.hit_points==chars[(self.x+dx, self.y+dy)].hit_points and min_char_enemy.y==self.y+dy and min_char_enemy.x>self.x+dx:
                    min_char_enemy = chars[(self.x+dx, self.y+dy)]
        
        if min_char_enemy is not None:
            min_char_enemy.hit_points -= self.attack
            if min_char_enemy.hit_points <= 0:
                chars.pop((min_char_enemy.x, min_char_enemy.y))
            return True
        
        return False

    #Return (x, y, path_len, first x move, first y move)
    def find_target_pos(self):
        visited = set()

        options = [(0, -1), (-1, 0), (1, 0), (0, 1)]
        paths = [(self.x+dx, self.y+dy, 1, dx, dy) for dx, dy in options]
        visited.add((self.x, self.y))

        best_target = None
        while len(paths)>0:
            curr_x, curr_y, path_len, fdx, fdy = paths.pop(0)

            if best_target is not None and best_target[2]<path_len: continue
            if (curr_x, curr_y) in walls: continue
            if (curr_x, curr_y) in visited: continue

            if (curr_x, curr_y) in characters:

                #If the two characters are on the same team skip
                if characters[(curr_x, curr_y)].is_goblin == self.is_goblin: continue


                if best_target is None:
                    best_target = (curr_x, curr_y, path_len, fdx, fdy)
                elif best_target[2]>path_len:
                    best_target = (curr_x, curr_y, path_len, fdx, fdy)
                elif best_target[1]>curr_y or (best_target[1]==curr_y and best_target[0]>curr_x):
                    best_target = (curr_x, curr_y, path_len, fdx, fdy)
                elif best_target[1]==curr_y and best_target[0]==curr_x and (fdy==-1 or (fdx==-1 and best_target[4]!=-1) or (fdx==1 and best_target[4]==1)):
                    best_target = (curr_x, curr_y, path_len, fdx, fdy)
                
                continue

            visited.add((curr_x, curr_y))
            
            for dx, dy in options:
                paths.append((curr_x+dx, curr_y+dy, path_len+1, fdx, fdy))
        
        return best_target


    def take_action(self, tc, chars: dict):
        if tc<self.move_count: return chars

        self.move_count +=1

        if self.attack_action(chars): return chars
        
        move_data = self.find_target_pos()
        if move_data is None: 
            return chars
        nx, ny, p_len, fdx, fdy = move_data

        chars[(self.x+fdx, self.y+fdy)] = chars.pop((self.x, self.y))

        self.x += fdx
        self.y += fdy
        self.attack_action(chars)

        return chars

characters: dict[tuple, Character] = dict()


def print_board():
    for y in range(lenY):
        string = ''
        charss = ''
        for x in range(lenX):
            if (x, y) in walls: string += '#'
            elif (x, y) in characters: 
                string += 'G' if characters[(x, y)].is_goblin else 'E'
                charss += 'G' if characters[(x, y)].is_goblin else 'E'
                charss += '(' + str(characters[(x, y)].hit_points) + '), '
            else: string += '.'
        
        print(string+'  '+charss)

    print()


def run_game(power):
    global characters
    elf_count = 0
    walls.clear()
    characters.clear()
    #Set Game Board
    for y, row in enumerate(data):
        for x, char in enumerate(row):
            if char == '#': 
                walls.add((x, y))
            elif char in ['G', 'E']:
                characters[(x, y)] = Character(char=='G', x, y, power)
                if char=='E': elf_count +=1

    #Round looper
    turn_count = 0
    while True:
        #print('Turn:', turn_count)
        for y in range(lenY):
            for x in range(lenX):
                if characters.get((x, y)) is not None:
                    characters = characters[(x, y)].take_action(turn_count, characters)
                    if sum(1 if not c.is_goblin else 0 for c in characters.values())!=elf_count:
                        # print_board()
                        #print(turn_count, sum(c.hit_points for c in characters.values()), (turn_count)*sum(c.hit_points for c in characters.values()))

                        return -1
                    
                    if len(characters.values())==elf_count:
                        if all(c.move_count>turn_count for c in characters.values()): turn_count +=1
                        #print_board()
                        print(turn_count, sum(c.hit_points for c in characters.values()), (turn_count)*sum(c.hit_points for c in characters.values()))
                        exit()

    
        turn_count+=1

elf_pow = 4

walls = set()
while True:
    print('elf Power:', elf_pow)
    run_game(elf_pow)
    elf_pow +=1
