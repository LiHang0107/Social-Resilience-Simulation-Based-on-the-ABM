import argparse

import mesa
import mesa_geo as mg

from src.model.model import ResilintJinze
from src.visualization.server import (
    agent_draw,
    clock_element,
    status_chart,
    happiness_chart,
    gentrification_chart
    # friendship_chart,
)


def make_parser():
    parser = argparse.ArgumentParser("Agents and Networks in Python")
    parser.add_argument("--town", type=str, required=True)
    return parser


if __name__ == "__main__":
    args = make_parser().parse_args()

    data_file_prefix = "jz"

    town_params = {
        "jz": {"data_crs": "epsg:4326", "commuter_speed": 0.5},
    }

    model_params = {
        "data_crs": town_params['jz']["data_crs"],
        "areas_file": f"data/raw/{args.town}/{data_file_prefix}_bld.shp",
        "walkway_file": f"data/raw/{args.town}/{data_file_prefix}_walkway_line.shp",
        "show_walkway": True,
        "num_locals": mesa.visualization.Slider(
            "Number of Locals", value=100, min_value=10, max_value=300, step=10
        ),
        "num_tourists": mesa.visualization.Slider(
            "Number of Tourists", value=20, min_value=10, max_value=100, step=10
        ),
        "local_speed": mesa.visualization.Slider(
            "Commuter Walking Speed (m/s)",
            value=town_params['jz']["commuter_speed"],
            min_value=0.1,
            max_value=1.5,
            step=0.1,
        ),
        "tourist_speed": mesa.visualization.Slider(
            "Commuter Walking Speed (m/s)",
            value=town_params['jz']["commuter_speed"],
            min_value=0.1,
            max_value=1.5,
            step=0.1,
        ),
    }

    map_element = mg.visualization.MapModule(agent_draw, map_height=600, map_width=600)

    server = mesa.visualization.ModularServer(
        ResilintJinze,
        [map_element, clock_element, status_chart, happiness_chart, gentrification_chart],
        "ResilintJinze",
        model_params,
    )

    server.launch()