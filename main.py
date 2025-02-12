from datetime import datetime

from utils.logger import log_vrp as log
from config import vrp as config
from model.vrp import vrp_load
from visual.vrp import scatter_route_vrp


DTS = datetime.now()

NUM_NODE = config.NUM_NODE
LIST_NODE_UAV = config.LIST_NODE_UAV.copy()
LIST_WEIGHT = config.LIST_WEIGHT
UPPER_LOAD = config.UPPER_LOAD
MAT_DISTANCE = config.MAT_DISTANCE.copy()
COST_UAV = config.COST_UAV
log.info(msg="number of nodes:  {}".format(NUM_NODE))
log.info(msg="node can served by uav:  {}".format(LIST_NODE_UAV))


# model
list_routes, dict_uav_route = vrp_load(
    num_node=NUM_NODE, list_node_uav=LIST_NODE_UAV, list_weight=LIST_WEIGHT, upper_load=UPPER_LOAD,
    mat_distance=MAT_DISTANCE, cost_uav=COST_UAV)
for i in range(len(list_routes)):
    log.info(msg="truck route {}:  {}".format(i + 1, list_routes[i]))
for i in dict_uav_route.keys():
    log.info(msg="uav served node:  {},  {}".format(i, dict_uav_route[i]))

# visualisation
scatter_route_vrp(list_routes=list_routes, dict_uav_route=dict_uav_route)


DTE = datetime.now()
TM = round((DTE - DTS).seconds + (DTE - DTS).microseconds / (10 ** 6), 3)
log.info(msg="total time:  {} s".format(TM))
