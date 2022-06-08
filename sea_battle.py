import random


class BoardOutException(Exception):
    pass


class DirectionException(Exception):
    pass


class RepeatedShotException(Exception):
    pass


class Dot:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    @property
    def x(self):
        return self.a

    @property
    def y(self):
        return self.b

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y


class Ship:
    def __init__(self, masts, head_point, direction):
        self.masts = masts
        self.head_point = head_point
        self.direction = direction
        self.lives = masts
        self.cont_dots = []

    @property
    def dots(self):
        dot_list = []
        for i in range(self.masts):
            if self.direction == "H":
                x = self.head_point.x
                y = self.head_point.y + i
                point = Dot(x, y)
                dot_list.append(point)
            elif self.direction == "V":
                x = self.head_point.x + i
                y = self.head_point.y
                point = Dot(x, y)
                dot_list.append(point)
            else:
                raise DirectionException("Такого направления не существует")
        return dot_list


class Board:
    def __init__(self, hid):
        self.field = [["o" for row in range(6)] for column in range(6)]
        self.hid = hid
        self.live_ships = 0
        self.ships = []
        self.contour_dots = []
        self.dot_shots = []
        self.f_p = []
        for row in range(6):
            for column in range(6):
                self.f_p.append(Dot(row, column))

    def clear_board(self):
        self.field = [["o" for row in range(6)] for column in range(6)]
        self.live_ships = 0
        self.ships = []
        self.contour_dots = []
        self.dot_shots = []
        self.f_p = []
        for row in range(6):
            for column in range(6):
                self.f_p.append(Dot(row, column))

    @property
    def fields_points(self):
        return self.f_p

    def update_f_p(self):
        self.f_p = []
        for row in range(6):
            for column in range(6):
                self.f_p.append(Dot(row, column))

    def add_ship(self, ship):
        correct = False
        for dot in ship.dots:
            if not self.out(dot) and dot not in self.contour_dots:
                correct = True
                continue
            else:
                correct = False
                break
        if correct:
            self.contour(ship)
            self.ships.append(ship)
            self.live_ships += 1
            for dot in ship.dots:
                self.field[dot.x][dot.y] = "■"
            return True
        else:
            return False

    def get_board(self):
        printed_field = '|-----|-----|-----|-----|-----|-----|-----|\n' \
                        '|     |  1  |  2  |  3  |  4  |  5  |  6  |\n' \
                        '|-----|-----|-----|-----|-----|-----|-----|\n'
        k = 1
        for row in self.field:
            printed_field += f"|  {k}  |"
            for column in row:
                if self.hid:
                    if column != "x" and column != "T":
                        printed_field += f"  o  |"
                    else:
                        printed_field += f"  {column}  |"
                else:
                    printed_field += f"  {column}  |"
            printed_field += "\n|-----|-----|-----|-----|-----|-----|-----|\n"
            k += 1
        print(printed_field)

    def contour(self, ship):
        for row in range(ship.dots[0].x - 1, ship.dots[-1].x + 2):
            for i in range(ship.dots[0].y - 1, ship.dots[-1].y + 2):
                dot = Dot(row, i)
                if not self.out(dot) and dot not in self.contour_dots:
                    self.contour_dots.append(dot)

    def out(self, dot):
        if 0 <= dot.x < 6 and 0 <= dot.y < 6:
            return False
        else:
            return True

    def shot(self, dot):
        repeat = False

        if dot not in self.dot_shots and not self.out(dot):
            self.dot_shots.append(dot)
            removed_ship = None
            for ship in self.ships:
                removed_ship = ship
                if dot in removed_ship.dots:
                    removed_ship.lives -= 1
                    break
            if removed_ship.lives == 0:
                self.ships.remove(removed_ship)
                self.live_ships -= 1
                print("Убил")
            else:
                print("Ранил")
            if self.field[dot.x][dot.y] == "■":
                self.field[dot.x][dot.y] = "x"
                repeat = True
            else:
                self.field[dot.x][dot.y] = "T"
                repeat = False
        else:
            repeat = True
            raise BoardOutException("Попытка выстрела за пределы поля")
        return repeat


class Player:
    def __init__(self, player_board, opponent_board):
        self.player_board = player_board
        self.opponent_board = opponent_board

    def ask(self):
        dot = Dot(0, 0)
        return dot

    def move(self):
        dot = self.ask()
        try:
            repeat = self.opponent_board.shot(dot)
        except BoardOutException as e:
            print("выберите другие координаты")
            return True
        return repeat


class User(Player):
    def ask(self):
        user_shot = input("Введите координаты хода: ").split()
        x = int(user_shot[0]) - 1
        y = int(user_shot[1]) - 1
        dot = Dot(x, y)
        return dot


class AI(Player):
    def ask(self):
        dot = random.choice(self.opponent_board.fields_points)
        self.opponent_board.fields_points.remove(dot)
        return dot


class Game:
    def __init__(self):
        self.user_board = Board(False)
        self.ai_board = Board(True)
        self.random_board(self.user_board)
        self.random_board(self.ai_board)
        self.user = User(self.user_board, self.ai_board)
        self.comp = AI(self.ai_board, self.user_board)

    def random_board(self, board):
        cycle = 0
        while True:
            ship = None
            dot = random.choice(board.fields_points)
            direction = random.randrange(0, 2)
            if direction == 0:
                direction = "H"
            else:
                direction = "V"
            if len(board.ships) < 1:
                ship = Ship(3, dot, direction)
            elif len(board.ships) < 3:
                ship = Ship(2, dot, direction)
            else:
                ship = Ship(1, dot, direction)
            board.add_ship(ship)
            cycle += 1
            if cycle > 3000 or len(board.ships) == 7:
                break
        if len(board.ships) < 7:
            board.clear_board()
            self.random_board(board)
        board.update_f_p()
        return board

    def greet(self):
        print(f"Привет!\n"
              f"Добро пожаловать в игру морской бой!\n"
              f"все что тебе нужно знать об иггровом процессе:\n"
              f"1. выбери координату точки на вражеском поле и введи ее: "
              f"'1 1' - вводить нужно через пробел. сначала вертикаьную потом горизонтальную\n"
              f"2. если попал повтори шаг 1, если нет жди хода компьютера\n"
              f"3. Победит тот, кто первым уничтожит все вражеские корабли!\n "
              f"('о')- море\n "
              f"('x') - попадание\n"
              f"('■') - Твои корабли\n"
              f"Удачи и приятной игры!\n"
              f"Начнем!")
        input("Для начала игры нажмите enter")

    def loop(self):
        user_queue = random.randrange(1, 2)
        self.ai_board.get_board()
        self.user_board.get_board()
        while True:
            if user_queue == 1:
                while self.user.move() and len(self.ai_board.ships) > 1:
                    self.ai_board.get_board()
                    self.user_board.get_board()
                if len(self.ai_board.ships) < 1:
                    break
                else:
                    self.ai_board.get_board()
                    self.user_board.get_board()
                    user_queue = 2
            else:
                while self.comp.move() and len(self.user_board.ships) > 1:
                    self.ai_board.get_board()
                    self.user_board.get_board()
                if len(self.user_board.ships) < 1:
                    break
                else:
                    self.ai_board.get_board()
                    self.user_board.get_board()
                    user_queue = 1
        if len(self.user_board.ships) < 1:
            print("Проиграл!")

        elif len(self.ai_board.ships) < 1:
            print("Поздавляю! ПОБЕДА")


    def start(self):
        self.greet()
        self.loop()

game = Game()
game.start()