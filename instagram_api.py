import logging

from instagrapi import Client

class InstagramAPI:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = Client()

    def login(self):
        try:
            self.client.login(self.username, self.password)
            logging.info('Logged in as "%s"', self.username)
            return True
        except Exception as e:
            logging.error("Failed to login: %s", e)
            return False

    def logout(self):
        try:
            self.client.logout()
            logging.info('Logged out from "%s"', self.username)
            return True
        except Exception as e:
            logging.error("Failed to logout: %s", e)
            return False

    def post(self, image_path, caption=""):
        try:
            self.client.photo_upload(image_path, caption)
            logging.info('Photo posted successfully')
        except Exception as e:
            logging.error("Failed to post photo: %s", e)
            raise e