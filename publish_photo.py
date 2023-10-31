import requests
import urllib3
import os
import sys
from pathvalidate import sanitize_filepath
from pathlib import Path
import random
import os
from dotenv import load_dotenv


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def download_random_comic(path, save_path, image_name, payloads = None):
    response = requests.get(path, params=payloads,  verify=False)
    response.raise_for_status()
    comics_text = response.json()
    comic_path = comics_text['img']
    filename = sanitize_filepath(os.path.join(save_path, f'{image_name}'))
    comic_response = requests.get(comic_path, params=payloads,  verify=False)
    comic_response.raise_for_status()
    with open(filename, 'wb') as file:
        file.write(comic_response.content)

    return comics_text
    


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


def save_photo_in_album(server_photo_link, server_answer_hash, token, group_id):
    path = 'https://api.vk.com/method/photos.saveWallPhoto'
    payloads = {
        'access_token': token,
        'group_id': group_id,
        'photo':  server_photo_link,
        'hash': server_answer_hash, 
        'v': 5.154,       
    }
    response = requests.post(path, data=payloads)
    response.raise_for_status()
    return response.json()


def publish_photo_on_the_VK_wall(token, group_id, photo_owner_id, id, message):
    path = 'https://api.vk.com/method/wall.post'
    payloads = {
        'access_token': token,
        'owner_id': -group_id,
        'from_group': 1,
        'message': message,
        'attachments': f'photo{photo_owner_id}_{id}',
        'v': 5.154, 
    }
    response = requests.post(path, data=payloads)
    response.raise_for_status()
    return response.json()



def main():
    load_dotenv()
    VK_TOKEN = os.environ['VK_ACCESS_TOKEN']
    GROUP_ID = os.environ['VK_GROUP_ID']
    last_comic_number = 2842
    num = random.randint(1, last_comic_number)
    os.makedirs(Path('.','comics'), exist_ok=True)
    try:
        comics_text = download_random_comic(f'https://xkcd.com/{num}/info.0.json', 'comics', f'comic{num}.png')
        server_answer = upload_photo_to_server_VK(Path('comics', 'comic{num}.png'), VK_TOKEN, GROUP_ID)
        vk_answer = save_photo_in_album(server_answer['photo'], server_answer['hash'], VK_TOKEN, GROUP_ID)
        publish_photo_on_the_VK_wall(VK_TOKEN, GROUP_ID, vk_answer['owner_id'], vk_answer['id'], num, comics_text['alt'])
        os.remove(Path('comics', 'comic{num}.png'))
    except requests.HTTPError:
        print('Страница не найдена', file=sys.stderr)
    finally:
        os.remove(Path('comics', 'comic{num}.png'))
        

if __name__ == '__main__':
    main()

