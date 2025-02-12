from datetime import datetime
from typing import List, Dict, Tuple
import math
from gurobipy import *

from utils.logger import log_vrp as log


def vrp_load(num_node: int, list_node_uav: List[int], list_weight: List[int], upper_load: int,
             mat_distance: List[List[int]], cost_uav: float = 0.5) \
        -> Tuple[List[List[int]], Dict[int, Tuple[int, int]]]:
    """
    VRP model, load limit mode

    :param num_node:  number of nodes
    :param list_node_uav:  nodes can be served by uav
    :param list_weight:  weight of each node
    :param upper_load:  upper limit of vehicle loads
    :param mat_distance:  distance matrix,  0 index for hub
    :param cost_uav:  cost coefficient of uav

    :return: list_routes:  list of truck routes
    :return: dict_uav_route:  dict of uav routes
    """

    log.info(msg=">>> VRP model, load limit mode, start")

    model = Model('vrp_load')

    """ variables """

    # if truck flow from i to j
    x = model.addVars([(i, j) for i in range(0, num_node + 1) for j in range(0, num_node + 1)], vtype=GRB.BINARY,
                      name='x_')

    # if uav flow from i to j
    y = model.addVars([(i, j) for i in range(0, num_node + 1) for j in range(0, num_node + 1)], vtype=GRB.BINARY,
                      name='y_')

    # if served by truck
    s = model.addVars([i for i in range(1, num_node + 1)], vtype=GRB.BINARY, name='s_')

    # load limit: arc weight
    z = model.addVars([(i, j) for i in range(0, num_node + 1) for j in range(0, num_node + 1)], ub=upper_load,
                      vtype=GRB.CONTINUOUS, name='a_')

    """ constraints """

    # cons 1: stream in / out, not including origin
    for i in range(1, num_node + 1):
        # nodes can only served by truck
        if i not in list_node_uav:
            model.addConstr(quicksum(x[j, i] for j in range(0, num_node + 1)) == 1, name='cons_1_in_x_[{}]'.format(i))
            model.addConstr(quicksum(x[i, j] for j in range(0, num_node + 1)) == 1, name='cons_1_out_x_[{}]'.format(i))

        # nodes can served by truck or uav
        else:
            model.addConstr(quicksum(x[j, i] + y[j, i] for j in range(0, num_node + 1)) == 1,
                            name='cons_1_in_xy_[{}]'.format(i))
            model.addConstr(quicksum(x[i, j] + y[i, j] for j in range(0, num_node + 1)) == 1,
                            name='cons_1_out_xy_[{}]'.format(i))

            # truck or uav
            model.addConstr(quicksum(y[j, i] for j in range(0, num_node + 1))
                            == quicksum(y[i, j] for j in range(0, num_node + 1)), name='cons_1_y[{}]'.format(i))

    # cons 2: self-loop elimination
    model.addConstr(quicksum(x[i, i] for i in range(0, num_node + 1)) == 0, name='cons_2_x')
    model.addConstr(quicksum(y[i, i] for i in range(0, num_node + 1)) == 0, name='cons_2_y')

    # cons 3: get, if served by truck
    for i in range(1, num_node + 1):
        model.addConstr(s[i] == quicksum(x[i, j] for j in range(0, num_node + 1)), name='cons_3_[{}]'.format(i))

    # cons 4: load limit, including sub-loop elimination
    big_m = 10 ** 6
    for j in range(1, num_node + 1):
        for i in range(0, num_node + 1):
            list_not_j = list(range(0, j)) + list(range(j + 1, num_node + 1))
            list_uav_not_j = list_node_uav.copy()
            if j in list_uav_not_j:
                list_uav_not_j.remove(j)
            model.addConstr(z[i, j] >= list_weight[j - 1] + quicksum(z[j, k] for k in list_not_j)
                            + quicksum(y[j, u] * list_weight[u - 1] for u in list_uav_not_j) + (x[i, j] - 1) * big_m,
                            name='cons_4_[{},{}]'.format(i, j))

            model.addConstr(z[i, j] <= x[i, j] * big_m, name='cons_4_zx_[{},{}]'.format(i, j))

            # todo: sun-loop elimination:  2-node loop
            if i:
                model.addConstr(x[i, j] + x[j, i] <= 1, name='cons_4_loop_2[{},{}]'.format(i, j))

    # cons 5: uav order
    for j in list_node_uav:
        for i in range(0, num_node + 1):
            for k in range(0, num_node + 1):
                model.addConstr(y[i, j] + y[j, k] <= 2 * x[i, k] + 1, name='cons_5_[{},{},{}]'.format(i, j, k))

    # cons 6: only one uav
    for i in range(0, num_node + 1):
        model.addConstr(quicksum(y[i, j] for j in range(0, num_node + 1)) <= 1, name='cons_6_out_[{}]'.format(i))
        model.addConstr(quicksum(y[j, i] for j in range(0, num_node + 1)) <= 1, name='cons_6_in_[{}]'.format(i))

    # cons 7: valid inequality
    model.addConstr(quicksum(x[0, j] for j in range(1, num_node + 1)) >= math.ceil(sum(list_weight) / upper_load),
                    name='cons_7')

    """ objective & solve """

    num_vehicle = quicksum(x[0, j] for j in range(1, num_node + 1))
    sum_distance = quicksum(x[i, j] * mat_distance[i][j] + y[i, j] * mat_distance[i][j] * cost_uav
                            for i in range(0, num_node + 1) for j in range(0, num_node + 1))
    model.setObjective(num_vehicle * big_m + sum_distance, sense=GRB.MINIMIZE)

    model.setParam(GRB.Param.TimeLimit, 600)
    model.setParam(GRB.Param.MIPGap, 0.05)

    dts_solve = datetime.now()
    model.optimize()
    dte_solve = datetime.now()
    tm_solve = round((dte_solve - dts_solve).seconds + (dte_solve - dts_solve).microseconds / (10 ** 6), 3)
    log.info(msg="solving time:  {} s".format(tm_solve))

    """ result """

    x_ = model.getAttr('X', x)
    y_ = model.getAttr('X', y)
    s_ = model.getAttr('X', s)

    num_vehicle_ = int(sum(x_[0, j] for j in range(1, num_node + 1)))
    log.info("total vehicles: {}".format(num_vehicle_))

    # uav routes
    list_node_uav_ = []
    dict_uav_route = {}
    for j in list_node_uav:
        if s_[j] < 0.1:
            list_node_uav_.append(j)

            fr, to = None, None
            for i in range(0, num_node + 1):
                if y_[i, j] > 0.9:
                    fr = i
                    break
            for k in range(0, num_node + 1):
                if y_[j, k] > 0.9:
                    to = k
                    break
            tup_fr_to = (fr, to)
            dict_uav_route[j] = tup_fr_to
    log.info(msg="nodes can be served by uav:  {}".format(list_node_uav))
    log.info(msg="nodes served by uav:  {}".format(list_node_uav_))

    # truck routes
    list_routes = []
    set_node = set(range(0, num_node + 1))
    while len(set_node) > 1 + len(list_node_uav_):  # todo: number of nodes served by truck
        list_route_cur = [0]
        to = None
        while to != 0:
            if to:
                set_node.remove(to)
            for i in set_node:
                if x_[list_route_cur[-1], i] > 0.9:
                    to = i
                    list_route_cur.append(to)
                    break
        list_routes.append(list_route_cur)

    log.info(msg="<<< TSP model, GG formulation, end")

    return list_routes, dict_uav_route
