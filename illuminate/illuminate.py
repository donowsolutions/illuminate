from __future__ import absolute_import, division, print_function, unicode_literals

import json
import requests
from requests.compat import urljoin
from requests.exceptions import RequestException
from rauth import OAuth1Session
try:
    from exceptions import ConnectionError
except ImportError:
    class ConnectionError(OSError):
        pass

import logging
logger = logging.getLogger(__name__)


# API details
ILLUMINATE_URL_TEMPLATE = 'https://{}.illuminateed.com/{}/rest_server.php/Api/'

class Illuminate(object):
    """A client for a specific Illuminate instance

    """

    def __init__(self, subdomain, instance, consumer_key, consumer_secret, access_token, access_token_secret, user_agent=None):
        """


        """
        self.base_url = ILLUMINATE_URL_TEMPLATE.format(subdomain, instance)
        self.session = self._establish_session(consumer_key, consumer_secret, access_token, access_token_secret, user_agent=user_agent)

        self.sites = self.get_sites()
        self.district = self._determine_district()

        logger.debug('Illuminate client initialized for %s!', self.district)

    def _establish_session(self, consumer_key, consumer_secret, access_token, access_token_secret, user_agent):
        """

        """

        headers = {}
        if user_agent:
            headers['User-Agent'] = user_agent

        session = OAuth1Session(
            consumer_key=consumer_key,
            consumer_secret=consumer_secret,
            access_token=access_token,
            access_token_secret=access_token_secret,
        )
        session.headers.update(headers)
        logger.debug('Oauth1 session initialized.')

        return session

    def _determine_district(self):
        districts = [site['site_name'] for site in self.sites if site['site_type_name'] == 'DISTRICT' or site['site_id'] == '9999999']
        if len(districts) == 1:
            district = districts[0]
        elif len(districts) < 1:
            logger.warn('No districts found.  Haven\'t encountered this in the wild yet.')
            district = 'UNKNOWN'
        else:
            logger.warn('More than one district found: %s.  Haven\'t encountered this in the wild yet', districts)
            district = ', '.join(districts)
        return district


    def _get(self, relative_url, *args, **kwargs):
        """Issue base GET request to PS API."""

        for arg in args:
            relative_url += '/{}'.format(arg)

        url = urljoin(self.base_url, relative_url)
        logger.debug('Hitting url: %s with params: %s', url, kwargs)

        try:
            response = self.session.get(url, header_auth=True, params=kwargs)
        except requests.ConnectionError:
            raise ConnectionError('Unable to connect to %s - are you sure the subdomain is correct?' % self.base_url)

        try:
            response.raise_for_status()
        except requests.HTTPError as e:
            if response.status_code == 401:
                raise ConnectionError('Unable to authenticate - are you sure the API key is correct?')
            elif response.status_code == 404:
                raise ConnectionError('No such resource %s - are you sure the endpoints were configured correctly?' % relative_url)
            else:
                raise(e)

        try:
            response_json = response.json()
        except ValueError:
            logger.exception('Response was not valid JSON!')
            return None

        if isinstance(response_json, list):
            logger.debug('Returning %d results.', len(response_json))
            return response_json
        elif isinstance(response_json, dict):
            if 'num_pages' in response_json and 'results' in response_json:
                num_pages = response_json['num_pages']
                page = response_json['page']
                num_results = response_json['num_results']
                results = response_json['results']
                assert page == 1 or page == kwargs['page']
                if num_pages <= 1 or page == num_pages:
                    logger.debug('Returning %d results.', num_results)
                    return results
                else:
                    page = response_json['page']
                    kwargs['page'] = page + 1
                    return results + self._get(relative_url, *args, **kwargs)
            else:
                raise ValueError('Unexpected response format from Illuminate: %s', response_json)

    def __getattr__(self, name):
        if name.startswith('get_'):
            target = name.partition('_')[-1]
            return lambda *args, **kwargs: self._get(snake_to_pascal(target), *args, **kwargs)
        else:
            return self.__getattribute__(name)



def snake_to_pascal(string):
    return ''.join(map(lambda s: s.capitalize(), string.split('_')))
