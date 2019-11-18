from klaviyo import Klaviyo, KlaviyoException


class Public(Klaviyo):
    # PUBLIC API PATHS
    IDENTIFY = 'identify'
    TRACK = 'track'

    TOKEN = 'token'
    ERROR_MESSAGE_ID_AND_EMAIL = 'You must identify a user by email or ID.'

    def __init__(self):
        pass

    def track(self, event, email=None, id=None, properties=None, customer_properties=None,
        timestamp=None, ip_address=None, is_test=False):
        
        if email is None and id is None:
            raise KlaviyoException(self.ERROR_MESSAGE_ID_AND_EMAIL)

        if properties is None:
            properties = {}
        
        if customer_properties is None:
            customer_properties = {}

        if email: 
            customer_properties['email'] = email

        if id: 
            customer_properties['id'] = id

        params = {
            self.TOKEN: self.public_token,
            'event': event,
            'properties': properties,
            'customer_properties': customer_properties,
            'time': self._normalize_timestamp(timestamp),
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
            self.TOKEN: self.public_token,
            'properties': properties,
        }, is_test)

        return self._pubic_request(self.IDENTIFY, query_string)
