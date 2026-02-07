import cv2
import numpy as np
import os
class img_processing():
    def __init__(self):
        self.img = None
        self.gray = None
        self.thresh = None
        self.countour = None
        self.data_frame = None

    def read_img(self, path):
        self.img = cv2.imread(path)
        self.img = self.img [:,:,::-1]
        return self.img 
    def img2gray(self):
        self.gray = cv2.cvtColor(self.img, cv2.COLOR_RGB2GRAY)
        return self.gray
    
    def detect_contour(self, path, thresh1, thresh2, check):
        self.read_img(path)
        self.img2gray()
        
        blur = cv2.GaussianBlur(self.gray,(5,5),0)
        
        if check == 1:
            fuc = cv2.THRESH_BINARY
        else:
            fuc = cv2.THRESH_BINARY_INV

        _, self.thresh = cv2.threshold(blur, thresh1, thresh2, fuc)
        # Tạo kernel (structuring element) - kích thước 3x3
        kernel = np.ones((3, 3), np.uint8)

        # Thực hiện erode
        erode = cv2.erode(self.thresh, kernel, iterations=1)
        
        # Tìm kiếm contour
        contours, _ = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Vẽ contour và vòng tròn bao quanh lên ảnh gốc
        self.countour = self.img.copy()
        number_countour = 0
        for i, contour in enumerate(contours):
            # Tìm vòng tròn bao quanh nhỏ nhất
            (x, y), radius = cv2.minEnclosingCircle(contour)
            d = radius * 2
            
            # Tính diện tích của contour và đường tròn
            area_contour = cv2.contourArea(contour)
            area_circle = np.pi * (radius ** 2)
            
            if (0.7 < area_contour / area_circle < 1.3) and d > 20:  # Độ chênh lệch nhỏ cho phép
                # Vẽ contour có hình dạng tròn
                center = (int(x), int(y))
                
                number_countour+=1 
                text = f'{number_countour}'
                self.countour= cv2.putText(self.countour, text, center, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
                #cv2.drawContours(contour_image, [contour], -1, (0, 255, 0), 2)  # Vẽ contour bằng màu xanh lá cây
                self.countour = cv2.circle(self.countour, (int(x), int(y)), int(radius), (0, 255, 0), 4)
        
        return self.img,self.gray,self.thresh,self.countour
    
    def detect_contour_cal_intensity(self, path, thresh1, check, max_diameter):
        self.read_img(path)
        self.img2gray()
        
        blur = cv2.GaussianBlur(self.gray,(5,5),0)
        
        if check == 1:
            fuc = cv2.THRESH_BINARY
        else:
            fuc = cv2.THRESH_BINARY_INV

        _, self.thresh = cv2.threshold(blur, thresh1, 255, fuc)
        # Tạo kernel (structuring element) - kích thước 3x3
        kernel = np.ones((3, 3), np.uint8)

        # Thực hiện erode
        erode = cv2.erode(self.thresh, kernel, iterations=1)
        
        # Tìm kiếm contour
        contours, _ = cv2.findContours(erode, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        img_height, img_width = img.shape[:2]  
        self.countour = img.copy()
        number_countour = 0
        
        for i, contour in enumerate(contours):
            # Tìm tâm của contour và bán kính
            (x, y), radius = cv2.minEnclosingCircle(contour)
            d = radius * 2
            # Tính diện tích của contour và đường tròn
            area_contour = cv2.contourArea(contour)
            area_circle = np.pi * (radius ** 2)

            # Kiểm tra xem contour có gần với hình tròn không
            if (0.7 < area_contour / area_circle < 1.3) and d > 100:  # Độ chênh lệch nhỏ cho phép
                # Vẽ contour có hình dạng tròn
                center = (int(x), int(y))
                    
                # Tính toán các điểm end1 và end2 cho đường kính lớn nhất
                end1 = (int(center[0] - max_diameter / 2), center[1])
                end2 = (int(center[0] + max_diameter / 2), center[1])
                
                number_countour+=1 
                text = f'{number_countour}'
                contour_image= cv2.putText(contour_image, text, center, cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 2)
                #cv2.drawContours(contour_image, [contour], -1, (0, 255, 0), 2)  # Vẽ contour bằng màu xanh lá cây
                contour_image = cv2.circle(contour_image, (int(x), int(y)), int(radius), (0, 255, 0), 4)
                
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
                cv2.line(contour_image, end1, end2, (0, 0, 255), 4)
                    
                #Lưu giá trị cường độ sáng trên đường kính
                diameter_pixel_values = []
                for px in range(end1[0], end2[0] + 1):
                    if end1[0] <= px <= end2[0] and cv2.pointPolygonTest(contour, (px, center[1]), False) >= 0:
                            diameter_pixel_values.append(self.gray[center[1], px])
                    else:
                        diameter_pixel_values.append(0)
                
                # 1 dòng code làm nên mùa xuân
                average_intensity = np.mean(diameter_pixel_values)
                
                filename = os.path.basename(self.path)
                # Lưu thông tin vào data_img
                self.data_frame.append({
                    'Filename': filename,
                    'Contour': number_countour,
                    'Center X': center[0],
                    'Center Y': center[1],
                    'Radius': radius,
                    'Diameter': radius * 2,
                    'Diameter Pixel Values': diameter_pixel_values,
                    'mean_intensity': average_intensity,
                    'Bounding Box X Center': bbox_x_center,
                    'Bounding Box Y Center': bbox_y_center,
                    'Bounding Box Width': bbox_width,
                    'Bounding Box Height': bbox_height,
                    
                })
                
            contour_image = cv2.cvtColor(contour_image, cv2.COLOR_BGR2RGB)
            # Lưu ảnh đã xử lý vào thư mục đích
            folder_process = os.path.join(os.getcwd(), "processing")
            destination_path = os.path.join(folder_process, filename)
            cv2.imwrite(destination_path, contour_image)