import base64
import datetime
import json
import time

import requests

try:
   from urllib.parse import urlencode
except ImportError:
   from urllib import urlencode


KLAVIYO_DATA_VARIABLE = 'data'
PUBLIC_TOKEN_REQUESTS = ('identify', 'track')
TRACK_ONCE_KEY = '__track_once__'



CUD_REQUEST_TYPE = ("DELETE", "POST", "PUT")

class KlaviyoException(Exception):
    pass

class Klaviyo(object):
    KLAVIYO_API_SERVER = 'https://a.klaviyo.com/api'
    V1_API = 'v1'
    V2_API = 'v2'

    # PUBLIC API PATHS
    IDENTIFY = 'identify'
    TRACK = 'track'
    
    # PRIVATE API PATHS
    EXPORT = 'export'
    LIST = 'list'
    LISTS = 'lists'
    METRIC = 'metric'
    METRICS = 'metrics'
    TIMELINE = 'timeline'

    # HTTP METHODS
    HTTP_DELETE = 'delete'
    HTTP_GET = 'get'
    HTTP_POST = 'post'
    HTTP_PUT = 'put'

    def __init__(self, public_token=None, private_token=None, api_server=KLAVIYO_API_SERVER):
        self.public_token = public_token
        self.private_token = private_token
        self.api_server = api_server

        # if you only need to do one type of request, it's not required to have both private and public.. but we need at least 1 token
        if not self.public_token and not self.private_token:
            raise KlaviyoException('You must provide a public or private api token')

    def track(self, event, email=None, id=None, properties=None, customer_properties=None,
        timestamp=None, ip_address=None, is_test=False):
        
        if email is None and id is None:
            raise KlaviyoException('You must identify a user by email or ID.')
        
        if properties is None:
            properties = {}
        
        if customer_properties is None:
            customer_properties = {}
        
        if email: 
            customer_properties['email'] = email

        if id: 
            customer_properties['id'] = id

        params = {
            'token' : self.public_token,
            'event' : event,
            'properties' : properties,
            'customer_properties' : customer_properties,
            'time' : self._normalize_timestamp(timestamp),
        }

        if ip_address:
            params['ip'] = ip_address

        query_string = self._build_query_string(params, is_test)
        return self._pubic_request(self.TRACK, query_string)

    def track_once(self, event, email=None, id=None, properties=None, customer_properties=None,
        timestamp=None, ip_address=None, is_test=False):
        
        if properties is None:
            properties = {}
        
        properties[TRACK_ONCE_KEY] = True
        
        return self.track(event, email=email, id=id, properties=properties, customer_properties=customer_properties,
            ip_address=ip_address, is_test=is_test)

    def identify(self, email=None, id=None, properties=None, is_test=False):
        if email is None and id is None:
            raise KlaviyoException('You must identify a user by email or ID.')

        if properties is None:
            properties = {}

        if email: properties['email'] = email
        if id: properties['id'] = id

        query_string = self._build_query_string({
            'token' : self.public_token,
            'properties' : properties,
        }, is_test)

        return self._pubic_request(self.IDENTIFY, query_string)

    def get_metrics(self, page=0, count=50):
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
    
    def get_metrics_timeline(self, since=None, count=100, sort='desc'):
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
        
    def get_metric_timeline_by_id(self, metric_id, since=None, count=100, sort='desc'):
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

    def lists(self, list_name=None, method='GET'):
        """
        args:
            method: str() optional type of request
            list_name: str() optional name of list to be created
        """
        api_version = 'v2'
        if method.upper() == 'GET':
            return self._request('lists', api_version=api_version)

        elif method.upper() == 'POST':
            params = {
                'list_name': list_name
            }
            return self._v2_request('lists', params, method=method, api_version=api_version)
            
    def get_lists(self):
        """
        Returns a list of Klaviyo lists
        """
        return self._v2_request('lists', self.HTTP_GET)
    
    def create_lists(self, list_name):
        """
        This will create a new list in Klaviyo
        Args:
            list_name (str): A list name
        """
        return self._v2_request('lists', self.HTTP_POST, list_name)

    def get_list_by_id(self, list_id):
        """
        args:
            list_id: str() the list id
        """
        return self._v2_request('{}/{}'.format(self.LIST, list_id), self.HTTP_GET)
    
    def update_list_by_id(self, list_id, list_name):
        """
        """
        params = dict({
            'list_name': list_name
        })

        return self._v2_request('{}/{}'.format(self.LIST, list_id), self.HTTP_PUT, params)
    
    def list_subscription(self, list_id, data, subscription_type='subscribe', method="GET"):
        """
        args:
            list_id: str() the list id
            subscription_type: str() subscribe or members depending on the action
            data: for POST -> data must be a list of objects, for GET data must be a list of emails
            
        """
        api_version = 'v2'

        if method.upper() == "GET":
            if not isinstance(data, list) or not  all(isinstance(s, str) for s in data):
                raise KlaviyoException("Data must be a list of strings")

            params = {
                'emails': data
            }

            return self._request('list/{}/{}'.format(list_id, subscription_type), params, api_version=api_version)

        elif method.upper() == "POST":
            if not isinstance(data, list) or not isinstance(data[0], dict):
                raise KlaviyoException("Data must be a list of objects")

            params = {
                "profiles": data
            }
            return self._request('list/{}/{}'.format(list_id, subscription_type), params, method=method, api_version=api_version)

    def unsubscribe_from_list(self, list_id, emails, subscription_type='subscribe'):
        """
        args:
            list_id: str() the list id
            subscription_type: str() subscribe or members depending on the action
            emails: a list of emails
        """
        api_version = 'v2'

        params = {
            'emails': emails
        }
        return self._request('list/{}/{}'.format(list_id, subscription_type), params, method="DELETE", api_version=api_version)

    def list_exclusions(self, list_id, marker=None):
        """
        args:
            list_id: str() the list id
            marker: int() optional returned from the previous get call
        """
        api_version = 'v2'
        params = self._build_marker_param(marker)

        return self._request('list/{}/exclusions/all', params, api_version=api_version)

    def all_members(self, group_id, marker=None):
        """
        args:
            id: str() the list id or the segment id
            marker: int() optional returned from the previous get call
        """
        api_version = 'v2'
        params = self._build_marker_param(marker)

        return self._request('group/{}/members/all'.format(group_id), params, api_version=api_version)

    ######################
    # PROFILE API
    ######################
    def get_profile(self, profile_id):
        return self._request('person/{}'.format(profile_id))

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

        return self._request('person/{}/metrics/timeline'.format(profile_id), params)
        
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

        return self._request('person/{}/metric/{}/timeline'.format(profile_id, metric_id), params)

    ######################
    # HELPER FUNCTIONS
    ######################
    def _normalize_timestamp(self, timestamp):
        if isinstance(timestamp, datetime.datetime):
            timestamp = time.mktime(timestamp.timetuple())

        return timestamp

    def _build_query_string(self, params, is_test):
        return urlencode({
            KLAVIYO_DATA_VARIABLE : base64.b64encode(json.dumps(params).encode('utf-8')),
            'test' : 1 if is_test else 0,
        })
        
    def _filter_params(self, params):
        """
        
        """
        return dict((k,v) for k,v in params.items() if v is not None)

    def _build_marker_param(self, marker):
        """
        
        """
        params = {}
        if marker:
            params['marker'] = marker
        return params

    def __is_valid_request_option(self, type='private'):
        """
        """
        if type == 'public' and not self.public_token:
            raise KlaviyoException('Public token is not defined')

        if type == 'private' and not self.private_token:
            raise KlaviyoException('Private token is not defined')

    def _v2_request(self, path, method, params):
        """
        """
        self.__is_valid_request_option()

        params = json.dumps(params)
        
        url = '{}/{}/{}'.format(
            self.api_server, 
            self.V2_API, 
            path, 
        )

        params.update({
            "api_key": self.private_token
        })

        return self.__request(method, url, params).json()

    def _v1_request(self, path, method, params={}):
        """
        """
        self.__is_valid_request_option()
        url = '{}/{}/{}'.format(
            self.api_server, 
            self.V1_API, 
            path, 
        )

        params.update({
            "api_key": self.private_token
        })

        return self.__request(method, url, params).json()

    def _pubic_request(self, path, querystring):
        """
        This handles track and identify calls, always a get request
        Args:
            path (str): track or identify
            querystring (str): urlencoded & b64 encoded string
        Returns:
            (str): 1 or 0 (pass/fail)
        """
        self.__is_valid_request_option('public')

        url = '{}/{}?{}'.format(self.api_server, path, querystring)
        return self.__request('get', url)

    def __request(self, method, url, params={}):
        """
        The method that executes the request being made
        Args:
            method (str): the type of HTTP request
            url (str): the url to make the request to
            params (dict or json): the body of the request
        Returns:
            (str, dict): public returns 1 or 0  (pass/fail)
                        v1/v2 returns dict
        """
        headers = {
            'Content-Type': "application/json",
            'User-Agent': 'Klaviyo/Python {}'.format(self.API_VERSION)
        }
        
        return getattr(requests, method.lower())(url, headers=headers, data=params)
