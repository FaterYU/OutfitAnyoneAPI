import urllib3
from urllib3 import PoolManager
from urllib3.filepost import encode_multipart_formdata
import random
import string
import json

urllib3.disable_warnings()  # 关闭SSL警告

http = PoolManager()


def createId():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=13))


def uploadImage(image_data, image_id):
    uploadUrl = "https://humanaigc-outfitanyone.hf.space/upload?upload_id="

    # 构建请求body
    boundary = '----WebKitFormBoundaryGYIaXS3xDCtcKfzH'
    fields = [
        ('files', ('sample.jpg', image_data, 'image/png'))
    ]

    # 编码multipart/form-data格式的数据
    body, headers_content_type = encode_multipart_formdata(
        fields, boundary=boundary)

    # 构建请求头
    headers = {
        'Content-Type': headers_content_type,
        'User-Agent': 'OutfitAnyone/1.0.0 (com.humanaigc.outfitanyone; build:1; iOS 14.4.2) Alamofire/5.2.2',
        'Accept': '*/*',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip;q=1.0, compress;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'humanaigc-outfitanyone.hf.space',
        'Content-Length': str(len(body))
    }

    # 发送请求
    response = http.request('POST', uploadUrl + image_id,
                            body=body, headers=headers)
    return response.data.decode('utf-8')[2:-2]


def WaitEvent(session_hash):
    queueUrl = "https://humanaigc-outfitanyone.hf.space/queue/data?session_hash="
    response = http.request(
        'GET', queueUrl + session_hash, preload_content=False)

    for chunk in response.stream():
        data = chunk.decode('utf-8')[6:-1]
        json_data = json.loads(data)
        print(json_data['msg']+"...")
        if json_data['msg'] == 'estimation':
            print("wait rank: "+str(json_data['rank']
                                    ) + "/"+str(json_data['queue_size']))
        elif json_data['msg'] == 'process_completed':
            if json_data['success'] == False:
                print("failed")
                return json_data['output']['error']
            else:
                return "https://humanaigc-outfitanyone.hf.space/file="+json_data['output']['data'][0]['path']


def run(session_hash, image1_srv, image2_srv, image1_size, image2_size):
    runUrl = "https://humanaigc-outfitanyone.hf.space/queue/join?"
    body = {
        "data": [
            {
                "path": "/tmp/gradio/28dbd2deba1e160bfadffbc3675ba4dcac20ca58/Eva_0.png",
                "url": "ttps://humanaigc-outfitanyone.hf.space/file=/tmp/gradio/28dbd2deba1e160bfadffbc3675ba4dcac20ca58/Eva_0.png",
                "meta": {
                    "_type": "gradio.FileData",
                },
                "size": None,
                "mime_type": None,
                "orig_name": "Eva_0.png",
            },
            {
                "path": image1_srv,
                "url": "https://humanaigc-outfitanyone.hf.space/file=" + image1_srv,
                "meta": {
                    "_type": "gradio.FileData",
                },
                "size": image1_size,
                "mime_type": "",
                "orig_name": "sample.jpg",
            },
            {
                "path": image2_srv,
                "url": "https://humanaigc-outfitanyone.hf.space/file=" + image2_srv,
                "meta": {
                    "_type": "gradio.FileData",
                },
                "size": image2_size,
                "mime_type": "",
                "orig_name": "sample.jpg",
            }
        ],
        "event_data": None,
        "fn_index": 3,
        "session_hash": session_hash,
        "trigger_id": 13
    }
    headers = {
        'Content-Type': 'application/json',
        'User-Agent': 'OutfitAnyone/1.0.0 (com.humanaigc.outfitanyone; build:1; iOS 14.4.2) Alamofire/5.2.2',
        'Accept': '*/*',
        'Accept-Language': 'zh-Hans-CN;q=1',
        'Accept-Encoding': 'gzip;q=1.0, compress;q=0.5',
        'Connection': 'keep-alive',
        'Host': 'humanaigc-outfitanyone.hf.space',
    }
    response = http.request('POST', runUrl, headers=headers,
                            body=str(body).replace('None', 'null').replace("'", '"'))
    return response.data.decode('utf-8')


def getResult(url):
    response = http.request('GET', url, preload_content=False)
    with open('./output/result.jpg', 'wb') as out:
        while True:
            data = response.read(1024)
            if not data:
                break
            out.write(data)


def main():
    # 图片文件路径
    image1_path = './input/image1.jpg'
    image2_path = './input/image2.jpg'
    image1_id = createId()
    image2_id = createId()
    image1_data = None
    image2_data = None

    # 读取图片文件
    with open(image1_path, 'rb') as f:
        image1_data = f.read()
    with open(image2_path, 'rb') as f:
        image2_data = f.read()

    image1_size = len(image1_data)
    image2_size = len(image2_data)

    # 上传图片
    image1_srv = uploadImage(image1_data, image1_id)
    image2_srv = uploadImage(image2_data, image2_id)

    session_hash = createId()

    run(session_hash,
        image1_srv, image2_srv, image1_size, image2_size)

    result_url = WaitEvent(session_hash)

    getResult(result_url)


if __name__ == "__main__":
    main()
