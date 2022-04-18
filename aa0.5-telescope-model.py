import sys
sys.path.append('../')
from os import makedirs
from os.path import join
import time
import json

import numpy as np
import matplotlib.pyplot as plt

from scripts.generate_station_layouts import random_layout
# %matplotlib inline

# Station generation settings
num_ant = 256
max_radius = 38 / 2  # m
min_separation = 1.5  # m
seed = 1

# Station coordinates (WGS84 longiture, latitute)
telescope_dir = 'SKA1-LOW-AA0.5-v1.0.tm'

stations = {
    "s010-1": dict(lon=116.69345390, lat=-26.86371635),
    "s010-2": dict(lon=116.69365770, lat=-26.86334071),
    "s008-1": dict(lon=116.72963910, lat=-26.85615287),
    "s008-2": dict(lon=116.73007800, lat=-26.85612864),
    "s009-1": dict(lon=116.74788540, lat=-26.88080530),
    "s009-2": dict(lon=116.74733280, lat=-26.88062234)
}


# Generate and save telescope level files
makedirs(telescope_dir, exist_ok=True)
station_coordinates = []
for station, station_dict in stations.items():
    station_coordinates.append([station_dict['lon'], station_dict['lat']])
layout_file = join(telescope_dir, 'layout_wgs84.txt')
np.savetxt(layout_file, station_coordinates, delimiter=',', fmt="%.8f")
station0 = next(iter(stations.values()))
telescope_position = [ [station0['lon'], station0['lat']]]
np.savetxt(join(telescope_dir, 'position.txt'), telescope_position,
           delimiter=',', fmt="%.8f")

# Generate, save, and plot station level files
np.random.seed(seed)
for station, station_dict in stations.items():
    station_dir = join(telescope_dir, f'station_{station}')
    station_dict['dir'] = station_dir
    t0 = time.time()
    layout = random_layout(num_ant, max_radius, min_separation)
    print(f'Generated station {station} layout in = {time.time() - t0:.2f} s')
    station_dict['layout'] = layout.tolist()
    makedirs(station_dir, exist_ok=True)
    layout_file = join(station_dir, 'layout.txt')
    np.savetxt(layout_file, layout, delimiter=',')
    # Plot the station layout
    fig, ax = plt.subplots(1, figsize=(6, 6))
    ax.plot(layout[:, 0], layout[:, 1], '+')
    for x, y in layout:
        ax.add_artist(plt.Circle((x, y), min_separation/2, fill=False, color='Red'))
    ax.add_patch(plt.Circle((0, 0), max_radius, fill=False, ec='Blue'))
    ax.set_aspect('equal', 'box')
    ax.set(xlim=(-max_radius - 1, max_radius + 1),
           ylim=(-max_radius - 1, max_radius + 1))
    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.grid()
    # plt.show()
    plt.savefig(join(station_dir, "layout.png"), bbox_inches='tight', dpi=300,
                transparent=False, facecolor='white')
    plt.close()