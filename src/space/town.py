import random
from collections import defaultdict
from typing import Dict, Tuple, Optional, DefaultDict, Set

import mesa
import mesa_geo as mg
from shapely.geometry import Point

from src.agent.group import Locals, Tourists, Huawei
from src.agent.area import Area


class Town(mg.GeoSpace):
    all_places: Tuple[Area]
    homes: Tuple[Area]
    tour_homes: Tuple[Area]
    activities: Tuple[Area]
    other_areas: Tuple[Area]
    work_places: Tuple[Area]
    home_counter: DefaultDict[mesa.space.FloatCoordinate, int]
    _areas: Dict[int, Area]
    _locals_pos_map: DefaultDict[mesa.space.FloatCoordinate, Set[Locals]]
    _tourists_pos_map: DefaultDict[mesa.space.FloatCoordinate, Set[Tourists]]
    _areas_pos_map: DefaultDict[mesa.space.FloatCoordinate, Area]
    _locals_id_map: Dict[int, Locals]
    _tourists_id_map: Dict[int, Tourists]

    def __init__(self, crs: str) -> None:
        super().__init__(crs=crs)
        self.homes = tuple()
        self.all_places = tuple()
        self.tour_homes = tuple()
        self.activities = tuple()
        self.other_areas = tuple()
        self.work_places = tuple()
        self.home_counter = defaultdict(int)
        self._areas = dict()
        self._areas_pos_map = defaultdict(Area)
        self._locals_pos_map = defaultdict(set)
        self._tourists_pos_map = defaultdict(set)
        self._locals_id_map = dict()
        self._tourists_id_map = dict()

    def get_random_home(self) -> Area:
        areas = self.homes
        weights = [area.inh_weight for area in areas]
        return random.choices(areas, weights=weights, k=1)[0]
        # 基于权重的出生点

    def get_random_work(self) -> Area:
        areas = self.work_places
        weights = [area.work_weight for area in areas]
        return random.choices(areas, weights=weights, k=1)[0]

    def get_random_tour_home(self) -> Area:
        return random.choice(self.tour_homes)

    def get_random_place(self) -> Area:
        sum_d_tourist = 0.0
        list_d_tourist =[]
        for place in self.all_places:
            sum_d_tourist += place.d_tourist
            list_d_tourist.append(place.d_tourist)
        weights = [value / sum_d_tourist for value in list_d_tourist]
        return random.choices(self.all_places, weights=weights, k=1)[0]

    def get_random_activity(self) -> Area:
        return random.choice(self.activities)

    def get_area_by_id(self, unique_id: int) -> Area:
        return self._areas[unique_id]

    def add_areas(self, agents) -> None:
        super().add_agents(agents)
        homes, activities, other_areas, tour_homes, all_places, work_places = [], [], [], [], [], []
        for agent in agents:
            self._areas_pos_map[agent.centroid] = agent
            if isinstance(agent, Area):
                all_places.append(agent)
                self._areas[agent.unique_id] = agent
                if agent.work_weight != 0:
                    work_places.append(agent)
                if agent.function == 10:
                    other_areas.append(agent)
                elif agent.function == 4 or agent.function == 5 or agent.function == 6 or agent.function == 7 or agent.function == 8 or agent.function == 9:
                    activities.append(agent)
                elif agent.function == 1 or agent.function == 2:
                    homes.append(agent)
        for agent in agents:
            if isinstance(agent, Area):
                if agent.Tourist_sp == 1:
                    tour_homes.append(agent)
        self.work_places = self.work_places + tuple(work_places)
        self.other_areas = self.other_areas + tuple(other_areas)
        self.all_places = self.all_places + tuple(all_places)
        self.activities = self.activities + tuple(activities)
        self.homes = self.homes + tuple(homes)
        self.tour_homes = self.tour_homes + tuple(tour_homes)

    def get_area_by_pos(self, float_pos: mesa.space.FloatCoordinate):
        return self._areas_pos_map[float_pos]

    def get_locals_by_pos(
        self, float_pos: mesa.space.FloatCoordinate
    ) -> Set[Locals]:
        return self._locals_pos_map[float_pos]

    def get_locals_by_id(self, locals_id: int) -> Locals:
        return self._locals_id_map[locals_id]

    def add_locals(self, agent: Locals) -> None:
        super().add_agents([agent])
        self._locals_pos_map[(agent.geometry.x, agent.geometry.y)].add(agent)
        self._locals_id_map[agent.unique_id] = agent

    def add_tourists(self, agent: Tourists) -> None:
        super().add_agents([agent])
        self._tourists_pos_map[(agent.geometry.x, agent.geometry.y)].add(agent)
        self._tourists_id_map[agent.unique_id] = agent

    def update_home_counter(
        self,
        old_home_pos: Optional[mesa.space.FloatCoordinate],
        new_home_pos: mesa.space.FloatCoordinate,
    ) -> None:
        if old_home_pos is not None:
            self.home_counter[old_home_pos] -= 1
        self.home_counter[new_home_pos] += 1

    def move_locals(
        self, local: Locals, pos: mesa.space.FloatCoordinate
    ) -> None:
        self.__remove_locals(local)
        local.geometry = Point(pos)
        self.add_locals(local)

    def move_tourists(
        self, tourist: Tourists, pos: mesa.space.FloatCoordinate
    ) -> None:
        self.__remove_tourists(tourist)
        tourist.geometry = Point(pos)
        self.add_tourists(tourist)

    def __remove_locals(self, local: Locals) -> None:
        super().remove_agent(local)
        del self._locals_id_map[local.unique_id]
        self._locals_pos_map[(local.geometry.x, local.geometry.y)].remove(
            local
        )

    def __remove_tourists(self, tourist: Tourists) -> None:
        super().remove_agent(tourist)
        del self._tourists_id_map[tourist.unique_id]
        self._tourists_pos_map[(tourist.geometry.x, tourist.geometry.y)].remove(
            tourist
        )
