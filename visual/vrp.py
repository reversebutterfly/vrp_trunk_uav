import os
from typing import List, Dict, Tuple
import matplotlib.pyplot as plt

from config import vrp as config


PATH = os.path.dirname(os.path.dirname(__file__))


def scatter_route_vrp(list_routes: List[List[int]], dict_uav_route: Dict[int, Tuple[int, int]]):
    """
    scatters and route of vrp result

    :param list_routes:  list of truck route
    :param dict_uav_route:  dict of uav routes

    :return: nothing
    """

    num_node = config.NUM_NODE
    list_node_uav = config.LIST_NODE_UAV
    origin = config.ORIGIN
    list_coordinate_ = config.LIST_COORDINATE_
    range_coordinate = config.RANGE_COORDINATE

    # scatters
    plt.scatter(x=origin[0], y=origin[1], s=50, c='black', label='origin')
    for i in range(1, num_node + 1):
        color = 'blue' if i not in list_node_uav else 'red'
        plt.scatter(x=list_coordinate_[i][0], y=list_coordinate_[i][1], s=20, c=color, label=str(i))

    width = 0.2
    head_width = 2
    head_length = 3
    alpha = 0.7
    color_truck, color_uav = 'green', 'orange'
    line_width = 0.5

    # truck routes
    for route in list_routes:
        for i in range(len(route) - 1):
            plt.arrow(x=list_coordinate_[route[i]][0], y=list_coordinate_[route[i]][1],
                      dx=list_coordinate_[route[i + 1]][0] - list_coordinate_[route[i]][0],
                      dy=list_coordinate_[route[i + 1]][1] - list_coordinate_[route[i]][1],
                      width=width, length_includes_head=True, head_width=head_width, head_length=head_length,
                      alpha=alpha, color=color_truck, linestyle='-', linewidth=line_width)

    # uav routes
    for i in dict_uav_route.keys():
        plt.arrow(x=list_coordinate_[dict_uav_route[i][0]][0], y=list_coordinate_[dict_uav_route[i][0]][1],
                  dx=list_coordinate_[i][0] - list_coordinate_[dict_uav_route[i][0]][0],
                  dy=list_coordinate_[i][1] - list_coordinate_[dict_uav_route[i][0]][1],
                  width=width, length_includes_head=True, head_width=head_width, head_length=head_length,
                  alpha=alpha, color=color_uav, linestyle='--', linewidth=line_width)
        plt.arrow(x=list_coordinate_[i][0], y=list_coordinate_[i][1],
                  dx=list_coordinate_[dict_uav_route[i][1]][0] - list_coordinate_[i][0],
                  dy=list_coordinate_[dict_uav_route[i][1]][1] - list_coordinate_[i][1],
                  width=width, length_includes_head=True, head_width=head_width, head_length=head_length,
                  alpha=alpha, color=color_uav, linestyle='--', linewidth=line_width)

    # x, y range
    edge = 5
    plt.xlim(range_coordinate[0] - edge, range_coordinate[1] + edge)
    plt.ylim(range_coordinate[0] - edge, range_coordinate[1] + edge)

    # save
    path = os.path.join(PATH, "output/vrp.png")
    plt.savefig(path)
