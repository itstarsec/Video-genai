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
        "yoga", "asana", "meditation", "breathing", "posture", "balance", "stretch", "flexibility",
        "pose", "mindfulness", "awareness", "energy", "chakra", "pranayama", "focus", "peace",
        "calm", "harmony", "relaxation", "flow", "movement", "core", "strength", "wellness",
        "spirituality", "concentration", "breath", "mantra", "serenity", "alignment", "health",
        "body", "soul", "mind", "detox", "vinyasa", "hatha", "kundalini", "restoration", "healing",
        "connection", "meditative", "grounding", "rejuvenation", "stillness", "zen", "self-care",
        "yogi", "yogini", "practice", "discipline", "self-awareness", "balance", "inner peace",
        "holistic", "natural", "therapy", "self-love", "gratitude", "positivity", "equanimity",
        "lightness", "openness", "compassion", "kindness", "transcendence", "self-discovery",
        "growth", "awakening", "purity", "simplicity", "intention", "reflection", "silence",
        "contentment", "acceptance", "forgiveness", "patience", "letting go", "healing energy",
        "prayer", "devotion", "spiritual growth", "trust", "clarity", "cosmic", "energy flow",
        "high vibrations", "soulful", "enlightenment", "nirvana", "sacred", "divine", "consciousness",
        "higher self", "universe", "surrender", "non-attachment", "mind-body connection",
        "inner strength", "self-discipline", "introspection", "deep breathing", "heart opening",
        "compassionate", "gentle movement", "emotional balance", "stress relief", "positive mindset",
        "mental clarity", "detachment", "liberation", "duality", "santosha", "dhyana", "pratyahara",
        "samadhi", "shavasana", "tadasana", "downward dog", "child’s pose", "warrior pose",
        "sun salutation", "yin yoga", "restorative yoga", "chair yoga", "power yoga", "hot yoga",
        "yoga nidra", "yogic diet", "fasting", "herbal healing", "chakra balancing",
        "ayurveda", "holistic health", "detoxification", "mindful eating", "organic lifestyle",
        "raw foods", "plant-based", "herbal tea", "hydration", "essential oils", "aromatherapy",
        "crystals", "sound healing", "vibrations", "energy work", "qi", "acupuncture",
        "tai chi", "qigong", "reiki", "chakras", "sacral chakra", "solar plexus chakra",
        "heart chakra", "throat chakra", "third eye chakra", "crown chakra", "root chakra",
        "spine alignment", "backbends", "hip openers", "forward folds", "twists", "inversions",
        "headstand", "handstand", "shoulder stand", "lotus pose", "half lotus", "seated poses",
        "supine poses", "standing poses", "yoga philosophy", "eight limbs of yoga",
        "yama", "niyama", "asana", "pranayama", "pratyahara", "dharana", "dhyana",
        "samadhi", "bhakti yoga", "jnana yoga", "karma yoga", "raja yoga", "tantra yoga",
        "sound meditation", "om chanting", "bija mantras", "affirmations", "self-reflection",
        "inner guidance", "kundalini awakening", "self-transformation", "higher frequency",
        "spirit guides", "akashic records", "universal energy", "oneness", "divine love",
        "mindfulness meditation", "vipassana", "transcendental meditation", "zen meditation",
        "guided meditation", "breath awareness", "self-inquiry", "conscious breathing",
        "holotropic breathing", "alternate nostril breathing", "diaphragmatic breathing",
        "ocean breath", "ujjayi breath", "kapalabhati", "bhastrika", "sitali", "sithkari",
        "breath retention", "mala beads", "yoga mat", "meditation cushion", "incense",
        "sacred space", "altar", "sound bath", "gong bath", "tibetan singing bowls",
        "crystal healing", "reiki healing", "meridians", "aura cleansing", "vibrational healing",
        "light therapy", "color therapy", "herbal remedies", "homeopathy", "naturopathy",
        "detox water", "mindful movement", "body scan meditation", "chakra meditation",
        "yogic lifestyle", "yogic wisdom", "satsang", "kirtan", "devotional chanting",
        "monastic life", "asceticism", "prayer beads", "intuitive guidance", "soul journey",
        "self-acceptance", "self-healing", "healing frequencies", "celestial energy",
        "sacred geometry", "kundalini serpent", "tantric practices", "mantra repetition",
        "holistic well-being", "natural balance", "herbal tonics", "gut health",
        "mind-body-soul harmony", "sustainable living", "eco-friendly lifestyle",
        "veganism", "ethical living", "mindful parenting", "conscious relationships",
        "love and light", "positive affirmations", "subtle body", "life force energy",
        "nervous system regulation", "deep relaxation", "heart-centered living",
        "soul nourishment", "cosmic wisdom", "celestial bodies", "moon phases",
        "lunar energy", "solar energy", "universal flow", "serene mind",
        "conscious evolution", "spiritual leadership", "enlightened living",
        "embodied presence", "self-empowerment", "soul alignment", "soul expansion",
        "emotional intelligence", "unwavering peace", "higher states of consciousness",
        "sacred stillness", "being present", "existential awareness", "eternal truth",
        "universal oneness", "sacred breath", "higher vibration living",
        "intuitive wisdom", "deep surrender", "soulful living", "mindful breathing",
        "sacred devotion", "yogic bliss", "cosmic rhythm", "harmony with nature",
        "sacred silence", "infinite peace", "divine consciousness", "soul purpose",
        "soul tribe", "spiritual renewal", "universal flow", "vibrational alignment",
        "deep presence", "sacred connection", "cosmic consciousness", "soul retrieval",
        "energetic healing", "high-frequency living", "primal energy", "holistic movement",
        "sacred embodiment", "tantric wisdom", "soul evolution", "sacred living",
        "spiritual ascension", "divine energy", "soul awakening", "soul healing",
        "meditative state", "soul expansion", "sacred energy", "spiritual wholeness"
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

# Sinh màu nền đậm ngẫu nhiên
def random_dark_color():
    return (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))

# Vẽ ID object với màu nền đậm
def draw_object_ids(frame, object_centers, object_ids):
    color_map = {}  

    for (x, y), obj_id in zip(object_centers, object_ids):
        if obj_id not in color_map:
            color_map[obj_id] = random_dark_color()

        text_size, _ = cv2.getTextSize(obj_id, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
        text_w, text_h = text_size
        bg_color = color_map[obj_id]  

        cv2.rectangle(frame, (x - text_w//2 - 4, y - text_h//2 - 4),
                      (x + text_w//2 + 4, y + text_h//2 + 4), bg_color, cv2.FILLED)

        cv2.putText(frame, obj_id, (x - text_w//2, y + text_h//2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

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

        # Vẽ bounding box quanh người
        # for (x, y, w, h) in persons:
            # cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 0)

        out.write(frame)
        cv2.imshow('Processed Video', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Chạy xử lý video
process_video("input.mp4", "output.mp4")
