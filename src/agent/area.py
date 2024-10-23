from __future__ import annotations
import uuid
from random import randrange
import geopandas as gpd
import pyproj
import mesa
import mesa_geo as mg
from shapely.geometry import Polygon


class Area(mg.GeoAgent):
    unique_id: int  # 代理功能区id
    model: mesa.Model
    geometry: Polygon
    crs: pyproj.CRS  # 参考系
    centroid: mesa.space.FloatCoordinate  # 浮点坐标作为中心点
    name: str
    gent_ind: float  # 人风险指标！！！！！！！！！！！！！！！！！！！！！！！路径与功能概率
    isol_ind: float  # 商业风险指标！！！！！！！！！！！！！！！！！！！！！！
    function: int  # 有待刁提供
    Tourist_sp: int
    inh_weight: float
    work_weight: float
    d_tourist: float
    entrance_pos: mesa.space.FloatCoordinate  # 最近的道路节点

    def __init__(self, unique_id, model, geometry, crs) -> None:
        super().__init__(unique_id=unique_id, model=model, geometry=geometry, crs=crs)
        areas_df = gpd.read_file('data/raw/jz/jz_bld.shp')
        areas_df.index.name = "jack"
        self.entrance = None  # 初始化入口
        self.name = str(uuid.uuid4())  # 随机起名
        self.function = areas_df.loc[unique_id, "class"]
        self.Tourist_sp = areas_df.loc[unique_id, "Tourist_sp"]
        self.d_tourist = areas_df.loc[unique_id, "d_tourist"]
        self.inh_weight = areas_df.loc[unique_id, 'weight']
        self.work_weight = areas_df.loc[unique_id, 'work']
        self.gent_ind = 0.0
        self.isol_ind = 0.0

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}(unique_id={self.unique_id}, name={self.name}, function={self.function}, "
            f"centroid={self.centroid})"
        )

    def __eq__(self, other):
        if isinstance(other, Area):
            return self.unique_id == other.unique_id
        return False

    def __hash__(self):
        # Use unique_id for hashing since it uniquely identifies the Area object
        return hash(self.unique_id)


