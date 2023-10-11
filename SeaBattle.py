from random import randint, choice


class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'


class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Выстрел за пределы доски'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'В эту клетку уже стреляли'


class BoardWrongShipException(BoardException):
    pass


class Ship:
    def __init__(self, start_point, length, orient):
        self.start_point = start_point
        self.length = length
        self.orient = orient
        self.health = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            cur_x = self.start_point.x
            cur_y = self.start_point.y
            if self.orient == 'hor':
                cur_x += i

            elif self.orient == 'vert':
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))
        return ship_dots


class Board:
    def __init__(self, hid=False, size=6):
        self.size = size
        self.hid = hid
        self.count = 0
        self.field = [['О' for _ in range(size)] for _ in range(size)]
        self.busy = []
        self.ships = []

    def __str__(self):
        res = ''
        res += f'''{' ':<2}|{'|'.join([f'{col + 1:^3}' for col in range(self.size)])}|'''
        for num, row in enumerate(self.field):
            res += f'''\n{num + 1:<2}| {' | '.join(row):^3} |'''

        if self.hid:
            res.replace('■', 'О')
        return res

    def dot_in_board(self, dot):
        return dot.x in range(1, self.size + 1) and dot.y in range(1, self.size + 1)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (0, -1), (1, -1),
            (-1, 0), (0, 0), (1, 0),
            (-1, 1), (0, 1), (1, 1)
        ]
        for dot in ship.dots:
            for dx, dy in near:
                cur = Dot(dot.x + dx, dot.y + dy)
                if self.dot_in_board(cur) and cur not in self.busy:
                    if verb:
                        self.field[cur.y - 1][cur.x - 1] = '.'
                    self.busy.append(cur)

    def add_ship(self, ship):
        for dot in ship.dots:
            if not self.dot_in_board(dot) or dot in self.busy:
                raise BoardWrongShipException()
        for dot in ship.dots:
            self.field[dot.y - 1][dot.x - 1] = '■'
            self.busy.append(dot)
        self.ships.append(ship)
        self.contour(ship)

    def shot(self, dot):
        if not self.dot_in_board(dot):
            raise BoardOutException
        if dot in self.busy:
            raise BoardUsedException
        self.busy.append(dot)

        for ship in self.ships:
            if dot in ship.dots:
                ship.health -= 1
                self.field[dot.y - 1][dot.x - 1] = 'X'
                if ship.health == 0:
                    self.count += 1
                    self.contour(ship, True)
                    print('Корабль уничтожен!')
                    return True
                else:
                    print('Корабль ранен!')
                    return True
        self.field[dot.y - 1][dot.x - 1] = 'T'
        print('Мимо!')
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)

    def combined_boards(self):
        combined_boards = zip(self.board.field, self.enemy.field)
        result = ''
        result += f"{'Доска Пользователя:':^27}{' ':^21}{'Доска Компьютера:':^27}\n"
        result += f'''\n{' ':<2}|{'|'.join([f'{col + 1:^3}' for col in range(self.board.size)])}|{'|':^21}\
{' ':<2}|{'|'.join([f'{col + 1:^3}' for col in range(self.board.size)])}|'''
        for num, (us_row, ai_row) in enumerate(combined_boards):
            result += f'''\n{num + 1:<2}| {' | '.join(us_row)} {'|'}{'|':^21}{num + 1:<2}| {' | '.join(ai_row)} {'|'}'''
        result += '\n'
        return result


class AI(Player):
    def ask(self):
        dot = Dot(randint(1, 6), randint(1, 6))
        print(f"Ход компьютера: {dot.x} {dot.y}")
        return dot


class User(Player):
    def ask(self):
        while True:
            coords = input('Ваш ход: ').split()
            x, y = coords[0], coords[1]
            if len(coords) != 2:
                print('Введите 2 координаты!')
            if not x.isdigit() or not y.isdigit():
                print('Введите числа!')
            x, y = int(x), int(y)
            return Dot(x, y)


class Game:
    ship_lens = [3, 2, 2, 1, 1, 1, 1]

    def __init__(self, size=6):
        self.size = size
        player = self.random_board()
        computer = self.random_board()
        computer.hid = True
        self.check_hid(computer)
        self.ai = AI(computer, player)
        self.us = User(player, computer)

    def check_hid(self, player):
        for ship in player.ships:
            for dot in ship.dots:
                if player.hid:
                    player.field[dot.y - 1][dot.x - 1] = 'О'

    def try_board(self):
        board = Board(size=self.size)
        attempts = 0
        for i in self.ship_lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(1, self.size), randint(1, self.size)), i, choice(('hor', 'vert')))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    @staticmethod
    def greet():
        print("-" * 75)
        print(f"{'Приветсвуем вас в игре:':^75}")
        print(f"{'МОРСКОЙ БОЙ':^75}")
        print("-" * 75)
        print(" формат ввода: x y ")
        print(" x - координата по горизонтали  ")
        print(" y - координата по вертикали ")

    def loop(self):
        num = 0
        while True:
            print('-' * 75)
            print(self.us.combined_boards())
            print('-' * 75)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == len(self.ship_lens):
                print("-" * 75)
                print("Пользователь выиграл!")
                break

            if self.us.board.count == len(self.ship_lens):
                print("-" * 75)
                print("Компьютер выиграл!")
                break
            num += 1

    def start(self):
        self.greet()
        self.loop()


g = Game()
g.start()

