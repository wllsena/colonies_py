# -*- coding: utf-8 -*-
from __future__ import annotations

from typing import List, Optional, Tuple, Union

import numpy as np
from numpy.random import choice, normal, randint

# -----

result_food = Tuple[int, int, int, float, int, int]
result_ant = Tuple[int, int, int, int, int, bool, int]
result_pheromone = Tuple[int, int, int]
result_colony = Tuple[int, int, int, int, List[result_ant], List[result_pheromone]]
result_worlds = Tuple[int, int, int, List[result_food], List[result_colony]]


class Food:
    def __init__(
        self,
        num_: int,
        x_: int,
        y_: int,
        amount_: float,
        replacement_: float,
        limit_: int,
    ):

        self.num: int = num_
        self.x: int = x_
        self.y: int = y_
        self.amount: float = amount_
        self.replacement: float = replacement_
        self.limit: int = limit_

        self.amount_max: float = self.amount
        self.inside: int = 0

    def get(self) -> bool:
        if self.inside != self.limit:
            self.amount -= 1
            self.inside += 1

            return True

        return False

    def update(self) -> result_food:
        self.amount = min(self.amount_max, self.amount + self.replacement)

        result = (self.num, self.x, self.y, self.amount, self.inside, self.limit)

        self.inside = 0

        return result


class Pheromone:
    def __init__(
        self,
        num_: int,
        x_: int,
        y_: int,
        from_x_: int,
        from_y_: int,
        lifetime_: int,
    ):

        self.num: int = num_
        self.x: int = x_
        self.y: int = y_
        self.from_x: int = from_x_
        self.from_y: int = from_y_
        self.lifetime: int = lifetime_

    def update(self) -> Optional[result_pheromone]:
        self.lifetime -= 1

        if self.lifetime == 0:
            return None

        result = (self.x, self.y, self.lifetime)

        return result


def not_same_direction(ant: Ant, phe: Pheromone, col: Colony) -> bool:
    dir1_x = phe.x - ant.x > 0
    dir1_y = phe.y - ant.y > 0
    dir2_x = col.x - ant.x > 0
    dir2_y = col.y - ant.y > 0

    not_same = dir1_x != dir2_x or dir1_y != dir2_y

    return not_same


class Ant:
    def __init__(
        self,
        num_: int,
        world_x_: int,
        world_y_: int,
        x_: int,
        y_: int,
        old_x_: int,
        old_y_: int,
        vision_: int,
    ):

        self.num: int = num_
        self.world_x: int = world_x_
        self.world_y: int = world_y_
        self.x: int = x_
        self.y: int = y_
        self.old_x: int = old_x_
        self.old_y: int = old_y_
        self.vision: int = vision_

        self.has_food: bool = False
        self.punctuation: int = 0

    def get_distance(self, goal: Union[Colony, Pheromone, Food]) -> int:
        distance = abs(goal.x - self.x) + abs(goal.y - self.y)

        return distance

    def walk_randomly(self) -> bool:
        directions = []

        if self.x != 0:
            directions.append('left')
        if self.x != self.world_x - 1:
            directions.append('right')
        if self.y != 0:
            directions.append('down')
        if self.y != self.world_y - 1:
            directions.append('up')

        direction = choice(np.array(directions, dtype=np.str_))

        if direction == 'left':
            self.x -= 1
        elif direction == 'right':
            self.x += 1
        elif direction == 'down':
            self.y -= 1
        elif direction == 'up':
            self.y += 1

        return True

    def walk_goal(self, goal: Union[Colony, Pheromone, Food]) -> bool:
        diff_x = goal.x - self.x
        diff_y = goal.y - self.y

        if abs(diff_x) >= abs(diff_y):
            self.x += 1 if diff_x > 0 else -1
        else:
            self.y += 1 if diff_y > 0 else -1

        return True

    def walk_pheromone(self, pheromone: Pheromone) -> bool:
        self.x = pheromone.x
        self.y = pheromone.y

        return True

    def update(
        self,
        colony: Colony,
        pheromones: List[Pheromone],
        foods: List[Food],
    ) -> result_ant:

        if self.has_food:
            if self.get_distance(colony) == 0:
                result = colony.store()
                self.has_food = not result

                if result:
                    self.punctuation += 1

            else:
                self.walk_goal(colony)

        else:
            food_min_distance = (self.vision + 1, None)

            for food in foods:
                if food.amount == 0:
                    continue

                distance = self.get_distance(food)

                if distance == 0:
                    food_min_distance = (0, food)
                    self.has_food = food.get()

                    break

                if distance < food_min_distance[0]:
                    food_min_distance = (distance, food)

            if food_min_distance[1] is None:
                pheromone_min_distance = (self.vision + 1, None)

                for pheromone in pheromones:
                    distance = self.get_distance(pheromone)

                    if distance == 0:
                        pheromone_min_distance = (0, pheromone)
                        self.walk_pheromone(pheromone)

                        break

                    if (not_same_direction(self, pheromone, colony)
                            and distance < pheromone_min_distance[0]):
                        pheromone_min_distance = (distance, pheromone)

                if pheromone_min_distance[1] is None:
                    self.walk_randomly()
                elif pheromone_min_distance[0] != 0:
                    self.walk_goal(pheromone_min_distance[1])

            elif food_min_distance[0] != 0:
                self.walk_goal(food_min_distance[1])

        result = (self.num, self.x, self.y, self.old_x, self.old_y, self.has_food, self.punctuation)

        return result


class Colony:
    def __init__(
        self,
        num_: int,
        world_x_: int,
        world_y_: int,
        x_: int,
        y_: int,
        ph_lifetime_: int,
        n_ants_: int,
        ant_vision_: int,
    ):

        self.num: int = num_
        self.world_x: int = world_x_
        self.world_y: int = world_y_
        self.x: int = x_
        self.y: int = y_
        self.ph_lifetime: int = ph_lifetime_
        self.n_ants: int = n_ants_
        self.ant_vision: int = ant_vision_

        self.amount_of_food = 0
        self.ants = [
            Ant(n, self.world_x, self.world_y, self.x, self.y, self.x, self.y, self.ant_vision)
            for n in range(self.n_ants)
        ]
        self.pheromones = []

    def store(self) -> bool:
        self.amount_of_food += 1

        return True

    def update(
        self,
        foods: List[Food],
    ) -> result_colony:

        ant_results = []

        for ant in self.ants:
            result = ant.update(self, self.pheromones, foods)
            ant_results.append(result)

            if result[5]:
                _, x, y, old_x, old_y, _, _ = result
                pheromone = Pheromone(len(self.pheromones), x, y, old_x, old_y, self.ph_lifetime)

                self.pheromones.append(pheromone)

        pheromone_results = []
        new_pheromenes = []

        for pheromone in self.pheromones:
            result = pheromone.update()

            if result is not None:
                pheromone_results.append(result)
                new_pheromenes.append(pheromone)

        self.pheromones = new_pheromenes

        result = (self.num, self.x, self.y, self.amount_of_food, ant_results, pheromone_results)

        return result


class World:
    def randnormal(self, mult=1) -> int:
        value = normal(self.norm_area, self.norm_area // 2)
        value = min(max(int(value * mult), 1), self.area)

        return value

    def __init__(
        self,
        food_goal_: int = 100,
        x_: Optional[int] = None,
        y_: Optional[int] = None,
        foods_: Optional[List[Food]] = None,
        colonies_: Optional[List[Colony]] = None,
    ):

        self.food_goal = food_goal_

        if x_ is None:
            self.x: int = min(max(int(normal(102, 50)), 2), 202)
        else:
            self.x: int = x_

        if y_ is None:
            self.y: int = min(max(int(normal(27, 12.5)), 2), 52)
        else:
            self.y: int = y_

        self.area = self.x * self.y
        self.norm_area = self.area**0.25

        if foods_ is None:
            self.foods: List[Food] = []

            for num in range(self.randnormal()):
                food = Food(num, randint(self.x), randint(self.y), self.randnormal(1),
                            self.randnormal(0.5), self.randnormal(0.5))
                self.foods.append(food)
        else:
            self.foods: List[Food] = foods_

        if colonies_ is None:
            self.colonies: List[Colony] = []

            for num in range(self.randnormal()):
                colony = Colony(num, self.x, self.y, randint(self.x), randint(self.y),
                                self.randnormal(1), self.randnormal(1), self.randnormal(1))
                self.colonies.append(colony)
        else:
            self.colonies: List[Colony] = colonies_

    def update(self) -> result_worlds:
        food_results = []

        for food in self.foods:
            result = food.update()
            food_results.append(result)

        colony_results = []
        winner = -1

        for colony in self.colonies:
            result = colony.update(self.foods)
            colony_results.append(result)

            if result[3] >= self.food_goal:
                winner = result[0]

        result = (winner, self.x, self.y, food_results, colony_results)

        return result


# ----
