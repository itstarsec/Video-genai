import cv2
import numpy as np
import random
from scipy.spatial import Delaunay

# Load model MobileNetSSD
net = cv2.dnn.readNetFromCaffe("MobileNetSSD_deploy.prototxt", "MobileNetSSD_deploy.caffemodel")
CONFIDENCE_THRESHOLD = 0.5  # Ngưỡng nhận diện

# Tạo ID ngẫu nhiên
def generate_id():
    viet_words_en = [
        # Culture & Heritage
        "folk songs", "quan ho", "heritage", "tradition", "craftsmanship", "pagoda", "temple", "festival",         "legend", "history", "ancestor", "ritual", "spiritual", "sacred", "ceremony", "procession", "worship",         "folklore", "traditional art", "chanting", "calligraphy", "poetry", "silk weaving", "lacquer painting",         "incense village", "wood carving", "historical relics", "dynasty", "ancient town", "bronze drum", "dragon dance",         "lion dance", "folk tales", "storytelling", "mythology", "sacred site", "shrine", "ancestral altar", "meditation",         "devotion", "zen", "harmony", "bamboo flute", "folklore performance", "traditional costume", "embroidered silk",         "folk poetry", "cultural treasure", "Buddhist chanting", "spiritual journey", "ancient temple", "artistic heritage",         "handicraft village", "century-old tradition", "performing arts", "ancestral wisdom", "serenity", "divine energy",         "sacred relics", "temple festival", "village ceremony", "blessings", "harmony with nature", "cultural pride", "sacred harmony", "pho", "bun dau mam tom", "nem ran", "cha ca", "banh cuon", "banh khuc", "banh te", "banh phu the", "che lam",         "keo lac", "ruou lang van", "grilled pork", "rice wine", "sticky rice cake", "vermicelli", "fermented shrimp paste",         "pork roll", "pickled vegetables", "coconut candy", "rice noodle soup", "crispy spring rolls", "traditional tea",         "peanut candy", "mung bean cake", "steamed rice cake", "green bean cake", "fermented rice", "herbal tea", "sticky rice",         "fresh herbs", "fish sauce", "dipping sauce", "char-grilled meat", "street food", "local delicacy", "culinary tradition",         "handmade sweets", "traditional confectionery", "coconut treats", "aromatic spices", "roasted duck", "steamed fish",         "authentic flavors", "specialty dish", "organic farming", "fresh ingredients", "tea plantation", "honeycomb cake",         "crispy rice paper", "family recipes", "hand-ground spices", "traditional flavors", "countryside cuisine", "green fields", "riverbank", "countryside", "mountain view", "sunset", "sunrise", "peaceful scenery", "lotus pond",         "bamboo forest", "tea garden", "ancient village", "breathtaking landscape", "natural wonder", "scenic route",         "boat ride", "eco-tourism", "rural charm", "tranquil nature", "countryside retreat", "golden rice fields", "wildlife",         "hidden paradise", "off-the-beaten-path", "cultural exploration", "village life", "stilt house", "traditional homestay",         "heritage tour", "silk village", "lake view", "panoramic view", "countryside cycling", "local market", "river cruise",         "floating village", "lush greenery", "peaceful retreat", "rustic charm", "village trekking", "ancient well", "stone bridge",         "cave exploration", "traditional fishing", "spiritual journey", "stargazing", "night market", "cultural immersion",         "local experiences", "hidden gem", "sustainable tourism", "rural adventure", "eco-friendly travel", "timeless beauty",         "harmony with nature", "lim festival", "spring festival", "temple festival", "full moon festival", "traditional games", "kite flying", "boat racing",         "dragon boat festival", "fire dance", "folk performance", "cultural parade", "flower festival", "ancestral celebration",         "new year festival", "incense offering", "pilgrimage", "moon worship", "village feast", "music festival", "folk dance",         "paper lanterns", "lantern festival", "poetry recitation", "theatrical performance", "Buddhist festival", "dragon procession",         "lion dance", "vibrant colors", "festive spirit", "annual gathering", "fireworks", "carnival", "joyous occasion",         "harvest festival", "traditional attire", "sacred rituals", "cultural vibrancy", "storytelling nights", "temple fair",         "calligraphy contest", "folk instrument performance", "spirit summoning", "prayers and blessings", "incense smoke",         "chanting monks", "family gathering", "ethnic harmony", "religious harmony", "traditional competition",         "martial arts demonstration", "prayer ceremonies", "ceramic village", "pottery", "silk weaving", "bronze casting", "wood carving", "lacquerware", "embroidery", "bamboo crafts", "paper-making", "conical hat", "woven mats", "traditional mask", "handcrafted jewelry", "artistic pottery", "clay sculptures", "silk embroidery", "fine craftsmanship", "mosaic art", "shell inlay", "silverwork", "handmade furniture", "incense making", "traditional drum", "decorative lanterns", "folk painting", "handcrafted accessories", "beadwork", "vintage artistry","folk craftsmanship", "rattan weaving", "handmade dolls", "basket weaving", "natural dyes", "cultural artifacts","traditional stencils", "stone carving", "handmade souvenirs", "calligraphic art", "aged pottery", "paper crafts","ancient techniques", "ancestral skills", "handmade artistry", "folk-inspired creations", "artisanal heritage", "authentic craftsmanship", "hospitality", "warm smiles", "friendly locals", "hardworking people", "artisan community", "family traditions", "rural lifestyle",         "humble beginnings", "deep-rooted culture", "hardworking farmers", "creative minds", "inspiring artists", "dedicated craftsmen","resilient spirit", "harmonious community", "traditional wisdom", "family bonds", "ancestral respect", "deep connections","simple joys", "vibrant personalities", "kindness", "respect for heritage", "passionate souls", "vibrant storytellers",         "enthusiastic dancers", "skilled musicians", "inspiring teachers", "devoted artisans", "lifelong friendships", "shared experiences",         "cultural pride", "spiritual seekers", "loyal friends", "open-hearted generosity", "treasured traditions", "sincere hearts"
    ]
    return random.choice(viet_words_en)
    # return str(random.randint(1000, 9999))

# Hàm lọc object nằm trong vùng phát hiện người
def filter_objects_in_person_area(objects, persons):
    filtered_objects = []
    filtered_ids = []
    
    for (ox, oy), obj_id in objects:
        for (px, py, pw, ph) in persons:
            if px <= ox <= px + pw and py <= oy <= py + ph:
                filtered_objects.append((ox, oy))
                filtered_ids.append(obj_id)
                break  # Chỉ cần kiểm tra với 1 người là đủ
    
    return filtered_objects, filtered_ids

# Vẽ lưới Delaunay
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

# Vẽ ID object với phong cách MS-DOS (chữ trắng, nhỏ, đơn giản)
def draw_object_ids(frame, object_centers, object_ids):
    for (x, y), obj_id in zip(object_centers, object_ids):
        cv2.putText(frame, obj_id, (x, y), 
                    cv2.FONT_HERSHEY_PLAIN, 0.5, (255, 255, 255), 1, cv2.LINE_AA)  
                    

# Nhận diện người với MobileNetSSD
def detect_persons(frame):
    height, width = frame.shape[:2]
    blob = cv2.dnn.blobFromImage(frame, 0.007843, (300, 300), 127.5)
    net.setInput(blob)
    detections = net.forward()

    persons = []

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]
        class_id = int(detections[0, 0, i, 1])

        if confidence > CONFIDENCE_THRESHOLD and class_id == 15:  # Lớp 15 là "person"
            box = detections[0, 0, i, 3:7] * np.array([width, height, width, height])
            (x, y, x_max, y_max) = box.astype("int")
            persons.append((x, y, x_max - x, y_max - y))

    return persons

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

        persons = detect_persons(frame)

        object_ids = []
        object_centers = []

        # Duyệt qua danh sách object hiện tại (trích từ ảnh xám)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            M = cv2.moments(contour)
            if M["m00"] != 0:
                x = int(M["m10"] / M["m00"])
                y = int(M["m01"] / M["m00"])
                object_centers.append((x, y))
                object_ids.append(generate_id())

        # Lọc các object chỉ trong vùng người
        object_centers, object_ids = filter_objects_in_person_area(zip(object_centers, object_ids), persons)

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
