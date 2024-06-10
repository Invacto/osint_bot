import os
import requests


def download_image(image_url, save_path):
    try:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)

        response = requests.get(image_url)
        if response.status_code == 200:
            with open(save_path, 'wb') as image_file:
                image_file.write(response.content)
            print("Image downloaded successfully!")
        else:
            print("Failed to download image. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred while downloading the image:", str(e))
