from __future__ import annotations

import random
from typing import List, Dict
import pyproj
import numpy as np
import mesa
import mesa_geo as mg
from shapely.geometry import Point, LineString

from src.agent.area import Area
from src.space.utils import redistribute_vertices, UnitTransformer


class Locals(mg.GeoAgent):
    unique_id: int  # locals_id, used to link locals and nodes
    model: mesa.Model
    geometry: Point
    crs: pyproj.CRS
    origin: Area
    destination: Area
    employee: str
    my_path: List[
        mesa.space.FloatCoordinate
    ]
    step_in_path: int  # the number of step taking in the walk
    my_home: Area
    my_interest: List[Area]
    my_work: Area
    start_time_h: int  # time to start going to work, hour and minute
    start_time_m: int
    work_time : int
    change_time_h: int  # time to change to another place
    change_time_m: int
    my_g: List[Area]
    end_time_h: int  # time to leave act, hour and minute
    end_time_m: int
    # friends_id: List[int]  # set of friends at activity!!!
    status: str  # activity, home, or transport
    testing: bool  # detect fri
    happiness_in_place: Dict[int: float]
    happiness_in_home: float
    nz: int
    tolerance: float
    MIN_FRIENDS: int
    MAX_FRIENDS: int
    HAPPINESS_INCREASE: float
    HAPPINESS_DECREASE: float
    SPEED: float
    CHANCE_NEW_FRIEND: float

    def __init__(self, unique_id, model, geometry, crs) -> None:
        super().__init__(unique_id, model, geometry, crs)
        self.my_home = None
        self.my_interest = []
        self.my_work = None
        self.my_g = []
        self.start_time_h = round(np.random.normal(9, 1))
        while self.start_time_h < 7 or self.start_time_h > 11:
            self.start_time_h = round(np.random.normal(9, 1))
        self.start_time_m = np.random.randint(0, 12) * 5
        self.end_time_h = np.random.randint(self.start_time_h, 14)  # 10点前回家
        self.change_time_h = 0
        self.work_time = np.random.randint(6, 8)
        self.change_time_m = np.random.randint(0, 12) * 5
        self.end_time_m = np.random.randint(0, 12) * 5
        self.happiness_in_place = {}
        self.happiness_in_home = 100.0
        self.employee = random.choices(['work', 'unwork'], weights=[1, 1], k=1)[0]
        self.nz = 0
        random_number = np.random.normal(loc=0.33, scale=1.0 / 6.0)
        if random_number < 0.0:
            random_number = 0.0
        elif random_number > 1.0:
            random_number = 1.0
        self.tolerance = random_number
        # self.friends_id = []
        self.testing = False

    def __repr__(self) -> str:
        return (
            f"Commuter(unique_id={self.unique_id}, geometry={self.geometry}, status={self.status}, "
            # f"num_friends={len(self.friends_id)})"
        )  # return

    @property
    def num_neighbors(self) -> int:
        return self.model.space.home_counter[self.my_home.centroid]  # home counter in town

    # @property
    # def num_friends(self) -> int:
        # return len(self.friends_id)

    def set_home(self, new_home: Area) -> None:
        old_home_pos = self.my_home.centroid if self.my_home else None
        self.my_home = new_home
        self.model.space.update_home_counter(
            old_home_pos=old_home_pos, new_home_pos=self.my_home.centroid
        )

    def set_work(self, work: Area) -> None:
        self.my_work = work

    def del_activity(self, old_activity: Area) -> None:
        self.my_interest.remove(old_activity)
        del self.happiness_in_place[old_activity.unique_id]

    def set_activity(self, new_activity: Area) -> None:
        if new_activity is not None:
            self.my_interest.append(new_activity)
            self.happiness_in_place[new_activity.unique_id] = 100.0

    def step(self) -> None:
        self.check_work()
        self._check_happiness()
        self._prepare_to_move()
        self._move()
        # self._make_friends_at_work()

    def _check_happiness(self) -> None:
        if self.status == "activity":
            place = self.model.space.get_area_by_pos((self.geometry.x, self.geometry.y))
            place_id = place.unique_id
            locals_together = [
                c
                for c in self.model.space.get_locals_by_pos(
                    (self.geometry.x, self.geometry.y)
                )
            ]
            if len(locals_together) > self.MAX_FRIENDS:
                if place_id in self.happiness_in_place:
                    self.happiness_in_place[place_id] -= self.HAPPINESS_DECREASE * (
                            len(locals_together) - self.MAX_FRIENDS
                    )
            else:
                if len(locals_together) < self.MIN_FRIENDS:
                    if place_id in self.happiness_in_place:
                        self.happiness_in_place[place_id] -= self.HAPPINESS_DECREASE * (
                            self.MIN_FRIENDS - len(locals_together)
                        )
                else:
                    if place_id in self.happiness_in_place:
                        self.happiness_in_place[place_id] += self.HAPPINESS_INCREASE
            if place_id in self.happiness_in_place:
                if self.happiness_in_place[place_id] < 0.0:
                    self.my_interest.remove(place)
                    del self.happiness_in_place[place_id]
                    self._relocate_activity()
        if self.status == "home":
            if self.model.minute == 30:
                random_relo = np.random.random()
                if random_relo < self.my_home.gent_ind:
                    self._relocate_home()


    def check_work(self):
        if self.model.hour == 0 and self.model.minute == 30:
            if self.model.day % 7 == 5 or self.model.day % 7 == 6:
                self.employee = 'unwork'
            else:
                self.employee = self.employee = random.choices(['work', 'unwork'], weights=[1, 1], k=1)[0]

    def _prepare_to_move(self) -> None:
        # start going to activity
        if self.employee == 'unwork':
            if (
                self.status == "home"
                and (self.model.hour == self.start_time_h)
                and self.model.minute == self.start_time_m
            ):
                self.origin = self.model.space.get_area_by_id(self.my_home.unique_id)
                self.model.space.move_locals(self, pos=self.origin.centroid)
                self.destination = self.model.space.get_area_by_id(
                    self.my_interest[0].unique_id
                )
                self.change_time_h = self.start_time_h + 2
                self._path_select()
                self.status = "transport"
            # start going home
            elif (
                self.status != "home"
                and (self.model.hour == self.end_time_h or self.model.hour == self.end_time_h + 5)
                and self.model.minute == self.end_time_m
            ):
                if self.status == "activity":
                    self.origin = self.model.space.get_area_by_pos((self.geometry.x, self.geometry.y))
                else:
                    self.origin = self.destination
                self.model.space.move_locals(self, pos=self.origin.centroid)
                self.destination = self.model.space.get_area_by_id(
                    self.my_home.unique_id
                )
                self._path_select()
                self.status = "transport"
        elif self.employee == 'work':
            if(
                self.status == 'home'
                and self.model.hour == self.work_time
                and self.model.minute == self.start_time_m
            ):
                self.origin = self.model.space.get_area_by_id(self.my_home.unique_id)
                self.model.space.move_locals(self, pos=self.origin.centroid)
                self.destination = self.model.space.get_area_by_id(
                    self.my_work.unique_id
                )
                self._path_select()
                self.status = "transport"
                self.start_time_h = round(np.random.normal(9, 1))
            elif(
                self.status == 'work'
                and self.model.hour == self.work_time + 8
                and self.model.minute == self.end_time_m
            ):
                self.origin = self.model.space.get_area_by_id(self.my_home.unique_id)
                self.model.space.move_locals(self, pos=self.origin.centroid)
                self.destination = self.model.space.get_area_by_id(
                    self.my_home.unique_id
                )
                self._path_select()
                self.status = "transport"

        """elif (
            # self.status == "activity"
            self.model.hour == self.change_time_h
            and self.model.minute == self.change_time_m
            and self.change_time_h < self.end_time_h
        ):
            self.my_g = self.my_interest
            self.my_g.append(self.my_home)
            jnan = np.random.randint(0, 4)
            self.origin = self.model.space.get_area_by_pos((self.geometry.x, self.geometry.y))
            self.model.space.move_locals(self, pos=self.origin.centroid)
            self.destination = self.model.space.get_area_by_id(self.my_g[jnan].unique_id)
            self._path_select()
            self.nz += 1
            if self.nz >= 2:
                self.nz = 2
            self.status = "transport"
            self.change_time_h += 1
            """

    def _move(self) -> None:
        if self.status == "transport":
            if self.step_in_path < len(self.my_path):
                next_position = self.my_path[self.step_in_path]
                self.model.space.move_locals(self, next_position)
                self.step_in_path += 1
            else:
                self.model.space.move_locals(self, self.destination.centroid)
                if self.employee == 'unwork':
                    if self.destination in self.my_interest:
                        self.status = "activity"
                    # elif self.destination == self.my_home and self.model.hour < self.end_time_h:
                        # self.status = "activity"
                    elif self.destination == self.my_home: # and self.model.hour >= self.end_time_h:
                        self.status = "home"
                elif self.employee == 'work':
                    if self.destination == self.my_work:
                        self.status = 'work'
                    elif self.destination == self.my_home:
                        self.status = 'home'
                self.model.got_to_destination += 1

    def advance(self) -> None:
        raise NotImplementedError

    def _relocate_home(self) -> None:
        while (new_home := self.model.space.get_random_home()) == self.my_home:
            continue
        self.set_home(new_home)

    def _relocate_activity(self) -> None:
        while (new_activity := self.model.space.get_random_activity()) in self.my_interest:
            continue
        self.set_activity(new_activity)

    def _path_select(self) -> None:
        self.step_in_path = 0
        if (
            cached_path := self.model.walkway.get_cached_path(
                source=self.origin.entrance_pos, target=self.destination.entrance_pos
            )
        ) is not None:
            self.my_path = cached_path
        else:
            self.my_path = self.model.walkway.get_shortest_path(
                source=self.origin.entrance_pos, target=self.destination.entrance_pos
            )
            self.model.walkway.cache_path(
                source=self.origin.entrance_pos,
                target=self.destination.entrance_pos,
                path=self.my_path,
            )
        self._redistribute_path_vertices()

    def _redistribute_path_vertices(self) -> None:
        # if origin and destination share the same entrance, then self.my_path will contain only this entrance node,
        # and len(self.path) == 1. There is no need to redistribute path vertices.
        if len(self.my_path) > 1:
            unit_transformer = UnitTransformer(degree_crs=self.model.walkway.crs)
            original_path = LineString([Point(p) for p in self.my_path])
            # from degree unit to meter
            path_in_meters = unit_transformer.degree2meter(original_path)
            redistributed_path_in_meters = redistribute_vertices(
                path_in_meters, self.SPEED
            )
            # meter back to degree
            redistributed_path_in_degree = unit_transformer.meter2degree(
                redistributed_path_in_meters
            )
            self.my_path = list(redistributed_path_in_degree.coords)


class Tourists(mg.GeoAgent):
    unique_id: int  # locals_id, used to link locals and nodes
    model: mesa.Model
    geometry: Point
    crs: pyproj.CRS  # 参考坐标系
    origin: Area  # 开始
    destination: Area  # 目标
    my_path: List[
        mesa.space.FloatCoordinate
    ]  # 寻路的坐标序列
    step_in_path: int  # the number of step taking in the walk
    my_home: Area
    my_interest: List[Area]  # !!!
    start_time_h: int  # time to start going to work, hour and minute
    start_time_m: int
    change_time_h: int  # time to change to another place
    change_time_m: int
    end_time_h: int  # time to leave act, hour and minute
    end_time_m: int
    friends_id: List[int]  # set of friends at activity!!!
    status: str  # activity or transport
    testing: bool  # 检测朋友
    tolerance: float  # 异常容忍度
    SPEED: float
    i: int

    def __init__(self, unique_id, model, geometry, crs) -> None:
        super().__init__(unique_id, model, geometry, crs)
        self.my_home = None
        self.my_interest = []
        self.start_time_h = np.random.randint(8, 16)
        self.start_time_m = np.random.randint(0, 12) * 5
        self.end_time_h = np.random.randint(self.start_time_h, 20)  # 10点前回家
        self.change_time_h = self.start_time_h + 1
        self.change_time_m = np.random.randint(0, 12) * 5
        self.end_time_m = np.random.randint(0, 12) * 5
        self.friends_id = []
        self.i = 0
        random_number = np.random.normal(loc=0.33, scale=1.0 / 6.0)
        if random_number < 0.0:
            random_number = 0.0
        elif random_number > 1.0:
            random_number = 1.0
        self.tolerance = random_number  # 以0.33 为中心的正态分布
        # self.friends_id = []
        self.testing = False

    def __repr__(self) -> str:
        return (
            f"Tourists(unique_id={self.unique_id}, geometry={self.geometry}, status={self.status}, "
            # f"num_friends={len(self.friends_id)})"
        )  # 返回一个包含上述属性值的字符串

    @property
    def num_friends(self) -> int:
        return len(self.friends_id)

    def set_home(self, new_home: Area) -> None:
        # old_home_pos = self.my_home.centroid if self.my_home else None
        self.my_home = new_home
        # self.model.space.update_home_counter(
            # old_home_pos=old_home_pos, new_home_pos=self.my_home.centroid
        # )

    def del_activity(self, old_activity: Area) -> None:
        self.my_interest.remove(old_activity)

    def set_activity(self, new_activity: Area) -> None:
        if new_activity is not None:
            self.my_interest.append(new_activity)

    def step(self) -> None:
        self._prepare_to_move()
        self._move()
        # self._make_friends_at_work()

    def _prepare_to_move(self) -> None:
        # start going to activity
        if self.model.hour == 23:
            self.i = 0
            self.change_time_h = self.start_time_h + 1
        if (
            self.status == "home"
            and (self.model.hour == self.start_time_h)
            and self.model.minute == self.start_time_m
        ):
            self.origin = self.model.space.get_area_by_id(self.my_home.unique_id)
            self.model.space.move_tourists(self, pos=self.origin.centroid)
            self.destination = self.model.space.get_area_by_id(
                self.my_interest[0].unique_id
            )
            self.change_time_h = self.start_time_h + 2
            self._path_select()
            self.status = "transport"
        # start going home
        elif (
            self.status != "home"
            and self.model.hour == self.change_time_h
            and self.model.minute == self.change_time_m
        ):
            self.i += 1
            if self.i > 8:
                self.i = 0
            if self.status == "activity":
                self.origin = self.model.space.get_area_by_pos((self.geometry.x, self.geometry.y))
            self.model.space.move_tourists(self, pos=self.origin.centroid)
            self.destination = self.model.space.get_area_by_id(
                self.my_interest[self.i].unique_id
            )
            self._path_select()
            self.change_time_h += np.random.randint(0, 1)
            self.change_time_m = np.random.randint(0, 12) * 5
            self.status = "transport"
        elif (
            self.status != "home"
            and self.model.hour == self.end_time_h
            and self.model.minute == self.end_time_m
        ):
            if self.status == "activity":
                self.origin = self.model.space.get_area_by_pos((self.geometry.x, self.geometry.y))
            else:
                self.origin = self.destination
            self.model.space.move_tourists(self, pos=self.origin.centroid)
            self.destination = self.model.space.get_area_by_id(
                self.my_home.unique_id
            )
            self._path_select()
            self.status = "transport"

    def _move(self) -> None:
        if self.status == "transport":
            if self.step_in_path < len(self.my_path):
                next_position = self.my_path[self.step_in_path]
                self.model.space.move_tourists(self, next_position)
                self.step_in_path += 1
            else:
                self.model.space.move_tourists(self, self.destination.centroid)
                if self.destination in self.my_interest:
                    self.status = "activity"
                # elif self.destination == self.my_home and self.model.hour < self.end_time_h:
                    # self.status = "activity"
                elif self.destination == self.my_home: # and self.model.hour >= self.end_time_h:
                    self.status = "home"

    def advance(self) -> None:
        raise NotImplementedError

    def _relocate_home(self) -> None:
        while (new_home := self.model.space.get_random_home()) == self.my_home:
            continue
        self.set_home(new_home)

    def _relocate_activity(self) -> None:
        while (new_activity := self.model.space.get_random_activity()) in self.my_interest:
            continue
        self.set_activity(new_activity)

    def _path_select(self) -> None:
        self.step_in_path = 0
        if (
            cached_path := self.model.walkway.get_cached_path(
                source=self.origin.entrance_pos, target=self.destination.entrance_pos
            )
        ) is not None:
            self.my_path = cached_path
        else:
            self.my_path = self.model.walkway.get_shortest_path(
                source=self.origin.entrance_pos, target=self.destination.entrance_pos
            )
            self.model.walkway.cache_path(
                source=self.origin.entrance_pos,
                target=self.destination.entrance_pos,
                path=self.my_path,
            )
        self._redistribute_path_vertices()

    def _redistribute_path_vertices(self) -> None:
        # if origin and destination share the same entrance, then self.my_path will contain only this entrance node,
        # and len(self.path) == 1. There is no need to redistribute path vertices.
        if len(self.my_path) > 1:
            unit_transformer = UnitTransformer(degree_crs=self.model.walkway.crs)
            original_path = LineString([Point(p) for p in self.my_path])
            # from degree unit to meter
            path_in_meters = unit_transformer.degree2meter(original_path)
            redistributed_path_in_meters = redistribute_vertices(
                path_in_meters, self.SPEED
            )
            # meter back to degree
            redistributed_path_in_degree = unit_transformer.meter2degree(
                redistributed_path_in_meters
            )
            self.my_path = list(redistributed_path_in_degree.coords)


class Huawei(mg.GeoAgent):
    unique_id: int  # locals_id, used to link locals and nodes
    model: mesa.Model
    geometry: Point
    crs: pyproj.CRS  # 参考坐标系

    def __init__(self, unique_id, model, geometry, crs) -> None:
        super().__init__(unique_id, model, geometry, crs)