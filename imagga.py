import requests

class Imgga:
    def __init__(self):
        self.api_key = 'acc_836adfc4b3e3265'
        self.api_secret = 'a6374e4fdb36c6a61e717ccbe1b57df6'

    def upload_img(self, path):
        response = requests.post(
            'https://api.imagga.com/v2/uploads',
            auth=(self.api_key, self.api_secret),
            files={'image': open(f"{path}.png", 'rb')})
        data = response.json()
        # print("********", data)
        return data['result']['upload_id']

    def get_tags(self, uplaod_id):
        # print("*****************",uplaod_id)
        response = requests.get(
            f'https://api.imagga.com/v2/tags?image_upload_id={uplaod_id}',
            auth=(self.api_key, self.api_secret))
        data = response.json()
        # print("DATA:",  data)
        # print(response.status_code)
        return data['result']['tags']
