import sys

import osmium
import geojson
import shapely.geometry

from robosat.osm.core import FeatureStorage, is_polygon


class BuildingHandler(osmium.SimpleHandler):
    """Extracts building polygon features (visible in satellite imagery) from the map.
    """

    # building=* to discard because these features are not vislible in satellite imagery
    building_filter = set(
        ["construction", "houseboat", "static_caravan", "stadium", "conservatory", "digester", "greenhouse", "ruins"]
    )

    # location=* to discard because these features are not vislible in satellite imagery
    location_filter = set(["underground", "underwater"])

    def __init__(self, out, batch):
        super().__init__()
        self.storage = FeatureStorage(out, batch)

    def way(self, w):
        if not is_polygon(w):
            return

        if "building" not in w.tags:
            return

        if w.tags["building"] in self.building_filter:
            return

        if "location" in w.tags and w.tags["location"] in self.location_filter:
            return

        geometry = geojson.Polygon([[(n.lon, n.lat) for n in w.nodes]])
        shape = shapely.geometry.shape(geometry)

        if shape.is_valid:
            feature = geojson.Feature(geometry=geometry)
            self.storage.add(feature)
        else:
            print("Warning: invalid feature: https://www.openstreetmap.org/way/{}".format(w.id), file=sys.stderr)

    def flush(self):
        self.storage.flush()
