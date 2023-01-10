
"""
Simple script that reads all Images uploaded to OMERO on current day

Based on Erick Ratamero's answer in the following forum thread:

https://forum.image.sc/t/filter-omero-images-solely-by-date-using-python/75568

"""

import omero
from omero.gateway import BlitzGateway
import numpy as np
import ezomero
from datetime import date, datetime, timedelta
import time
import credentials as creds

today = date.today()
start =  datetime(today.year, today.month, today.day)
end = start+timedelta(days=1)



username = creds.username
password = creds.password
hostname=  creds.hostname
myport = creds.port

#conn = BlitzGateway(username, password,host=hostname,port=myport,secure=True)

conn = ezomero.connect(user=username, password=password,
                               host=hostname,
                               port=myport,
                               secure=True)


q = conn.getQueryService()
params = omero.sys.Parameters()
timestamp = (today - datetime(1970, 1, 1)) / timedelta(seconds=1)
params.map = {"date": omero.rtypes.rlong(timestamp)}
results = q.projection(
            "select i.id from Image i"
            " where i.details.creationEvent.time > :date",
            params,
            conn.SERVICE_OPTS
            )

print(results)
