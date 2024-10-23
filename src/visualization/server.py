import mesa

from src.agent.area import Area
from src.agent.group import Locals, Tourists
from src.agent.geo_agents import Walkway


class ClockElement(mesa.visualization.TextElement):
    def __init__(self):
        super().__init__()
        pass

    def render(self, model):
        return f"Day {model.day}, {model.hour:02d}:{model.minute:02d}"


def agent_draw(agent):
    portrayal = dict()
    portrayal["color"] = "White"
    if isinstance(agent, Walkway):
        portrayal["color"] = "Brown"
    elif isinstance(agent, Area):
        portrayal["color"] = "Grey"
        if agent.function is None:
            portrayal["color"] = "Grey"
        elif agent.function == 1 or agent.function == 2:
            portrayal["color"] = "Yellow"
        elif agent.function == 3:
            portrayal["color"] = "Brown"
        elif agent.function == 4 or agent.function == 5:
            portrayal["color"] = "Orange"
        elif agent.function == 6 or agent.function == 7:
            portrayal["color"] = "Red"
        elif agent.function == 8 or agent.function == 9 or agent.function == 10:
            portrayal["color"] = "Green"
        else:
            portrayal["color"] = "Grey"
    elif isinstance(agent, Locals):
        if agent.status == "home":
            portrayal["color"] = "Green"
        elif agent.status == "activity":
            portrayal["color"] = "Blue"
        elif agent.status == "transport":
            portrayal["color"] = "Red"
        else:
            portrayal["color"] = "Grey"
        portrayal["radius"] = "3"
        portrayal["fillOpacity"] = 1
    elif isinstance(agent, Tourists):
        if agent.status == "home":
            portrayal["color"] = "Grey"
        elif agent.status == "activity":
            portrayal["color"] = "Blue"
        elif agent.status == "transport":
            portrayal["color"] = "Red"
        else:
            portrayal["color"] = "Grey"
        # portrayal["Shape"] = "square"
        portrayal["radius"] = "6"
        portrayal["fillOpacity"] = 1
    return portrayal


clock_element = ClockElement()
status_chart = mesa.visualization.ChartModule(
    [
        {"Label": "status_home", "Color": "Green"},
        {"Label": "status_activity", "Color": "Blue"},
        {"Label": "status_traveling", "Color": "Red"},
        {"Label": "status_work", "Color": "Grey"}
    ],
    data_collector_name="datacollector",
)
happiness_chart = mesa.visualization.ChartModule(
    [
        {"Label": "happiness", "Color": "Red"},
    ],
    data_collector_name="datacollector",
)
gentrification_chart = mesa.visualization.ChartModule(
    [
        {"Label": "gentrification", "Color": "Green"},
    ],
    data_collector_name="datacollector",
)

