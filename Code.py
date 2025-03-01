import cv2
import numpy as np
import random
from scipy.spatial import Delaunay

# Tạo ID ngẫu nhiên
def generate_id():
    return str(random.randint(1000, 9999))

# Hàm giảm số lượng object nếu quá nhiều (tối đa `max_objects`)
def reduce_object_ids(object_centers, object_ids, max_objects=50):
    if len(object_centers) > max_objects:
        sampled_indices = random.sample(range(len(object_centers)), max_objects)
        object_centers = [object_centers[i] for i in sampled_indices]
        object_ids = [object_ids[i] for i in sampled_indices]
    return object_centers, object_ids

# Vẽ lưới Delaunay (nếu đủ điểm)
def draw_vectors(frame, object_centers):
    if len(object_centers) < 4:
        return frame
    
    try:
        object_centers = np.array(object_centers, dtype=np.float32)
        tri = Delaunay(object_centers)
        
        for simplex in tri.simplices:
            pts = object_centers[simplex]
            for i in range(3):
                p1, p2 = pts[i], pts[(i+1) % 3]
                cv2.line(frame, tuple(map(int, p1)), tuple(map(int, p2)), (255, 255, 255), 1)
    except Exception as e:
        print(f"Lỗi Delaunay: {e}")
    
    return frame

# Hàm sinh màu nền cực kỳ đậm nhưng ngẫu nhiên
def random_dark_color():
    return (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))  # Màu tối nhưng không đen tuyệt đối

# Vẽ ID object với màu nền đậm ngẫu nhiên
def draw_object_ids(frame, object_centers, object_ids):
    color_map = {}  # Lưu màu nền cho từng ID
    
    for (x, y), obj_id in zip(object_centers, object_ids):
        if obj_id not in color_map:
            color_map[obj_id] = random_dark_color()  # Gán màu nền nếu chưa có
        
        text_size, _ = cv2.getTextSize(obj_id, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)  # Chữ nhỏ, font mỏng
        text_w, text_h = text_size
        bg_color = color_map[obj_id]  # Lấy màu nền đã lưu
        
        # Vẽ nền hình chữ nhật đậm
        cv2.rectangle(frame, (x - text_w//2 - 4, y - text_h//2 - 4), 
                      (x + text_w//2 + 4, y + text_h//2 + 4), bg_color, cv2.FILLED)
        
        # Vẽ chữ ID (màu trắng, font mỏng, không in đậm)
        cv2.putText(frame, obj_id, (x - text_w//2, y + text_h//2), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

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

        # Giảm số lượng object nếu quá nhiều
        object_centers, object_ids = reduce_object_ids(object_centers, object_ids, max_objects=50)

        frame = draw_vectors(frame, object_centers)
        draw_object_ids(frame, object_centers, object_ids)

        out.write(frame)
        cv2.imshow('Processed Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Chạy xử lý video
process_video("input.mp4", "output.mp4")
