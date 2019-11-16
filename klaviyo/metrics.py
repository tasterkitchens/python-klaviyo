from klaviyo import Klaviyo

STARTING_PAGE = 0
DEFAULT_BATCH_SIZE = 50
TIMELINE_BATCH_SIZE = DEFAULT_BATCH_SIZE + DEFAULT_BATCH_SIZE

class Metrics(Klaviyo):
    EXPORT = 'export'
    METRIC = 'metric'
    METRICS = 'metrics'
    TIMELINE = 'timeline'

    def __init__(self):
        pass

    def get_metrics(self, page=STARTING_PAGE, count=DEFAULT_BATCH_SIZE):
        """
        Args:
            page: int() page of results to return
            count: int() number of results to return
        Return:
            (dict): with data list of metrics
        """
        params = {
            'page': page,
            'count': count
        }
        return self._v1_request(self.METRICS, self.HTTP_GET, params)
    
    def get_metrics_timeline(self, since=None, count=TIMELINE_BATCH_SIZE, sort='desc'):
        """"
        Fetches all of the metrics and it's events regardless of the statistic
        Args:
            since (str or int): next attribute of the previous api call or unix timestamp
            count (int): number of events retuned
            sort (str): sort order for timeline
        Returns:
            (dict): metric timeline information
        """
        params = {
            'count': count,
            'sort': sort,
            'since': since
        }
        params = self._filter_params(params)
        url = '{}/{}'.format(self.METRICS, TIMELINE)

        return self._v1_request(url, self.HTTP_GET, params)
        
    def get_metric_timeline_by_id(self, metric_id, since=None, count=TIMELINE_BATCH_SIZE, sort='desc'):
        """"
        Args:
            metric_id (str): metric ID for the statistic
            since (str or int): next attribute of the previous api call or unix timestamp
            count (int): number of events retuned
            sort (str): sort order for timeline
        """
        params = {
            'count': count,
            'sort': sort,
            'since': since
        }
        params = self._filter_params(params)
        url = '{}/{}/{}'.format(self.METRIC, metric_id, TIMELINE)

        return self._v1_request(url, self.HTTP_GET, params)

    def metric_export(
        self, 
        metric_id, 
        start_date=None, 
        end_date=None, 
        unit=None, 
        measurement=None, 
        where=None, 
        by=None, 
        count=None
        ):
        params = {
            'metric_id': metric_id,
            'start_date': start_date,
            'end_date': end_date, 
            'unit': unit,
            'measurement': measurement,
            'where': where,
            'by': by,
            'count': count
        }
        params = self._filter_params(params)

        url = '{}/{}/{}'.format(self.METRIC, metric_id, self.EXPORT)

        return self._v1_request(url, self.HTTP_GET, params)