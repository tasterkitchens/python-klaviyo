from klaviyo import Klaviyo

class Profiles(Klaviyo):
    PERSON = 'person'

    def get_profile(self, profile_id):
        return self._v1_request('{}/{}'.format(self.PERSON, profile_id))

    def get_profile_metrics_timeline(self, profile_id, since=None, count=100, sort='desc'):
        """
        args:
            profile_id (str): unique id for profile
            since (unix timestamp int or uuid str): a timestamp or uuid
            count (int): the batch of records the response should return
            sort (str): the order in which results should be returned
        """
        params = {
            'since': since,
            'count': count,
            'sort': sort
        }
        params = self._filter_params(params)

        return self._request('{}/{}/metrics/timeline'.format(self.PERSON, profile_id), params)

    def get_profile_metric_timeline(self, profile_id, metric_id, since=None, count=100, sort='desc'):
        """
        args:
            profile_id (str): unique id for profile
            metric_id (str): unique id for metric
            since (unix timestamp int or uuid str): a timestamp or uuid
            count (int): the batch of records the response should return
            sort (str): the order in which results should be returned
        """
        params = {
            'since': since,
            'count': count,
            'sort': sort
        }
        params = self._filter_params(params)

        return self._request('{}/{}/metric/{}/timeline'.format(self.PERSON, profile_id, metric_id), params)
