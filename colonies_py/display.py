# -*- coding: utf-8 -*-
import os

import numpy as np

import structure

# ----

rst = '\x1B[0m'

colors = {
    -1: '\x1B[37m',
    0: '\x1B[31m',
    1: '\x1B[32m',
    2: '\x1B[33m',
    3: '\x1B[34m',
    4: '\x1B[35m',
    5: '\x1B[36m'
}


def print_color(text, color=-1):
    color_ = colors.get(color % 6 if color >= 0 else -1)
    print(color_ + text + rst, end='')


def display_screen(X, Y, screen):
    print_color(' ' + '-' * X + '\n')

    for y in range(Y):
        print_color('|')

        for x in range(X):
            num, value = screen[:, x, y]

            if value == 0:
                print_color(' ', num)
            elif value == 1:
                print_color(str(num)[0])
            elif value == 2:
                print_color('#', num)
            elif value == 3:
                print_color('x', num)
            elif value == 4:
                print_color('.', num)

        print_color('|\n')

    print_color(' ' + '-' * X + '\n')


def display(result: structure.result_worlds) -> None:
    os.system('clear')

    winner, X, Y, food_results, colony_results = result

    if winner != -1:
        print_color(f'WINNER: {winner}.\n')

    screen = np.zeros((2, X, Y), dtype=np.int64)

    for col_num, col_x, col_y, amount_of_food, ant_results, phe_results in colony_results:
        print_color(
            f'Col: {col_num}. Foods: {amount_of_food}. Ants: {len(ant_results)}, Phes: {len(phe_results)}\n',
            col_num)

        for phe_num, phe_x, phe_y, phe_lifetime in phe_results:
            screen[:, phe_x, phe_y] = col_num, 4

        for ant_num, ant_x, ant_y, ant_old_x, ant_old_y, ant_has_food, ant_punc in ant_results:
            screen[:, ant_x, ant_y] = col_num, 3

        screen[:, col_x, col_y] = col_num, 2

    for food_num, food_x, food_y, food_amount, food_inside, food_limit in food_results:
        print_color(
            f'Food: {food_num}. Amount: {food_amount}. Ants: {food_inside}. Limit: {food_limit}\n')
        screen[:, food_x, food_y] = food_num, 1

    display_screen(X, Y, screen)


# ----
