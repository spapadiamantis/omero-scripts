"""
Simple script that reads all Images uploaded to OMERO on current day 
and annotates Original metadata as map annotations

Based on Will Moore's code that can be found here:

https://gist.github.com/will-moore/03ef6cbd1f95d837af747538ba379b4c

"""

import omero
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
port = creds.port

conn = ezomero.connect(user=username, password=password,
                               host=hostname,
                               port=port,
                               secure=True)

im_ids = ezomero.get_image_ids(conn,dataset=102)


for i in im_ids:
    im_object, im_array = ezomero.get_image(conn,i, no_pixels=True)
    if start.timestamp()*1000 < im_object.details.creationEvent.time.val < end.timestamp()*1000:
        print("today " + str(i))
        image = im_object
        map_ann_data = []

        # Pick these items of metadata -> map annotation
        attributes = ('Camera Name', 'Description', 'dPosName', 'sObjective')

        # Load the 'Original Metadata' for the image
        # ==========================================
        om = image.loadOriginalMetadata()
        print(om)
        if om is not None:
           key_values = om[1] + om[2]
           for key_value in key_values:
               #if len(key_value) > 1 and key_value[0] in attributes:
               map_ann_data.append([key_value[0], str(key_value[1])])

        # Create a 'map' annotation (list of key: value pairs)
        # ====================================================
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        map_ann.setNs('original.metadata.from.script')
        map_ann.setValue(map_ann_data)
        map_ann.save()
        image.linkAnnotation(map_ann)


conn.close()
