import requests
import urllib3
import os
from pathvalidate import sanitize_filepath
from pathlib import Path
import random
import os
from dotenv import load_dotenv


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_comic_path(path, payloads = None):
    response = requests.get(path, params=payloads,  verify=False)
    response.raise_for_status()
    comics_text = response.json()
    comic_path = comics_text['img']
    comment_path = comics_text['alt']
    return comic_path, comment_path
    
def get_image(image_url, payloads = None):
    response = requests.get(image_url, params=payloads,  verify=False)
    response.raise_for_status()
    return response


def download_images(image_url, save_path, image_name):
    os.makedirs(Path('.',save_path), exist_ok=True)
    filename = sanitize_filepath(os.path.join(save_path, f'{image_name}'))
    with open(filename, 'wb') as file:
        file.write(get_image(image_url).content)


def get_server_link(token, group_id): 
    path = 'https://api.vk.com/method/photos.getWallUploadServer'
    payloads = {
        'group_id': group_id,
        'extended': 1,
        'count': 3,
        'v': 5.154,
        'access_token': token,
    }
    response = requests.get(path, params=payloads,  verify=False)
    response.raise_for_status()
    server_answer = response.json()

    return server_answer['response']['upload_url']


def upload_photo_to_server_VK(file_link, token, group_id):
    path = get_server_link(token, group_id)
    with open(file_link, 'rb') as file:
        files = {
            'photo': file,
        }
        response = requests.post(path, files=files)
        response.raise_for_status()
    return response.json()


def safe_photo_in_album(server_photo_link, hash, token, group_id):
    path = 'https://api.vk.com/method/photos.saveWallPhoto'
    payloads = {
        'access_token': token,
        'group_id': group_id,
        'photo':  server_photo_link,
        'hash': hash, 
        'v': 5.154,       
    }
    response = requests.post(path, data=payloads)
    response.raise_for_status()
    return response.json()


def publish_photo_on_the_VK_wall(token, group_id, photo_owner_id, id, num):
    path = 'https://api.vk.com/method/wall.post'
    payloads = {
        'access_token': token,
        'owner_id': -group_id,
        'from_group': 1,
        'message': get_comic_path(f'https://xkcd.com/{num}/info.0.json')[1],
        'attachments': f'photo{photo_owner_id}_{id}',
        'v': 5.154, 
    }
    response = requests.post(path, data=payloads)
    response.raise_for_status()
    return response.json()



def main():
    load_dotenv()
    VK_token = os.environ['ACCESS_TOKEN']
    group_ID = os.environ['GROUP_ID']
    num = random.randint(1,2842)
    download_images(get_comic_path(f'https://xkcd.com/{num}/info.0.json')[0], 'comics', f'comic{num}.png')
    server_answer = upload_photo_to_server_VK(f'comics/comic{num}.png', VK_token, group_ID)
    VK_answer = safe_photo_in_album(server_answer['photo'], server_answer['hash'], VK_token, group_ID)
    publish_photo_on_the_VK_wall(VK_token, group_ID, VK_answer['owner_id'], VK_answer['id'], num)
    os.remove(f'comics/comic{num}.png')


if __name__ == '__main__':
    main()

