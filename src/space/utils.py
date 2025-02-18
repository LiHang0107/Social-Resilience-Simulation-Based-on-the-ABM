from typing import Tuple, List
import geopandas as gpd
import numpy as np
import pyproj
import mesa
from shapely.geometry import LineString, MultiLineString
from shapely.ops import transform


"""一些地理空间处理的基础内容，可以不用改直接用"""


def get_coord_matrix(
    x_min: float, x_max: float, y_min: float, y_max: float
) -> np.ndarray:
    """确定坐标最大范围"""
    return np.array(
        [
            [x_min, y_min, 1.0],
            [x_min, y_max, 1.0],
            [x_max, y_min, 1.0],
            [x_max, y_max, 1.0],
        ]
    )


def get_affine_transform(
    from_coord: np.ndarray, to_coord: np.ndarray
) -> Tuple[float, float, float, float, float, float]:
    A, res, rank, s = np.linalg.lstsq(from_coord, to_coord, rcond=None)

    np.testing.assert_array_almost_equal(res, np.zeros_like(res), decimal=15)
    np.testing.assert_array_almost_equal(A[:, 2], np.array([0.0, 0.0, 1.0]), decimal=15)

    # A.T = [[a, b, x_off],
    #        [d, e, y_off],
    #        [0, 0,  1  ]]
    # affine transform = [a, b, d, e, x_off, y_off]
    # For details, refer to https://geopandas.org/en/stable/docs/reference/api/geopandas.GeoSeries.affine_transform.html
    return A.T[0, 0], A.T[0, 1], A.T[1, 0], A.T[1, 1], A.T[0, 2], A.T[1, 2]
# 返回仿射变换矩阵


def get_rounded_coordinate(
    float_coordinate: mesa.space.FloatCoordinate,
) -> mesa.space.Coordinate:
    return round(float_coordinate[0]), round(float_coordinate[1])
# 返回整数的坐标


def segmented(lines: gpd.GeoSeries) -> gpd.GeoSeries:
    def _segmented(linestring: LineString) -> List[LineString]:
        return [
            LineString((start_node, end_node))
            for start_node, end_node in zip(
                linestring.coords[:-1], linestring.coords[1:]
            )
            if start_node != end_node
        ]
    return gpd.GeoSeries([segment for line in lines for segment in _segmented(line)])
# 用来分割多段线为单独的线


# reference: https://gis.stackexchange.com/questions/367228/using-shapely-interpolate-to-evenly-re-sample-points-on-a-linestring-geodatafram
def redistribute_vertices(geom, distance):
    if isinstance(geom, LineString):
        if (num_vert := int(round(geom.length / distance))) == 0:
            num_vert = 1
        return LineString(
            [
                geom.interpolate(float(n) / num_vert, normalized=True)
                for n in range(num_vert + 1)
            ]
        )
    elif isinstance(geom, MultiLineString):
        parts = [redistribute_vertices(part, distance) for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise TypeError(
            f"Wrong type: {type(geom)}. Must be LineString or MultiLineString."
        )
# 重新分布或重新采样线上的顶点，使得顶点间的距离尽量保持为给定的 distance


# 度米坐标转换
class UnitTransformer:
    _degree2meter: pyproj.Transformer
    _meter2degree: pyproj.Transformer

    def __init__(
        self, degree_crs=pyproj.CRS("EPSG:4326"), meter_crs=pyproj.CRS("EPSG:3857")
    ):
        self._degree2meter = pyproj.Transformer.from_crs(
            degree_crs, meter_crs, always_xy=True
        )
        self._meter2degree = pyproj.Transformer.from_crs(
            meter_crs, degree_crs, always_xy=True
        )

    def degree2meter(self, geom):
        return transform(self._degree2meter.transform, geom)

    def meter2degree(self, geom):
        return transform(self._meter2degree.transform, geom)