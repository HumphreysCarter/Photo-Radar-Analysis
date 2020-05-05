# Carter J. Humphreys
# https://github.com/HumphreysCarter

from PIL import Image, ExifTags
from datetime import datetime

# Get lat/lon from tuple and convert from degrees/minutes/centiseconds to decimal degrees
def getDecimalDegrees(gpsTuple, gpsRef):
    degrees = gpsTuple[0][0]
    minutes = gpsTuple[1][0]
    centiseconds = gpsTuple[2][0]

    if (centiseconds < 6000):
        decimal = degrees + (minutes/60.0) + (centiseconds/(3600.0*100.0))
    else:
        decimal = degrees + (minutes/60.0)

    if gpsRef in ['S', 'W']:
        decimal = decimal * -1

    return float(decimal)

# Open image and extract EXIF metadata
def getEXIF(imagePath, findDateTime, findLatLon):
    img = Image.open(imagePath)

    photoTime = -9999
    if findDateTime:
        try:
            exif = { ExifTags.TAGS[k]: v for k, v in img._getexif().items() if k in ExifTags.TAGS }

            # Pull date and time from EXIF
            photoTime = datetime.strptime(exif['DateTimeOriginal'], '%Y:%m:%d %H:%M:%S')
        except:
            print('ERROR: Unable to extract date and time from ' + imagePath)

    photoLat = -99.99
    photoLon = -99.99
    if findLatLon:
        try:
            # Pull GPS coordinates from EXIF
            # Source: https://stackoverflow.com/questions/19804768/interpreting-gps-info-of-exif-data-from-photo-in-python
            gpsinfo = {}
            for key in exif['GPSInfo'].keys():
                decode = ExifTags.GPSTAGS.get(key, key)
                gpsinfo[decode] = exif['GPSInfo'][key]

            photoLat = getDecimalDegrees(gpsinfo['GPSLatitude'], gpsinfo['GPSLatitudeRef'])
            photoLon = getDecimalDegrees(gpsinfo['GPSLongitude'], gpsinfo['GPSLongitudeRef'])
        except:
            print('ERROR: Unable to extract lat/lon from ' + imagePath)

    exifData={'Time':photoTime, 'Latitude':photoLat, 'Longitude':photoLon}

    return exifData