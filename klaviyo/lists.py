from klaviyo import Klaviyo


class Lists(Klaviyo):
    LIST = 'list'
    LISTS = 'lists'

    def __init__(self):
        pass

    def get_lists(self):
        """ Returns a list of Klaviyo lists """
        return self._v2_request('lists', self.HTTP_GET)
    
    def create_list(self, list_name):
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