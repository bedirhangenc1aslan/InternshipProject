# main.py dosyanızın tamamı

import cv2
from tqdm import tqdm
from Initialize import Initialize
from Run import ProcessFrame
from Video import ImageCreator , VideoCreator
def main():
    video_path = "/home/nyenice/Desktop/Project Hiearchy/senaryo_48.mp4"
    output_video_path = "output_tracked_video.avi"
    time_series = 30
    image_creator = ImageCreator()
    video_creator = VideoCreator(output_video_path , image_creator)
    image_creator.split_frames(video_path)
    
    initialize = Initialize(time_series=time_series)
    process_frame_handler = ProcessFrame(video_path , time_series , initialize)
    total_frames = video_creator.get_total_frames()
    print(f"Video işleme ve çıktı oluşturma başlıyor. Toplam {total_frames} kare işlenecek.")
    
    # --- Ana İşleme Döngüsü (Orijinal haliyle) ---
    for _ in tqdm(range(total_frames), desc="Video İşleniyor"):
        # `process_frame` her çağrıldığında bir sonraki kareyi işler ve nesneleri günceller.
        processed_data = process_frame_handler.process_frame()
        
        if processed_data is None: # Video bitti
            break

        frame_idx = processed_data
        
        # Güncellenmiş nesneleri al
        objects = process_frame_handler.get_objects()

        video_creator.add_frame_to_video(frame_idx , objects)
        
    video_creator.release_video()

if __name__ == '__main__':
    main()