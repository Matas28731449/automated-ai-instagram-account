# This is a sample Python script.
import os
import logging
import time

from instagram_api import InstagramAPI


# Press ⌃F5 to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press F9 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%I:%M:%S',
    )

    username = os.environ['INSTAGRAM_USERNAME']
    password = os.environ['INSTAGRAM_PASSWORD']

    api = InstagramAPI(username, password)
    try:
        if api.login():
            image_path = os.path.join(os.getcwd(), 'images', 'sample.jpg')
            api.post(image_path, "wonderful day")
            time.sleep(30)
    except Exception as e:
        logging.error('Exception occurred during login: %s', e)
    finally:
        try:
            api.logout()
        except Exception as e:
            logging.error('Exception occurred during logout: %s', e)

    print_hi('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
