# Carter J. Humphreys
# https://github.com/HumphreysCarter

from datetime import datetime, timedelta
import s3fs
import numpy as np
import boto3
import botocore
from botocore.client import Config
from metpy.io import Level2File

# Use the anonymous credentials to access public data
fs = s3fs.S3FileSystem(anon=True)

def getFile(fileName):
    s3 = boto3.resource('s3', config=Config(signature_version=botocore.UNSIGNED, user_agent_extra='Resource'))

    bucket = s3.Bucket('noaa-nexrad-level2')
    for obj in bucket.objects.filter(Prefix=fileName):
        print(obj.key)

        # Use MetPy to read the file
        return Level2File(obj.get()['Body'])

def getLatestScan(radarSite):
    # List contents of NOAA NEXRAD L2 bucket
    radarBin = np.array(fs.ls('s3://noaa-nexrad-level2/'))

    # Get latest year (Subtract 2 to remove index.html)
    radarBin = np.array(fs.ls(radarBin[len(radarBin)-2]))

    # Get latest month
    radarBin = np.array(fs.ls(radarBin[len(radarBin)-1]))

    # Get latest day
    radarBin = np.array(fs.ls(radarBin[len(radarBin)-1] + '/' + radarSite))

    # Get latest file
    radarBin = np.array(fs.ls(radarBin[len(radarBin)-1]))
    latestScan = radarBin[0].replace('_MDM', '')

    return latestScan

def getArchivedScan(radarSite, time):
    # List contents of NOAA NEXRAD L2 bucket for given date/time and radar
    radarBin = np.array(fs.ls('s3://noaa-nexrad-level2/' + time.strftime('%Y/%m/%d') + '/' + radarSite + '/'))

    closestScan=radarBin[0]
    closestScanTime=99999

    for scan in radarBin:

        if '.ta' not in scan and '_MDM' not in scan:
            # Capture time from scan
            s = scan.rfind('/') + 1
            e = scan.rfind('_V06')

            scanTime = datetime.strptime(scan[s:e], radarSite+'%Y%m%d_%H%M%S')

            # Find closest scan
            timeDif = scanTime-time
            if (abs(timeDif.total_seconds())<=closestScanTime):
                closestScanTime = abs(timeDif.total_seconds())
                closestScan = scan

    return closestScan