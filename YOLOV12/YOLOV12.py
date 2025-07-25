from ultralytics import YOLO
from pathlib import Path
class YOLOV12:
    def __init__(self):
        model_path = Path(__file__).parent / 'best.pt'
        self.model = YOLO(str(model_path))
    
    def predict_video(self , VIDEO_PATH):
        results_generator = self.model.track(source=VIDEO_PATH, show=False, tracker='bytetrack.yaml', conf=0.5, iou=0.3, stream=True, persist=True, verbose=False)
        return results_generator


    def predict_image(self, IMAGE_PATH ,CONFIDENCE_THRESHOLD = 0.5):
        results = self.model(IMAGE_PATH, verbose=False)

        first_result = results[0]
        class_names = first_result.names
        detections_list = []

        # Her bir tespit (bounding box) için bilgileri alalım
        for i, box in enumerate(first_result.boxes):
            # Güven skorunu al
            confidence = box.conf[0].item()

            # Sadece belirlenen eşik değerinin üzerindeki tespitleri işle
            if confidence >= CONFIDENCE_THRESHOLD:

                # Sınıf ID'sini al (örn: 0, 1, 2, ...)
                class_id = int(box.cls[0].item())

                # Sınıf adını al (örn: 'person', 'car', ...)
                class_name = class_names[class_id]

                # Sınırlayıcı kutunun koordinatlarını al (x1, y1, x2, y2 formatında)
                # .tolist() ile tensörü standart bir Python listesine çeviriyoruz.
                coordinates = box.xyxy[0].tolist()

                detections_list.append({
                    "class_name": class_name,
                    "class_id": class_id,
                    "confidence": confidence,
                    "coordinates": coordinates
                })
        return detections_list
