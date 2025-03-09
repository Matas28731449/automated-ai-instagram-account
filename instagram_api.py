import requests
import logging
import time
import json
import uuid

class InstagramAPI:
    def __init__(self, username, password, session=None, max_entries=3):
        self.username = username
        self.password = password
        self.session = session or requests.Session()
        self.max_entries = max_entries

        self.session.headers.update({
            'User-Agent': ('Mozilla/5.0 Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/92.0.4515.107 Safari/537.36'),
            'Referer': 'https://www.instagram.com/',
        })
        self.csrf_token = None

    def _get_csrf_token(self):
        try:
            response = self.session.get('https://www.instagram.com/accounts/login/?next=/')
            response.raise_for_status()
        except requests.RequestException as e:
            logging.error(e)

        if 'csrftoken' in self.session.cookies:
            self.csrf_token = self.session.cookies['csrftoken']
            self.session.headers.update({'X-CSRFTOKEN': self.csrf_token})
            logging.debug('CSRF token retrieved: %s', self.csrf_token)
            return True
        else:
            logging.error('Failed to retrieve CSRF token')
            return False

    def login(self):
        if not self._get_csrf_token():
            raise Exception('Failed to retrieve CSRF token')

        login_url = 'https://www.instagram.com/accounts/login/ajax/'
        payload = {
            'username': self.username,
            'enc_password': f'#PWD_INSTAGRAM_BROWSER:0:{int(time.time())}:{self.password}',
            'queryParams': {},
            'optIntoOneTap': 'false'
        }

        for attempt in range(1, self.max_entries + 1):
            try:
                logging.info('Login attempt %d for user "%s"', attempt, self.username)
                response = self.session.post(login_url, data=payload, allow_redirects=True)
                response.raise_for_status()
                result = response.json()

                if result.get('authenticated'):
                    logging.info('Successfully logged in as "%s"', self.username)
                    return True
                else:
                    message = result.get('message', 'Unknown error')
                    logging.warning('Login attempt %d failed: %s', attempt, message)
            except requests.RequestException as e:
                logging.error('Network error during login attempt %d: %s', attempt, e)
            except json.JSONDecodeError as e:
                logging.error('Failed to decode JSON response: %s', e)

            time.sleep(2)

        raise Exception('Login failed after {} attempts'.format(self.max_entries))

    def logout(self):
        logout_url = 'https://www.instagram.com/accounts/logout/'
        payload = {
            'csrfmiddlewaretoken': self.csrf_token,
        }

        try:
            logging.info('Logging out user "%s"', self.username)
            response = self.session.post(logout_url, data=payload, allow_redirects=True)
            response.raise_for_status()

            if response.url == 'https://www.instagram.com/':
                logging.info('Successfully logged out user "%s"', self.username)
                return True
            else:
                logging.warning('Unexpected URL after logout: %s', response.url)
        except requests.RequestException as e:
            logging.error('Error during logout: %s', e)
        finally:
            self.session.close()
            self.session = None
            self.csrf_token = None

    def _upload_image(self, image_path):
        upload_id = str(uuid.uuid4())
        upload_url = 'https://i.instagram.com/api/v1/media/upload/photo/'

        try:
            with open(image_path, 'rb') as file:
                photo_data = file.read()
        except Exception as e:
            logging.error('Failed to read the image: %s', e)
            return None

        files = {
            'photo': ('photo.jpg', photo_data, 'application/octet-stream')
        }
        payload = {
            'upload_id': upload_id,
            'is_sidecar': 'false'
        }

        try:
            response = self.session.post(upload_url, data=payload, files=files)
            response.raise_for_status()
            result = response.json()

            if result.get('status') != 'ok':
                logging.error("Image upload failed: %s", result)
                return None
        except Exception as e:
            logging.error('Failed to upload the image: %s', e)
            return None

        return upload_id

    def _configure_image(self, upload_id, caption=""):
        config_url = 'https://i.instagram.com/api/v3/media/configure/'
        payload = {
            'upload_id': upload_id,
            'caption': caption,
            'usertags': json.dumps({'in': []}),
            'custom_accessibility_caption': '',
            'retry_timeout': ''
        }

        try:
            response = self.session.post(config_url, data=payload)
            response.raise_for_status()
            result = response.json()

            if result.get('status') == 'ok':
                logging.info('Successfully configured the image')
                return True
            else:
                logging.error('Failed to configure the image: %s', result)
                return False
        except Exception as e:
            logging.error('Exception during image configuration: %s', e)
            return False

    def post(self, image_path, caption=""):
        try:
            upload_id = self._upload_image(image_path)
            if upload_id:
                try:
                    self._configure_image(upload_id, caption)
                    logging.info('Image posted successfully')
                except Exception as e:
                    logging.error('Failed to post image: %s', e)
        except Exception as e:
            logging.error('Exception during image posting: %s', e)


