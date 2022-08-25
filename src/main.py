import time
from datetime import datetime, timedelta
from prometheus_client import PLATFORM_COLLECTOR
from prometheus_client import PROCESS_COLLECTOR
from prometheus_client import start_http_server
from prometheus_client.core import CounterMetricFamily
from prometheus_client.core import REGISTRY
import lib.wg_data_collector as wg_data_collector


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
            "wireguard_geo_location",
            "GEO-IP Location from connected endpoints",
            labels=["public_key", "lat", "long", "endpoint", "isp"]
        )
        for peer_dict in result:
            print(peer_dict)
            metric_collection.add_metric([peer_dict['public_key'], peer_dict['lat'], 
                                          peer_dict['long'], peer_dict['endpoint'], peer_dict['isp']],
                                          int(peer_dict['online_state']))
        yield metric_collection

if __name__ == "__main__":
    wgdc = wg_data_collector.WGDC(prom_url="http://prometheus.fink.home", prom_query={'query': 'wireguard_peer_info'}, geo_api_url="https://json.geoiplookup.io")
    wgdc.fetch()
    print("Started fetching metrics")

    start_http_server(8000)
    REGISTRY.register(CollectEndpointLatLong(wgdc))
    print("Registered Collectors")

    while True:
        time.sleep(300) 
        wgdc.fetch()