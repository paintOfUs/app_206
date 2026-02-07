import os
import re
import cv2
import numpy as np
import pandas as pd
import threading
import matplotlib.pyplot as plt
from PyQt6.QtCore import QThread, pyqtSignal

class ImageProcessingThread2(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame)
    
    def __init__(self, folder_path, df,ignore, max_d):
        super().__init__()
        self.folder_path = folder_path
        self.df = df
        self.ignore = ignore
        self.max_diameter = max_d
        self.data = None 
        
    # Hàm lấy phần số từ tên file để làm khóa sắp xếp
    @staticmethod
    def extract_number(filename):
        match = re.match(r"(\d+)", filename)  # Lấy chuỗi số ở đầu tên file
        return int(match.group()) if match else float('inf')  # Nếu không có số thì đặt giá trị cao để xếp sau


    def run(self):
        count = 0
        # Lấy danh sách file và sắp xếp theo thứ tự số từ thấp đến cao, giữ nguyên tên file cũ
        file_list = sorted(os.listdir(self.folder_path), key=self.extract_number)
        for filename in file_list:
            if self.ignore not in filename:
                continue
            contours_data = self.process_images(filename)
            if self.data is None:
                self.data = contours_data
            else:
                self.data = pd.concat([self.data, contours_data], ignore_index=True)
            self.progress.emit(count + 1)  # Emit progress signal
        self.finished.emit(self.data) 
    
    def process_images(self, filename):
        data_df3 = []
        if "_phatquang" in filename:
            base_name = filename.replace('_phatquang', '')
            rows = self.df[self.df['Filename'] == f'{base_name}']

            if not rows.empty:
                path = os.path.join(self.folder_path, filename)
                img = cv2.imread(path)
                img = img[:,:,::-1]
                gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
                new_img = img.copy()
                for index, row in rows.iterrows():
                    center_x = int(row['Center X'])
                    center_y = int(row['Center Y'])
                    radius = int(row['Radius'])

                    center = (center_x, center_y)
                    end1 = (center_x - self.max_diameter // 2, center_y)
                    end2 = (center_x + self.max_diameter // 2, center_y)

                    cv2.line(new_img, end1, end2, (255, 0, 0), 2)
                    cv2.circle(new_img, center, radius, (0, 255, 0), 2)

                    


                    # Lưu ảnh đã xử lý vào thư mục đích
                    folder_process = os.path.join(os.getcwd(), "processing_phatquang")
                    if not os.path.exists(folder_process):
                        os.makedirs(folder_process)
                    output = os.path.join(folder_process, filename)
                    cv2.imwrite(output, cv2.cvtColor(new_img, cv2.COLOR_RGB2BGR))

                    bien1 = center_x - radius
                    bien2 = center_x + radius
                    diameter_pixel_values = []
                    for px in range(end1[0], end2[0] + 1):
                        if end1[0] <= px <= end2[0] and  bien1<=px <= bien2:
                            diameter_pixel_values.append(gray[center[1], px])
                        else:
                            diameter_pixel_values.append(0)

                    
                    data_df3.append({
                            'Filename': filename,
                            'Center X': center_x,
                            'Center Y': center_y,
                            'Diameter Pixel Values': diameter_pixel_values,
                            'Mean Intensity': np.mean(diameter_pixel_values) if diameter_pixel_values else 0
                    })

        return pd.DataFrame(data_df3)  # Trả về DataFrame đã tạo
