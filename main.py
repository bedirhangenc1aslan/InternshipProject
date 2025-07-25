# main.py dosyanızın tamamı

import cv2
from tqdm import tqdm
from Initialize import Initialize
from Run import ProcessFrame
from Video import VideoCreator , ImageCreator

def main():
    video_path = "/home/nyenice/Desktop/Project Hiearchy/sssssssssssss.mp4"
    output_video_path = "output_tracked_video.avi"
    time_series = 30
    image_creator = ImageCreator()

    image_creator.split_frames(video_path)
    video_creator = VideoCreator(video_path , output_video_path , image_creator)
    total_frames = video_creator.get_total_frames()

    initialize = Initialize(time_series=time_series)
    process_frame_handler = ProcessFrame(video_path , time_series , initialize)
    
    print(f"Video işleme ve çıktı oluşturma başlıyor. Toplam {total_frames} kare işlenecek.")
    
    for _ in tqdm(range(total_frames), desc="Video İşleniyor"):
        processed_data , last_processed_frame = process_frame_handler.process_frame()
        
        if processed_data is None: # Video bitti
            break

        frame_idx = processed_data
        
        # Güncellenmiş nesneleri al
        objects = process_frame_handler.get_objects()
        
        # İlgili kareyi diskten oku
        video_creator.add_frame_to_video(frame_idx , objects , frame = last_processed_frame)

    # --- Kapanış ---
    video_creator.release_video()
    print(f"\nİşlem tamamlandı. Sonuç videosu '{output_video_path}' olarak kaydedildi.")

if __name__ == '__main__':
    main()