import uuid
from functools import partial

import numpy as np
import pandas as pd
import geopandas as gpd
import mesa
import mesa_geo as mg
import os
from shapely.geometry import Point
import math

from src.agent.group import Locals, Tourists
from src.agent.geo_agents import Walkway
from src.agent.area import Area
from src.space.town import Town
from src.space.road_network import TownWalkway

# 计时器
def get_time(model) -> pd.Timedelta:
    return pd.Timedelta(days=model.day, hours=model.hour, minutes=model.minute)


# 获取处于某种状态的commuter
def get_num_locals_by_status(model, status: str) -> int:
    locales = [
        local for local in model.schedule.agents if local.status == status
    ]
    return len(locales)


def gentrification(model):


    """for home in model.space.homes:
        if len(model.space._locals_pos_map[home.centroid]) < len(model.space._tourists_pos_map[home.centroid]):
            home.gent_ind += len(model.space._tourists_pos_map[home.centroid])"""


    # if model.hour == 23 and model.minute == 30:
    for home in model.space.homes:
        if len(model.space._locals_pos_map[home.centroid]) < len(model.space._tourists_pos_map[home.centroid]):
            if model.day % 7 == 5 or model.day % 7 == 6:
                home.gent_ind += (home.d_tourist * np.random.randint(0, 2) * len(model.space._tourists_pos_map[home.centroid]) / 30) / (model.day + 2)
            else:
                home.gent_ind += (home.d_tourist * np.random.randint(0, 2) * len(model.space._tourists_pos_map[home.centroid])/50) / (model.day + 2)
        elif len(model.space._locals_pos_map[home.centroid]) > len(model.space._tourists_pos_map[home.centroid]):
            if model.day > 0 and 0 < model.hour < 6:
                home.gent_ind -= 0.0002/ (model.day + 2)


def get_total_gent(model) -> float:
    num_gent = 0.0
    for home in model.space.homes:
        num_gent += home.gent_ind
    return num_gent


def get_total_happiness(model) -> float:
    num_happiness_list = []
    for local in model.schedule.agents:
        if isinstance(local, Locals):
            num_happiness_list.append(local.happiness_in_place)
    num_happiness = 0.0
    for happiness_d in num_happiness_list:
        for values in happiness_d.values():
            num_happiness += values
    return num_happiness

def get_gentrimap(model):
    if model.hour == 13 and model.minute == 30:
        csv_filename = 'data/output/gentri.csv'
        if not os.path.exists(csv_filename):
            gentri = []
            for _ in model.space.all_places:
                gentri.append('j')  # gentri.append(home.gent_ind)
            df = pd.DataFrame({'gent_id': gentri})
            df.to_csv(csv_filename, index=False)
        else:
            gentri = []
            for place in model.space.all_places:
                gentri.append(place.gent_ind)
            df2 = pd.DataFrame({'gent_id': gentri})
            existing_data1 = pd.read_csv(csv_filename)
            result1 = pd.concat([existing_data1, df2], axis=1)
            result1.to_csv(csv_filename, index=False)

def get_genmap(model):
    if model.hour == 13 and model.minute == 30:
        csv_filename3 = 'data/output/density_gen.csv'
        if not os.path.exists(csv_filename3):
            genmap = []
            for i in model.area_pos_map:
                genmap.append(model.space._locals_pos_map[i])
            df1 = pd.DataFrame({"pop": genmap})
            df1.to_csv(csv_filename3, index=False)

        else:
            genmap2 = []
            for i in model.area_pos_map:
                local_set = model.space._locals_pos_map[i]
                list_activity = []
                for l in local_set:
                    if l.status == 'activity':
                        list_activity.append(l)
                genmap2.append(len(list_activity) * 10 + np.random.randint(0, 20))
            df2 = pd.DataFrame({"pop": genmap2})
            existing_data1 = pd.read_csv(csv_filename3)
            result1 = pd.concat([existing_data1, df2], axis=1)
            result1.to_csv(csv_filename3, index=False)
    if model.hour == 23 and model.minute == 30:
        csv_filename4 = 'data/output/density_home.csv'
        if not os.path.exists(csv_filename4):
            genmap = []
            for i in model.area_pos_map:
                genmap.append(model.space._locals_pos_map[i])
            df3 = pd.DataFrame({"pop": genmap})
            df3.to_csv(csv_filename4, index=False)
        else:
            genmap2 = []
            for i in model.area_pos_map:
                local_set = model.space._locals_pos_map[i]
                list_activity = []
                for l in local_set:
                    if l.status == 'home':
                        list_activity.append(l)
                genmap2.append(len(list_activity) * 10 + np.random.randint(0, 20))
            df4 = pd.DataFrame({"pop": genmap2})
            existing_data1 = pd.read_csv(csv_filename4)
            result2 = pd.concat([existing_data1, df4], axis=1)
            result2.to_csv(csv_filename4, index=False)


def get_density(model):
    if model.minute == 30:
        csv_filename1 = 'data/output/density_local.csv'
        csv_filename2 = 'data/output/density_tourist.csv'
        if not os.path.exists(csv_filename1):
            densmap = []
            densmapt = []
            for i in model.area_pos_map:
                densmap.append(model.space._locals_pos_map[i])
                densmapt.append(model.space._tourists_pos_map[i])
            df1 = pd.DataFrame({"pop": densmap})
            dft1 = pd.DataFrame({'pop': densmapt})
            df1.to_csv(csv_filename1, index=False)
            dft1.to_csv(csv_filename2, index=False)
        else:
            densmap2 = []
            densmapt2 = []
            for i in model.area_pos_map:
                densmap2.append(len(model.space._locals_pos_map[i]) * 10 + np.random.randint(0, 20))
                densmapt2.append(len(model.space._tourists_pos_map[i])* 10 + np.random.randint(0, 20))
            df2 = pd.DataFrame({"pop": densmap2})
            dft2 = pd.DataFrame({'pop': densmapt2})
            existing_data1 = pd.read_csv(csv_filename1)
            existing_data2 = pd.read_csv(csv_filename2)
            result1 = pd.concat([existing_data1, df2], axis=1)
            result1.to_csv(csv_filename1, index=False)
            result2 = pd.concat([existing_data2, dft2], axis = 1)
            result2.to_csv(csv_filename2, index=False)


class ResilintJinze(mesa.Model):
    running: bool
    schedule: mesa.time.RandomActivation
    show_walkway: bool
    show_lakes_and_rivers: bool
    current_id: int
    space: Town
    walkway: TownWalkway
    world_size: gpd.geodataframe.GeoDataFrame
    got_to_destination: int
    num_locals: int
    num_tourists: int
    day: int
    hour: int
    minute: int
    datacollector: mesa.DataCollector

    def __init__(
        self,
        data_crs: str,
        areas_file: str,
        walkway_file: str,
        num_locals,
        num_tourists,
        local_min_friends=3,
        local_max_friends=8,
        local_happiness_increase=0.7,
        local_happiness_decrease=0.4,
        local_speed=1.0,
        tourist_speed=1.0,
        model_crs="epsg:3857",
        show_walkway=False,
    ) -> None:
        super().__init__()
        self.schedule = mesa.time.RandomActivation(self)
        self.show_walkway = show_walkway
        self.data_crs = data_crs
        self.space = Town(crs=model_crs)
        self.num_locals = num_locals
        self.num_tourists = num_tourists
        Locals.MIN_FRIENDS = local_min_friends
        Locals.MAX_FRIENDS = local_max_friends
        Locals.HAPPINESS_INCREASE = local_happiness_increase
        Locals.HAPPINESS_DECREASE = local_happiness_decrease
        Locals.SPEED = local_speed * 300.0  # meters per tick (5 minutes)
        Tourists.SPEED = tourist_speed * 300.0
        self._load_areas_from_file(areas_file, crs=model_crs)
        self._load_road_vertices_from_file(walkway_file, crs=model_crs)
        self._set_area_entrance()
        self.got_to_destination = 0
        self._create_locals()
        self._create_tourists()
        self.day = 0
        self.hour = 5
        self.minute = 55
        self.datacollector = mesa.DataCollector(
            model_reporters={
                "time": get_time,
                "status_home": partial(get_num_locals_by_status, status="home"),
                "status_activity": partial(get_num_locals_by_status, status="activity"),
                "status_work": partial(get_num_locals_by_status, status="work"),
                "status_traveling": partial(
                    get_num_locals_by_status, status="transport"
                ),
                "happiness": get_total_happiness,
                "gentrification": get_total_gent
                # "friendship_home": partial(get_total_friendships_by_type, friendship_type="home"),
                # "friendship_work": partial(get_total_friendships_by_type, friendship_type="work"),
            }
        )
        self.datacollector.collect(self)

    def _create_locals(self) -> None:
        for _ in range(self.num_locals):
            random_home = self.space.get_random_home()
            random_work = self.space.get_random_work()
            dist = {}
            for act in self.space.activities:
                dist[act.unique_id] = Point(random_home.centroid).distance(Point(act.centroid))
            sorted_dist = sorted(dist.items(), key=lambda kv: kv[1])
            top_4_activity = sorted_dist[:4]
            random_activity_id = [pair[0] for pair in top_4_activity]
            random_activity = [self.space.get_area_by_id(i) for i in random_activity_id]
            local = Locals(
                unique_id=uuid.uuid4().int,
                model=self,
                geometry=Point(random_home.centroid),
                crs=self.space.crs,
            )
            local.set_home(random_home)
            local.set_work(random_work)
            for random_act in random_activity:
                local.set_activity(random_act)
            local.status = "home"
            self.space.add_locals(local)
            self.schedule.add(local)

    def _create_tourists(self) -> None:
        for _ in range(self.num_tourists):
            random_home = self.space.get_random_tour_home()
            random_activity = [self.space.get_random_place() for _ in range(8)]
            tourist = Tourists(
                unique_id=uuid.uuid4().int,
                model=self,
                geometry=Point(random_home.centroid),
                crs=self.space.crs,
            )
            tourist.set_home(random_home)
            for random_act in random_activity:
                tourist.set_activity(random_act)
            tourist.status = "home"
            self.space.add_tourists(tourist)
            self.schedule.add(tourist)

    def _load_areas_from_file(
        self, areas_file: str, crs: str
    ) -> None:
        areas_df = gpd.read_file(areas_file)
        areas_df.drop("Id", axis=1, inplace=True)
        areas_df.index.name = "unique_id"
        areas_df = areas_df.set_crs(self.data_crs, allow_override=True).to_crs(
            crs
        )
        areas_df["centroid"] = [
            (x, y) for x, y in zip(areas_df.centroid.x, areas_df.centroid.y)
        ]
        areas_df.rename(columns={"class": "function"}, inplace=True)
        area_creator = mg.AgentCreator(Area, model=self)
        areas = area_creator.from_GeoDataFrame(areas_df)
        self.space.add_areas(areas)
        self.area_pos_map = areas_df['centroid'].tolist()

    def _load_road_vertices_from_file(
        self, walkway_file: str, crs: str
    ) -> None:
        walkway_df = (
            gpd.read_file(walkway_file)
            .set_crs(self.data_crs, allow_override=True)
            .to_crs(crs)
        )
        self.walkway = TownWalkway(lines=walkway_df["geometry"])
        if self.show_walkway:
            walkway_creator = mg.AgentCreator(Walkway, model=self)
            walkway = walkway_creator.from_GeoDataFrame(walkway_df)
            self.space.add_agents(walkway)

    def _set_area_entrance(self) -> None:
        for area in (
            *self.space.homes,
            *self.space.activities,
            *self.space.other_areas,
            *self.space.work_places
        ):
            area.entrance_pos = self.walkway.get_nearest_node(area.centroid)

    def step(self) -> None:
        self.__update_clock()
        self.schedule.step()
        gentrification(self)
        self.datacollector.collect(self)
        get_density(self)
        get_genmap(self)
        get_gentrimap(self)

    def __update_clock(self) -> None:
        self.minute += 5
        if self.minute == 60:
            if self.hour == 23:
                self.hour = 0
                self.day += 1
            else:
                self.hour += 1
            self.minute = 0
