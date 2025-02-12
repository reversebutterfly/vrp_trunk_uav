from datetime import datetime
import random
import math

from utils.logger import log_vrp as log


dts = datetime.now()


# nodes
NUM_NODE = 50
NUM_NODE_NAV = 10
LIST_NODE_UAV = list(range(NUM_NODE - NUM_NODE_NAV + 1, NUM_NODE + 1))

# coordinates
random.seed(2021)
RANGE_COORDINATE = (0, 100)
LIST_COORDINATE = [(random.randint(RANGE_COORDINATE[0], RANGE_COORDINATE[1]),
                    random.randint(RANGE_COORDINATE[0], RANGE_COORDINATE[1])) for _ in range(NUM_NODE)]

# distance
ORIGIN = (round((RANGE_COORDINATE[1] - RANGE_COORDINATE[0]) / 2),
          round((RANGE_COORDINATE[1] - RANGE_COORDINATE[0]) / 2))
LIST_COORDINATE_ = [ORIGIN] + LIST_COORDINATE
MAT_DISTANCE = [[0.0 for _ in range(0, NUM_NODE + 1)] for _ in range(0, NUM_NODE + 1)]
range_wave = (0.8, 1.2)
for i in range(0, NUM_NODE + 1):
    for j in range(0, NUM_NODE + 1):
        distance = round(math.sqrt((LIST_COORDINATE_[i][0] - LIST_COORDINATE_[j][0]) ** 2
                                   + (LIST_COORDINATE_[i][1] - LIST_COORDINATE_[j][1]) ** 2)
                         * (range_wave[0] + random.random() * (range_wave[1] - range_wave[0])), 4)
        MAT_DISTANCE[i][j] = distance

# cost
COST_UAV = 0.1

# weight, load
upper_weight_item = 20
LIST_WEIGHT = [random.randint(0, upper_weight_item) for _ in range(NUM_NODE)]
UPPER_LOAD = 100
log.info(msg="total weight:  {}".format(sum(LIST_WEIGHT)))


dte = datetime.now()
tm = round((dte - dts).seconds + (dte - dts).microseconds / (10 ** 6), 3)
log.info(msg="random data generating time:  {} s".format(tm))
