import tempfile
import json
import os

import shapely.wkt
import shapely.geometry

def first_from_filename(filename):
    """read the first geometry from filename"""
    import ogr
    ds = ogr.Open(filename)
    layer = ds.GetLayer(0)
    feature = layer.GetFeature(0)
    geometry = feature.geometry()
    wkt = geometry.ExportToWkt()
    return shapely.wkt.loads(wkt)
def first_from_bytes(bytes):
    """read the first geometry from bytes"""
    import ogr
    with tempfile.NamedTemporaryFile(prefix="pywpsInput",dir=os.curdir) as f:
        open(f.name, 'w').write(bytes)
        ds = ogr.Open(f.name)
        layer = ds.GetLayer(0)
        feature = layer.GetFeature(0)
        geometry = feature.geometry()
        wkt = geometry.ExportToWkt()
    return shapely.wkt.loads(wkt)

def decode(file_or_text):
    """combine several decoders to read geo data

    >>> location_wkt = "POINT(54 2)"
    >>> location_json = '{ "type": "LineString", "coordinates": [[51.0, 3.0], [52.0, 3.1]] }'
    >>> location_gml = '''<?xml version="1.0" encoding="utf-8" ?>
    ... <root
    ... xmlns:gml="http://www.opengis.net/gml"
    ... >
    ... <gml:featureMember>
    ... <gml:geometryProperty>
    ... <gml:Point >
    ... <gml:coordinates>54,3.1</gml:coordinates>
    ... </gml:Point>
    ... </gml:geometryProperty>
    ... </gml:featureMember>
    ... </root>
    ... '''

    >>> for location in [location_wkt, location_json, location_gml]:
    ...    decode(location).type
    'Point'
    'LineString'
    'Point'
"""
    # decoders for file or text
    decoders = {
        True: [
            lambda x: shapely.geometry.shape(json.loads(open(x,'r').read())),
            lambda x: shapely.wkt.loads(open(x, 'r').read()),
            first_from_filename
        ],
        False: [
            lambda x: shapely.geometry.shape(json.loads(x)),
            shapely.wkt.loads,
            first_from_bytes
            ]
        }
    for decoder in decoders[os.path.isfile(file_or_text)]:
        try:
            # try all the decoders and stop if it works
            geom = decoder(file_or_text)
            break
        except:
            # no worries, keep trying
            pass
    else:
        # we have not found a working decoder
        raise ValueError("could not decode %r" % file_or_text)
    return geom
if __name__ == '__main__':
    import doctest
    doctest.testmod()
