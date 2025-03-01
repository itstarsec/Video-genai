import cv2
import numpy as np
import random
from scipy.spatial import Delaunay
import random

# Tạo ID ngẫu nhiên
def generate_id():
    return str(random.randint(1000, 9999))

# Vẽ vector Delaunay với hiệu ứng tia sét
def draw_vectors(frame, object_centers, overlay):
    if len(object_centers) < 4:
        print("Không đủ điểm để tạo lưới Delaunay")
        return frame

    try:
        object_centers = np.array(object_centers, dtype=np.float32)
        tri = Delaunay(object_centers)

        for simplex in tri.simplices:
            pts = object_centers[simplex]
            for i in range(3):
                p1, p2 = pts[i], pts[(i+1) % 3]
                cv2.line(overlay, tuple(map(int, p1)), tuple(map(int, p2)), (255, 255, 255), 1)
    except Exception as e:
        print(f"Lỗi Delaunay: {e}")
    
    return frame

# Vẽ ID object
# def draw_object_ids(frame, object_centers, object_ids):
    # for (x, y), obj_id in zip(object_centers, object_ids):
        # text_size, _ = cv2.getTextSize(obj_id, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 2)
        # text_w, text_h = text_size
        # cv2.rectangle(frame, (x - text_w//2 - 5, y - text_h//2 - 5), (x + text_w//2 + 5, y + text_h//2 + 5), (255, 255, 255), -1)
        # cv2.putText(frame, obj_id, (x - text_w//2, y + text_h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
        
# Vẽ ID object với chữ nhỏ, mỏng và nền trắng rõ hơn
# def draw_object_ids(frame, object_centers, object_ids):
    # for (x, y), obj_id in zip(object_centers, object_ids):
        # text_size, _ = cv2.getTextSize(obj_id, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)  # Chữ nhỏ hơn, mỏng hơn
        # text_w, text_h = text_size
        # cv2.rectangle(frame, (x - text_w//2 - 4, y - text_h//2 - 4), (x + text_w//2 + 4, y + text_h//2 + 4), (255, 255, 255), cv2.FILLED)  # Nền trắng đậm hơn
        # cv2.putText(frame, obj_id, (x - text_w//2, y + text_h//2), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)  # Chữ đen, mỏng hơn
# Hàm sinh màu ngẫu nhiên
def random_color():
    return (random.randint(100, 255), random.randint(100, 255), random.randint(100, 255))  # Màu sáng hơn

# Vẽ ID object với màu nền ngẫu nhiên
def draw_object_ids(frame, object_centers, object_ids):
    color_map = {}  # Lưu màu của từng ID
    for (x, y), obj_id in zip(object_centers, object_ids):
        if obj_id not in color_map:
            color_map[obj_id] = random_color()  # Gán màu nếu chưa có
        
        text_size, _ = cv2.getTextSize(obj_id, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)  # Chữ nhỏ hơn, mỏng hơn
        text_w, text_h = text_size
        bg_color = color_map[obj_id]  # Lấy màu của object

        # Vẽ hình chữ nhật nền
        cv2.rectangle(frame, (x - text_w//2 - 4, y - text_h//2 - 4), 
                      (x + text_w//2 + 4, y + text_h//2 + 4), bg_color, cv2.FILLED)

        # Vẽ chữ ID
        cv2.putText(frame, obj_id, (x - text_w//2, y + text_h//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 0), 1)  # Chữ đen, mỏng hơn

# Xử lý video
def process_video(input_path, output_path):
    cap = cv2.VideoCapture(input_path)
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    
    out = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        overlay = frame.copy()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        object_ids = []
        object_centers = []

        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
                object_centers.append((x, y))
                object_ids.append(generate_id())

        frame = draw_vectors(frame, object_centers, overlay)
        draw_object_ids(frame, object_centers, object_ids)

        frame = cv2.addWeighted(overlay, 0.6, frame, 0.4, 0)

        out.write(frame)
        cv2.imshow('Processed Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Chạy xử lý video
process_video("input.mp4", "output.mp4")