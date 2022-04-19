from astropy.io import fits
import numpy
import oskar
 
data = fits.getdata('GLEAM_EGC.fits', 1)
sky_array = numpy.column_stack(
                (data['RAJ2000'], data['DEJ2000'], data['peak_flux_wide']))
sky = oskar.Sky.from_array(sky_array)
 
ra0 = 0.
dec0 = -27.
filtered = sky.filter_by_radius(0, 8, ra0, dec0)
 
sky_array = sky.to_array()
sorted_sky_array = sorted(sky_array, key=lambda col: col[2], reverse=True)
brightest = sorted_sky_array[0:20]
print(brightest)
 
sky_filtered = oskar.Sky.from_array(brightest)
sky_filtered.save("sources_filtered.txt")
