from kivy.metrics import sp
from kivy.app import App
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy import properties as kp
from collections import defaultdict
from kivy.animation import Animation
from random import randint

SPRITE_SIZE = sp(28)
COLS = int(Window. width / SPRITE_SIZE)
ROWS = int(Window.height / SPRITE_SIZE)


LENGTH = 4
MOVESPEED = .1

ALPHA = .5


LEFT = 'left'
UP = 'up'
RIGHT = 'right'
DOWN = 'down'


direction_values = {LEFT: [-1, 0],
                    UP: [0,1],
                    RIGHT: [1, 0],
                    DOWN: [0, -1]}

direction_group = {LEFT: 'horizontal',
                   UP: 'vertical',
                   RIGHT: 'horizontal',
                   DOWN: 'vertical'}

direction_keys = {'a': LEFT,
                  'w': UP,
                  'd': RIGHT,
                  's': DOWN,
                  26: UP,  # w on windows
                  4: LEFT,  # a on windows
                  7: RIGHT,  # d on windows
                  22: DOWN  # s on windows
                 }


class Sprite(Widget):
    coord = kp.ListProperty([0, 0])
    bgcolor = kp.ListProperty([0, 0, 0, 0])


SPRITES = defaultdict(lambda: Sprite())


class Fruit(Sprite):
    pass


class Snake(App):
    sprite_size = kp.NumericProperty(SPRITE_SIZE)

    head = kp.ListProperty([0, 0])
    snake = kp.ListProperty()
    length = kp.NumericProperty(LENGTH)

    fruit = kp.ListProperty([0, 0])
    fruit_sprite = kp.ObjectProperty(Fruit)

    direction = kp.StringProperty(RIGHT, options=(LEFT, UP, RIGHT, DOWN))
    buffer_direction = kp.StringProperty(RIGHT, options=(LEFT, UP, RIGHT, DOWN, ''))
    block_input = kp.BooleanProperty(False)

    alpha = kp.NumericProperty(0)

    def on_start(self):
        self.fruit_sprite = Fruit()
        self.fruit = self.new_fruit_location
        self.head = self.new_head_location
        Clock.schedule_interval(self.move, MOVESPEED)
        Window.bind(on_keyboard=self.key_handler)

    def on_fruit(self, *args):
        self.fruit_sprite.coord = self.fruit
        if not self.fruit_sprite.parent:
            self.root.add_widget(self.fruit_sprite)

    def key_handler(self, _, __, key, *____):
        try:
            self.try_change_direction(direction_keys[key])
        except KeyError:
            pass

    def try_change_direction(self, new_direction):
        if direction_group[new_direction] != direction_group[self.direction]:
            if self.block_input:
                self.buffer_direction = new_direction
            else:
                self.direction = new_direction
                self.block_input = True

    def on_head(self, *args):
        self.snake = self.snake[-self.length:]+[self.head]

    def on_snake(self, *args):
        for index, coord in enumerate(self.snake):
            sprite = SPRITES[index]
            sprite.coord = coord
            if not sprite.parent:
                self.root.add_widget(sprite)

    @property
    def new_head_location(self):
        return [randint(2, dim - 2)for dim in[COLS, ROWS]]

    @property
    def new_fruit_location(self):
        while True:
            fruit = [randint(2, dim)for dim in[COLS, ROWS]]
            if fruit not in self.snake and fruit != self.fruit:
                return fruit

    def move(self, *args):
        self.block_input = False
        new_head = [sum(x) for x in zip(self.head, direction_values[self.direction])]
        if not self.check_in_bounds(new_head) or new_head in self.snake:
            return self.die()
        if new_head == self.fruit:
            self.length += 1
            self.fruit = self.new_fruit_location
        if self.buffer_direction:
            self.try_change_direction(self.buffer_direction)
            self.buffer_direction = ''
        self.head = new_head

    def check_in_bounds(self, pos):
        return all(0 <= pos[x] < dim for x, dim in enumerate([COLS, ROWS]))

    def die(self):
        self.root.clear_widgets()
        self.alpha = ALPHA
        Animation(alpha=0, duration=MOVESPEED).start(self)

        self.snake.clear()
        self.length = LENGTH
        self.fruit = self.new_fruit_location
        self.head = self.new_head_location

if __name__ == '__main__':
    Snake().run()
