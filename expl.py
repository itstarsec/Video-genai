import requests
import json

# URL của API mà bạn đã tạo
url = "http://localhost:5000/detect"

# Địa chỉ RTSP bạn muốn kiểm tra
data = {
    "rtsp_url": "rtsp://192.168.1.222/1.mp4"
}

# Gửi yêu cầu POST
response = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))

# Kiểm tra phản hồi
if response.status_code == 200:
    result = response.json()
    print(f"Phát hiện người: {result['has_person']}")
else:
    print(f"Có lỗi xảy ra: {response.status_code} - {response.text}")