from klaviyo import Klaviyo


class Lists(Klaviyo):
    LIST = 'list'
    LISTS = 'lists'
    SUBSCRIBE = 'subscribe'

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
        
    def delete_list(self, list_id):
        """
        
        """
        return self._v2_request('{}/{}'.format(self.LIST, list_id), self.HTTP_DELETE)
    
    # TODO, probably better naming for this
    def post_subscribers_to_list(self, profiles):
        """
        Args:
            profiles (dict): for POST -> data must be a list of objects
        """
        params = {
            "profiles": profiles
        }
        return self._v2_request('{}/{}/{}'.format(self.LIST, list_id, self.SUBSCRIBE), self.HTTP_POST, params)
    
    def get_subscription_status
    
    def list_subscription(self, list_id, data, subscription_type='subscribe', method="GET"):
        """
        args:
            list_id: str() the list id
            subscription_type: str() subscribe or members depending on the action
            
            
        """
        api_version = 'v2'

        if method.upper() == "GET":
            if not isinstance(data, list) or not  all(isinstance(s, str) for s in data):
                raise KlaviyoException("Data must be a list of strings")

            params = {
                'emails': data
            }

            return self._request('list/{}/{}'.format(list_id, subscription_type), self.HTTP_GET, params, api_version=api_version)

        elif method.upper() == "POST":
            if not isinstance(data, list) or not isinstance(data[0], dict):
                raise KlaviyoException("Data must be a list of objects")

    def unsubscribe_from_list(self, list_id, emails, subscription_type='subscribe'):
        """
        args:
            list_id: str() the list id
            subscription_type: str() subscribe or members depending on the action
            emails: a list of emails
        """

        params = {
            'emails': emails
        }
        return self._v2_request('list/{}/{}'.format(list_id, subscription_type), self.HTTP_DELETE, params)

    def list_exclusions(self, list_id, marker=None):
        """
        args:
            list_id: str() the list id
            marker: int() optional returned from the previous get call
        """
        params = self._build_marker_param(marker)

        return self._v2_request('list/{}/exclusions/all'.format(list_id), params)

    def all_members(self, group_id, marker=None):
        """
        args:
            id: str() the list id or the segment id
            marker: int() optional returned from the previous get call
        """
        params = self._build_marker_param(marker)

        return self._v2_request('group/{}/members/all'.format(group_id), params)
