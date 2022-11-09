import omero
import numpy as np
import ezomero
from datetime import date, datetime, timedelta
import time

def time_to_int(dateobj):
    total = int(dateobj.strftime('%S'))
    total += int(dateobj.strftime('%M')) * 60
    total += int(dateobj.strftime('%H')) * 60 * 60
    total += (int(dateobj.strftime('%j')) - 1) * 60 * 60 * 24
    total += (int(dateobj.strftime('%Y')) - 1970) * 60 * 60 * 24 * 365
    total *= 1000
    return total

today = date.today()
start =  datetime(today.year, today.month, today.day)
end = start+timedelta(1)
print(time.mktime(start.timetuple()))
username="root"
password="4nM9&WYj"
hostname="ciml.centuri-engineering.univ-amu.fr"
port = 14064

conn = ezomero.connect(user=username, password=password,
                               host=hostname,
                               port=port,
                               secure=True)

im_ids = ezomero.get_image_ids(conn)
for i in im_ids:
    im_object, im_array = ezomero.get_image(conn,i, no_pixels=True)
    if time_to_int(start) < im_object.details.creationEvent.time.val < time_to_int(end):
        print("today " + i)
        image = im_object
        map_ann_data = []

        # Pick these items of metadata -> map annotation
        attributes = ('Camera Name', 'CameraOffset', 'dPosName', 'sObjective')

       # Load the 'Original Metadata' for the image
       # ==========================================
       om = image.loadOriginalMetadata()
       if om is not None:
           key_values = om[1] + om[2]
           for key_value in key_values:
               if len(key_value) > 1 and key_value[0] in attributes:
                   map_ann_data.append([key_value[0], str(key_value[1])])

        # Create a 'map' annotation (list of key: value pairs)
        # ====================================================
        map_ann = omero.gateway.MapAnnotationWrapper(conn)
        map_ann.setNs('original.metadata.from.script')
        map_ann.setValue(map_ann_data)
        map_ann.save()
        image.linkAnnotation(map_ann)

#print(im_object.get_date)
conn.close()
