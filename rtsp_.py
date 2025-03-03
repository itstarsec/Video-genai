from flask import Flask, jsonify, request
import cv2
import numpy as np

# Khởi tạo Flask
app = Flask(__name__)

# Load model MobileNetSSD
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")
CONFIDENCE_THRESHOLD = 0.5  # Ngưỡng nhận diện

# Nhận diện người
def detect_persons(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        class_id = int(detections[0, 0, i, 1])

        if confidence > CONFIDENCE_THRESHOLD and class_id == 15:  # Lớp 15 là "person"
            return True  # Phát hiện người

    return False  # Không phát hiện người

# Tạo API
@app.route('/detect', methods=['POST'])
def detect():
    data = request.json
    rtsp_url = data.get('rtsp_url')

    # Khởi tạo video capture từ RTSP
    cap = cv2.VideoCapture(rtsp_url)

    if not cap.isOpened():
        return jsonify({'error': 'Không thể mở luồng RTSP'}), 400

    has_person = False
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if detect_persons(frame):
            has_person = True
            break

    cap.release()

    return jsonify({'has_person': 1 if has_person else 0})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)