import re
from PyQt6.QtCore import QThread, pyqtSignal
import cv2
import numpy as np
import pandas as pd
import os

class ImageProcessingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(pd.DataFrame,  int)

    def __init__(self, folder_paths, thresh1, check, ignore, check_ignore):
        super().__init__()
        self.image_paths = folder_paths
        self.thresh1 = thresh1
        self.thresh2 = 255
        self.check = check
        self.max_diameter = 0
        self.ignore_image = ignore
        self.check_ignore = check_ignore
        self.data_frame = None
        
    # Hàm lấy phần số từ tên file để làm khóa sắp xếp
    @staticmethod
    def extract_number(filename):
        match = re.match(r"(\d+)", filename)  # Lấy chuỗi số ở đầu tên file
        return int(match.group()) if match else float('inf')
    
    def run(self):
        print("thư mục")
        count = 0
        # Lấy danh sách file và sắp xếp theo thứ tự số từ thấp đến cao, giữ nguyên tên file cũ
        file_list = sorted(os.listdir(self.image_paths), key=self.extract_number)
        for filename in file_list:
            print(filename)
            # bỏ qua file name có tên ignore
            if self.check_ignore == 1:
                if self.ignore_image  in filename:
                    continue
                print(filename)
                img = self.read_img(os.path.join(self.image_paths,filename))
                self.getmaxdiameter(img)
                self.progress.emit(count + 1)
            # bỏ qua file không có tên ignore
            elif self.check_ignore == 2:
                if self.ignore_image  not in filename:
                    continue
                print(filename)
                img = self.read_img(os.path.join(self.image_paths,filename))
                self.getmaxdiameter(img)
                self.progress.emit(count + 1)
        
        for filename in file_list:
            if self.check_ignore == 1:
                if self.ignore_image  in filename:
                    continue
            elif self.check_ignore == 2:
                if self.ignore_image  not in filename:
                    continue
            img = self.read_img(os.path.join(self.image_paths,filename))
            contours_data = self.detect_contours(img, filename)
            if self.data_frame is None:
                self.data_frame = contours_data
            else:
                self.data_frame = pd.concat([self.data_frame, contours_data], ignore_index=True)
            self.progress.emit(count + 1)  # Emit progress signal
        self.finished.emit(self.data_frame, self.max_diameter)  # Emit finished signal with data frame

    def read_img(self, path):
        img = cv2.imread(path)
        return img[:, :, ::-1]  # Convert BGR to RGB

    def getmaxdiameter(self, img):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        fuc = cv2.THRESH_BINARY if self.check == 1 else cv2.THRESH_BINARY_INV
        _, thresh = cv2.threshold(blur, self.thresh1, self.thresh2, fuc)
        
        # Tạo kernel (structuring element) - kích thước 3x3
        kernel = np.ones((3, 3), np.uint8)

        # Thực hiện erode
        erode = cv2.erode(thresh, kernel, iterations=1)
        
        contours, _ = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            (x, y), radius = cv2.minEnclosingCircle(contour)
            diameter = radius * 2
            # Tính diện tích của contour và đường tròn
            area_contour = cv2.contourArea(contour)
            area_circle = np.pi * (radius ** 2)

            # Kiểm tra xem contour có gần với hình tròn không
            if (0.7 < area_contour / area_circle < 1.3) and diameter >100:
                if diameter >= self.max_diameter:
                    self.max_diameter = diameter

    def detect_contours(self, img, filename):
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        
        fuc = cv2.THRESH_BINARY if self.check == 1 else cv2.THRESH_BINARY_INV
        _, thresh = cv2.threshold(blur, self.thresh1, self.thresh2, fuc)
        
        # Tạo kernel (structuring element) - kích thước 3x3
        kernel = np.ones((3, 3), np.uint8)

        # Thực hiện erode
        erode = cv2.erode(thresh, kernel, iterations=1)
        
        contours, _ = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        results = []
        
        img_height, img_width = img.shape[:2]  
        img_countour = img.copy()
        number_countour = 0

        for i, contour in enumerate(contours):
            # Tìm tâm của contour và bán kính
            (x, y), radius = cv2.minEnclosingCircle(contour)
            d = radius * 2
            # Tính diện tích của contour và đường tròn
            area_contour = cv2.contourArea(contour)
            area_circle = np.pi * (radius ** 2)
            
            # Kiểm tra xem contour có gần với hình tròn không
            if (0.7 < area_contour / area_circle < 1.3) and d > 50:  # Độ chênh lệch nhỏ cho phép
                # Vẽ contour có hình dạng tròn
                center = (int(x), int(y))
                    
                # Tính toán các điểm end1 và end2 cho đường kính lớn nhất
                end1 = (int(center[0] - self.max_diameter / 2), center[1])
                end2 = (int(center[0] + self.max_diameter / 2), center[1])
                
                number_countour+=1 
                text = f'{number_countour}'
                img_countour= cv2.putText(img_countour, text, center, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
                #cv2.drawContours(contour_image, [contour], -1, (0, 255, 0), 2)  # Vẽ contour bằng màu xanh lá cây
                img_countour = cv2.circle(img_countour, (int(x), int(y)), int(radius), (0, 255, 0), 4)
                
                # Tính toán hình chữ nhật bao quanh vòng tròn
                x_center = x / img_width
                y_center = y / img_height
                width = d / img_width
                height = d / img_height

                # Tính toán tọa độ góc trên bên trái của hình chữ nhật bao quanh
                x_min = (x - radius) / img_width
                y_min = (y - radius) / img_height
                x_max = (x + radius) / img_width
                y_max = (y + radius) / img_height

                # Tính toán tâm và kích thước của bounding box
                bbox_x_center = (x_min + x_max) / 2
                bbox_y_center = (y_min + y_max) / 2
                bbox_width = x_max - x_min
                bbox_height = y_max - y_min
                    
                # Vẽ đường kính lớn nhất lên contour
                cv2.line(img_countour, end1, end2, (0, 0, 255), 4)
                    
                #Lưu giá trị cường độ sáng trên đường kính
                diameter_pixel_values = []
                for px in range(end1[0], end2[0] + 1):
                    if end1[0] <= px <= end2[0] and cv2.pointPolygonTest(contour, (px, center[1]), False) >= 0:
                            diameter_pixel_values.append(gray[center[1], px])
                    else:
                        diameter_pixel_values.append(0)
                
                # 1 dòng code làm nên mùa xuân
                average_intensity = np.mean(diameter_pixel_values)
                
                results.append({
                    'Filename': filename,
                    'Contour': number_countour,
                    'Center X': center[0],
                    'Center Y': center[1],
                    'Radius': radius,
                    'Diameter': radius * 2,
                    'Diameter Pixel Values': diameter_pixel_values,
                    'Bounding Box X Center': bbox_x_center,
                    'Bounding Box Y Center': bbox_y_center,
                    'Bounding Box Width': bbox_width,
                    'Bounding Box Height': bbox_height,
                    'Mean Intensity': average_intensity
                })
        img_countour = cv2.cvtColor(img_countour, cv2.COLOR_BGR2RGB)
        # Lưu ảnh đã xử lý vào thư mục đích
        folder_process = os.path.join(os.getcwd(), "processing")
        if not os.path.exists(folder_process):
            os.makedirs(folder_process)
        destination_path = os.path.join(folder_process, filename)
        cv2.imwrite(destination_path, img_countour)
        return pd.DataFrame(results)
