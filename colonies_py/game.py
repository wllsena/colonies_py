# -*- coding: utf-8 -*-

from time import sleep

from display import display
from structure import World
from tasks import task_manager

# -----

if __name__ == '__main__':
    world = World(100)

    while True:
        result = world.update()
        display(result)
        sleep(0.5)
        task_manager.delay(result)

        if result[1] != -1:
            break

# -----
