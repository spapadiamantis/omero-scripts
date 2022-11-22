#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This a basic OMERO script that runs server-side and
turns original metadata into map annotations
"""

# Import
import omero
import omero.scripts as scripts
from omero.gateway import BlitzGateway
from omero.rtypes import robject, rstring

# load
def original_metadata_to_map_ann(conn, dataset_id, attributes=None):
    """
    Load the images in the specified dataset
    :param conn: The BlitzGateway
    :param dataset_id: The dataset's id
    :return: The Images or None
    """
    dataset = conn.getObject("Dataset", dataset_id)
    images = []
    if dataset is None:
        return None
    for image in dataset.listChildren():
        images.append(image)
    if len(images) == 0:
        return None

    for image in images:
        print("---- Processing image", image.id)
        image = conn.getObject("Image", image.id)

        map_ann_data = []

        # Pick these items of metadata -> map annotation
        if attributes is None:
            attributes = ('Information|Document|Comment', 'Information|Document|Description')

        # Load the 'Original Metadata' for the image
        # ==========================================
        #if not image.listAnnotations():
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

    return images


# main
if __name__ == "__main__":
    # Start declaration
    # Define the script name and description, and a single 'required' parameter
    client = scripts.client(
        'Original_Metadata_Server_Side.py',
        """
        This script does connect to OMERO.
        """,
        scripts.Long("datasetId", optional=False,grouping='1'),
        scripts.String("Tags", grouping="2.1",
            description="Optional parameter, contains the names of the key-value pairs, returns all map annotation if left empty, values should be separated with commas"),
        authors=["OME Team", "OME Team"],
        institutions=["University of Dundee"],
        contact="ome-users@lists.openmicroscopy.org.uk",
    )
    # Start script
    try:
        # process the list of arguments
        script_params = {}
        for key in client.getInputKeys():
            if client.getInput(key):
                script_params[key] = client.getInput(key, unwrap=True)

        dataset_id = script_params["datasetId"]
        attributes = script_params["Tags"]
        attributes = attributes.split(", ")
        attributes = tuple(i for i in attributes)

        # wrap client to use the Blitz Gateway                if len(key_value) > 1 and key_value[0] in attributes:

        conn = BlitzGateway(client_obj=client)

        # load the images
        images = original_metadata_to_map_ann(conn, dataset_id, attributes)

        # return output to the user
        if images is None:
            message = "No images found"
        else:
            message = "Returned %s images" % len(images)
            # return first image:
            client.setOutput("Image", robject(images[0]._obj))

        client.setOutput("Message", rstring(message))
        # end output
    finally:
        client.closeSession()
