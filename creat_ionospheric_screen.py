"""
Generate a test ionsopheric screen with multiple layers.
ARatmospy must be in the PYTHONPATH https://github.com/shrieks/ARatmospy
"""

import argparse
import numpy
from astropy.io import fits
from astropy.wcs import WCS
from ArScreens import ArScreens


def main():
    # Get command line arguments.
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--num_times", type=int, default=240, help="number of time samples to generate"
    )
    parser.add_argument(
        "--interval_sec", type=float, default=60.0, help="interval between time samples"
    )
    parser.add_argument(
        "--pixel_size_m", type=float, default=100.0, help="pixel size, in metres"
    )
    parser.add_argument(
        "--screen_width_km",
        type=float,
        default=200.0,
        help="width of screen, in kilometres",
    )
    parser.add_argument(
        "--scale_size_km", type=float, default=5.0, help="scale size, in kilometres"
    )
    parser.add_argument("filename", help="name of FITS file to write")
    args = parser.parse_args()

    screen_width_metres = 1000.0 * args.screen_width_km
    r0 = 1000.0 * args.scale_size_km
    bmax = 0.1 * screen_width_metres  # sub-aperture(?) size.
    sampling = args.pixel_size_m
    m = int(bmax / sampling)  # Pixels per sub-aperture (200).
    n = int(screen_width_metres / bmax)  # Sub-apertures across the screen (10).
    num_pix = n * m
    pscale = screen_width_metres / (n * m)  # Pixel scale (100 m/pixel).
    print("Number of pixels %d, pixel size %.3f m" % (num_pix, pscale))
    print("Field of view %.1f (m)" % (num_pix * pscale))
    speed = 150e3 / 3600.0  # 150 km/h in m/s.
    # Parameters for each layer.
    # (scale size [m], speed [m/s], direction [deg], layer height [m]).
    layer_params = numpy.array(
        [(r0, speed, 60.0, 300e3), (r0, speed / 2.0, -30.0, 310e3)]
    )

    rate = 1.0 / args.interval_sec  # The inverse frame rate.
    alpha_mag = 0.999  # Evolve screen slowly.
    num_times = args.num_times
    my_screens = ArScreens(n, m, pscale, rate, layer_params, alpha_mag)
    my_screens.run(num_times)

    # Convert to TEC
    # phase = image[pixel] * -8.44797245e9 / frequency
    frequency = 1e8
    phase2tec = -frequency / 8.44797245e9

    w = WCS(naxis=4)
    w.naxis = 4
    w.wcs.cdelt = [pscale, pscale, 1.0 / rate, 1.0]
    w.wcs.crpix = [num_pix // 2 + 1, num_pix // 2 + 1, num_times // 2 + 1, 1.0]
    w.wcs.ctype = ["XX", "YY", "TIME", "FREQ"]
    w.wcs.crval = [0.0, 0.0, 0.0, frequency]
    data = numpy.zeros([1, num_times, num_pix, num_pix])
    for layer in range(len(my_screens.screens)):
        for i, screen in enumerate(my_screens.screens[layer]):
            data[:, i, ...] += phase2tec * screen[numpy.newaxis, ...]
    fits.writeto(
        filename=args.filename, data=data, header=w.to_header(), overwrite=True
    )


if __name__ == "__main__":
    main()

