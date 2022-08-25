import time
from prometheus_client import PLATFORM_COLLECTOR
from prometheus_client import PROCESS_COLLECTOR
from prometheus_client import start_http_server
from prometheus_client.core import CounterMetricFamily
from prometheus_client.core import REGISTRY
import lib.wg_data_collector as wg_data_collector

import os

# unregister not used metrics
# pylint: disable=protected-access
REGISTRY.unregister(PLATFORM_COLLECTOR)
REGISTRY.unregister(PROCESS_COLLECTOR)
REGISTRY.unregister(
    REGISTRY._names_to_collectors["python_gc_objects_collected_total"])


class CollectEndpointLatLong:
    """
    Custom Collector Class for getting the lat and long for a IP
    """

    def __init__(self, wgdc: wg_data_collector.WGDC):
        self.wgdatacollector = wgdc

    def collect(self):
        """
        Collects metrics

        :return: one pair of lat/lon for each endpoint
        """
        result = self.wgdatacollector.result
        metric_collection = CounterMetricFamily(
            "wireguard_geo_location_test",
            "GEO-IP Location from connected endpoints",
            labels=["public_key", "latitude", "longitude", "endpoint", "isp"]
        )
        for peer_dict in result:
            if int(peer_dict['online_state']) == 1:
                metric_collection.add_metric([peer_dict['public_key'], peer_dict['lat'], 
                                              peer_dict['long'], peer_dict['endpoint'], peer_dict['isp']],
                                              int(peer_dict['online_state']))
        yield metric_collection

if __name__ == "__main__":
    wgdc = wg_data_collector.WGDC(prom_url=os.environ['PROM_URL'], prom_query=os.environ['PROM_QUERY'], geo_api_url=os.environ['GEO_API_URL'])
    wgdc.fetch()
    print("Started fetching metrics")

    start_http_server(8000)
    REGISTRY.register(CollectEndpointLatLong(wgdc))
    print("Registered Collectors")

    while True:
        time.sleep(300) 
        wgdc.fetch()