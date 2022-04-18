"""
Generate station layouts for use with randomised station layout study.
"""
import math
import os
import time
import numpy
import matplotlib

# pylint: disable=wrong-import-position
matplotlib.use("agg")
import matplotlib.pyplot as plt


def random_layout(n, r_max, min_sep, timeout=None):
    """Generate 2D random points with a minimum separation within a radius
    specified by r_max.

    Args:
        n (int): Number of points to generate.
        r_max (float): Maximum radius.
        min_sep (float): Minimum separation of points.
        timeout (Optional[float]): Timeout, in seconds.

    Returns:
        2D array
    """
    grid_size = min(100, int(math.ceil(float(r_max * 2.0) / min_sep)))
    grid_cell = float(r_max * 2.0) / grid_size  # Grid sector size
    scale = 1.0 / grid_cell  # Scaling onto the sector grid.

    xy = numpy.zeros((n, 2))
    grid_start = numpy.zeros((grid_size, grid_size), dtype="i8")
    grid_end = numpy.zeros((grid_size, grid_size), dtype="i8")
    grid_count = numpy.zeros((grid_size, grid_size), dtype="i8")
    grid_next = numpy.zeros(n, dtype="i8")

    t0 = time.time()
    for j in range(n):
        while True:
            if timeout and (time.time() - t0 >= timeout):
                return xy[: (j - 1), :]

            # Get trial coordinates.
            xt, yt = tuple(numpy.random.rand(2) * 2.0 * r_max - r_max)
            if ((xt ** 2 + yt ** 2) ** 0.5 + min_sep / 2.0) > r_max:
                continue

            # Get tile indices and tile ranges to check.
            jx = int(round(xt + r_max) * scale)
            jy = int(round(yt + r_max) * scale)
            y0 = max(0, jy - 2)
            y1 = min(grid_size, jy + 3)
            x0 = max(0, jx - 2)
            x1 = min(grid_size, jx + 3)

            # Find minimum spacing between trial and neighbouring points.
            d_min = r_max * 2.0
            for ky in range(y0, y1):
                for kx in range(x0, x1):
                    if grid_count[ky, kx] > 0:
                        i_other = grid_start[ky, kx]
                        for _ in range(grid_count[ky, kx]):
                            dx = xt - xy[i_other, 0]
                            dy = yt - xy[i_other, 1]
                            d_other = (dx ** 2 + dy ** 2) ** 0.5
                            d_min = min(d_min, d_other)
                            i_other = grid_next[i_other]

            # Accept the point if it's far enough from its neighbours.
            if d_min >= min_sep:
                xy[j, 0], xy[j, 1] = xt, yt
                if grid_count[jy, jx] == 0:
                    grid_start[jy, jx] = j
                else:
                    grid_next[grid_end[jy, jx]] = j
                grid_end[jy, jx] = j
                grid_count[jy, jx] += 1
                break
    return xy


def generate_telescope_model(num_stations, num_different_stations, seed=1):
    """Creates a telescope model directory using the supplied parameters."""
    telescope_dir = (
        "SKA1-LOW_SKO-0000422_Rev3_%03d_different_38m_stations.tm"
        % num_different_stations
    )
    if os.path.isdir(telescope_dir):
        print("%s already exists" % telescope_dir)
        return
    os.makedirs(telescope_dir)
    stations = []
    numpy.random.seed(seed)
    station_types = numpy.zeros(num_stations, dtype="i8")
    for _ in range(num_different_stations):
        stations.append(random_layout(256, 19.0, 1.5))
    for i_station in range(num_stations):
        station_types[i_station] = i_station % num_different_stations
    numpy.random.shuffle(station_types)
    for i_station in range(num_stations):
        station_type = station_types[i_station]
        station_dir = os.path.join(
            telescope_dir, "station%03d-type%03d" % (i_station, station_type)
        )
        layout_file = os.path.join(station_dir, "layout.txt")
        os.makedirs(station_dir)
        numpy.savetxt(layout_file, stations[station_type], delimiter=",")
    labels, counts = numpy.unique(station_types, return_counts=True)
    plt.bar(labels, counts, align="center")
    plt.gca().set_xticks(labels)
    plt.savefig(os.path.join(telescope_dir, "station_types.png"))
    plt.close()


# for i in range(10):
#    generate_telescope_model(512, i+1)
# for i in range(9):
#    generate_telescope_model(512, 2**i)
# generate_telescope_model(512, 512)
generate_telescope_model(512, 512, 10)
