import sys
# pip install pyqt5
from PyQt6.QtWidgets import QApplication, QMainWindow, QFileDialog, QTableWidgetItem, QVBoxLayout, QMessageBox
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt
from testapp2 import Ui_MainWindow
from image_processing import *
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas  # Thay đổi import
from Thread import ImageProcessingThread
from Thread2 import ImageProcessingThread2
from PyQt6.QtWidgets import QMainWindow, QGraphicsScene
from PyQt6.QtGui import QPen
from PyQt6.QtCore import Qt
import math

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uic = Ui_MainWindow()
        self.uic.setupUi(self)
        self.process = img_processing()
        self.uic.tabWidget.tabBar().hide()
        self.gray_img = None
        self.check = 1
        self.checkbox = 1
        self.checkIgnore = 1
        self.path =None
        self.folder = None
        self.folder3 = None
        self.data_frame = None
        self.max_d = None
        self.uic.img_file.clicked.connect(self.getfile)
        for button in self.uic.buttonGroup.buttons():
            print(button.text()) 
            button.clicked.connect(self.change_page)
            
        self.uic.check1.setChecked(True)
        self.uic.checkbox1.setChecked(True)
        
        # Kết nối sự kiện stateChanged cho cả hai checkbox
        self.uic.check1.clicked.connect(self.on_checkbox1_clicked)
        self.uic.check2.clicked.connect(self.on_checkbox2_clicked)
        self.uic.histogram.clicked.connect(self.display_histogram_on_label)
        self.path = None
        # Kết nối tín hiệu của QSlider với slot
        self.uic.thresh1.valueChanged.connect(self.update_spin_box)
        # Kết nối tín hiệu của QSpinBox với slot để cập nhật QSlider
        self.uic.thresh1_data.valueChanged.connect(self.update_slider)
        
        ###page2
        #folder
        self.uic.folder.clicked.connect(self.openFolder)
        self.uic.checkbox1.clicked.connect(self.on_checkbox1)
        self.uic.checkbox2.clicked.connect(self.on_checkbox2)
        
        self.uic.run.clicked.connect(self.multiprocessing)
        
        # Kết nối tín hiệu của QSlider với slot
        self.uic.thresh1_2.valueChanged.connect(self.update_spin_box2)
        # Kết nối tín hiệu của QSpinBox với slot để cập nhật QSlider
        self.uic.thresh1_data_2.valueChanged.connect(self.update_slider2)
        
        self.uic.radiobtn1.setChecked(True)
        # Hàm sự kiện chỉ in thông báo khi radio button đó được chọn
        def on_button_toggled(button):
            if button.isChecked():
                if button == self.uic.radiobtn1:
                    self.checkIgnore = 1
                elif button == self.uic.radiobtn2:
                    self.checkIgnore = 2

        # Kết nối sự kiện với từng radio button
        self.uic.radiobtn1.toggled.connect(lambda checked: on_button_toggled(self.uic.radiobtn1))
        self.uic.radiobtn1.toggled.connect(lambda checked: on_button_toggled(self.uic.radiobtn2))
        
        # Gắn sự kiện cho nút ruler
        self.uic.btn_ruler.clicked.connect(self.open_ruler)

        # Biến cho OpenCV
        self.start_point = None
        self.drawing = False
        self.line_length = 0
        self.img_original = None
        
        
        ###page3
        self.uic.folder2.clicked.connect(self.openFolder2)
        self.uic.run2.clicked.connect(self.multiprocessing2)
    ###chuyển page
    def change_page(self):
        btn = self.uic.buttonGroup.sender()
        tab_index = self.uic.buttonGroup.buttons().index(btn)  # lấy ra chỉ số 
        self.uic.tabWidget.setCurrentIndex(tab_index)
        
    ###Page 1 __ start __
    #Chọn file
    def getfile(self):
        path,_ = QFileDialog.getOpenFileName(
            self,
            "Open File",
            "${HOME}",
            "All Files (*);; Python Files (*.py);; PNG Files (*.png)",
        )
        self.path = path
        print(self.uic.thresh1.value)
        
        img, gray, thresh, countour = self.process.detect_contour(path, self.uic.thresh1.value(),255, self.check)
        self.gray_img = gray
        self.numpy2pixmap(img,self.uic.img1)
        self.numpy2pixmap(gray,self.uic.img2)
        self.numpy2pixmap(thresh,self.uic.img3)
        self.numpy2pixmap(countour,self.uic.img4)
        
        
    #Chuyển ảnh sang dạng bitmap và thêm vào qlabel đúng tỉ lệ
    def numpy2pixmap(self, img, qlabel):
        if len(img.shape) == 2:  # Grayscale image
            h, w = img.shape
            image = QImage(img.data.tobytes(), w, h, w, QImage.Format.Format_Grayscale8)
        if len(img.shape) == 3:
            h,w,ch = img.shape
            print(h,w,ch)
            image = QImage(img.data.tobytes(), w, h, ch * w, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(image)
        pixmap = pixmap.scaled(qlabel.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
        qlabel.setPixmap(pixmap)
        qlabel.setScaledContents(False)
        
    def display_histogram_on_label(self):
        # Tính histogram
        histogram = cv2.calcHist([self.gray_img], [0], None, [256], [0, 256])

        # Tạo biểu đồ với matplotlib
        fig = Figure(figsize=(5, 3), dpi=100)
        ax = fig.add_subplot(111)

        # Vẽ histogram
        ax.plot(histogram, color='black')
        ax.set_title('Histogram of Image Brightness')
        ax.set_xlabel('Brightness Level')
        ax.set_ylabel('Frequency')
        ax.set_xlim([0, 255])

        # Sử dụng tight_layout để điều chỉnh các thành phần
        fig.tight_layout()
        
        # Tạo canvas từ figure
        canvas = FigureCanvas(fig)  # Sử dụng FigureCanvasQTAgg

        # Kiểm tra xem layout đã được thiết lập chưa
        if self.uic.img_hist.layout() is None:
            # Nếu layout chưa được thiết lập, tạo một layout mới
            self.uic.img_hist.setLayout(QVBoxLayout())

        # Làm sạch widget trước khi thêm biểu đồ mới
        layout = self.uic.img_hist.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:  # Kiểm tra xem widget có phải là None không
                widget.deleteLater()  # Xóa widget nếu nó không phải là None

        # Thêm canvas vào QWidget
        layout.addWidget(canvas)
        canvas.draw()  # Cập nhật canvas để hiển thị

    def update_spin_box(self, value):
        # Cập nhật giá trị của QSpinBox khi QSlider thay đổi
        if self.path is not None:
            img, gray, thresh, countour = self.process.detect_contour(self.path, self.uic.thresh1.value(),255, self.check)
            self.numpy2pixmap(thresh,self.uic.img3)
            self.numpy2pixmap(countour,self.uic.img4)
        self.uic.thresh1_data.setValue(value)

    def update_slider(self, value):
        # Cập nhật giá trị của QSlider khi QSpinBox thay đổi
        if self.path is not None:
            img, gray, thresh, countour = self.process.detect_contour(self.path, self.uic.thresh1.value(),255, self.check)
            self.numpy2pixmap(thresh,self.uic.img3)
            self.numpy2pixmap(countour,self.uic.img4)
        self.uic.thresh1.setValue(value)
        
    def on_checkbox1_clicked(self):
        if self.uic.check1.isChecked():
            self.check = 1
            self.uic.check2.setChecked(False)
            if self.path != None:
                img, gray, thresh, countour = self.process.detect_contour(self.path, self.uic.thresh1.value(),255, self.check)
                self.numpy2pixmap(thresh,self.uic.img3)
                self.numpy2pixmap(countour,self.uic.img4)

    def on_checkbox2_clicked(self):
        if self.uic.check2.isChecked():
            self.check = 2
            self.uic.check1.setChecked(False)
            if self.path != None:
                img, gray, thresh, countour = self.process.detect_contour(self.path, self.uic.thresh1.value(),255, self.check)
                self.numpy2pixmap(thresh,self.uic.img3)
                self.numpy2pixmap(countour,self.uic.img4)
    
    ###Page 1 __ end __
    
    ###Page 2 __ start __
    def openFolder(self):
        dir_path = QFileDialog.getExistingDirectory(
        parent=self,
        caption="Select directory",
        directory="${HOME}",
        options=QFileDialog.Option.DontUseNativeDialog,
        )
        self.folder = dir_path
        self.uic.folder_label.setText(self.folder) 
    
    def on_checkbox1(self):
        if self.uic.checkbox1.isChecked():
            self.checkbox = 1
            self.uic.checkbox2.setChecked(False)
        
    def on_checkbox2(self):
        if self.uic.checkbox2.isChecked():
            self.checkbox = 2
            self.uic.checkbox1.setChecked(False)
            
    def update_spin_box2(self, value):
        # Cập nhật giá trị của QSpinBox khi QSlider thay đổi
        self.uic.thresh1_data_2.setValue(value)

    def update_slider2(self, value):
        # Cập nhật giá trị của QSlider khi QSpinBox thay đổi
        self.uic.thresh1_2.setValue(value)

    def multiprocessing(self):
        print(self.folder)
        self.thread = ImageProcessingThread(folder_paths=self.folder, thresh1=self.uic.thresh1.value(), check = self.checkbox, ignore=self.uic.ignore.toPlainText(), check_ignore=self.checkIgnore)
        self.thread.finished.connect(self.processing_finished)
        self.thread.start()
    

    def processing_finished(self, data_frame,max_d):
        self.data_frame = data_frame
        self.max_d = max_d
        print(data_frame)
        data_frame.to_excel(os.path.join(os.getcwd(),'data.xlsx'), index=False, engine='openpyxl')
        self.setTable(data_frame, self.uic.data_frame_2) 
        self.uic.data_frame_2.setStyleSheet("background-color: rgb(255,255,255);")
        self.plot_diameter_pixel_values(data_frame, self.uic.plot_data)
    def setTable(self,data_frame, table):
        table.setRowCount(len(data_frame))
        table.setColumnCount(len(data_frame.columns))  # Đặt số cột dựa trên số lượng cột của DataFrame
        table.setHorizontalHeaderLabels(data_frame.columns)  # Đặt tên cột dựa trên tên cột của DataFrame
        
        for i in range(len(data_frame)):
            for j in range(len(data_frame.columns)):
                # Lấy giá trị từ DataFrame tại hàng i và cột j
                value = data_frame.iat[i, j]
                
                # Tạo item và căn giữa
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Đặt item vào ô tương ứng
                table.setItem(i, j, item)

    def plot_diameter_pixel_values(self, data_img, plot_frame):
        data_img = data_img.to_dict(orient='records')
        
        # Xóa mọi đồ thị trước đó khỏi plot_frame
        for widget in plot_frame.findChildren(FigureCanvas):
            widget.setParent(None)
        
        # Lấy kích thước của plot_frame để điều chỉnh Figure cho phù hợp
        frame_width = plot_frame.width()
        frame_height = plot_frame.height()

        # Tạo một Figure với kích thước phù hợp
        fig = Figure(figsize=(20, 5), dpi=100)
        canvas = FigureCanvas(fig)
        
        # Đặt kích thước cố định cho canvas để không vượt quá plot_frame
        canvas.setFixedSize(frame_width, frame_height)

        # Vẽ đồ thị lên Figure
        ax = fig.add_subplot(111)
        max_diameter = max(len(entry['Diameter Pixel Values']) for entry in data_img)
        for entry in data_img:
            diameter_pixel_values = entry['Diameter Pixel Values']
            ax.plot(diameter_pixel_values, linestyle='-')
        
        # Thiết lập các thuộc tính cho biểu đồ
        ax.set_xlabel('Pixel trên đường kính')
        ax.set_ylabel('Cường độ xám')
        ax.set_title('Cường độ xám trên đường kính lớn nhất của các contour')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.minorticks_on()
        ax.grid(True, which='minor', linestyle=':', linewidth=0.5)
        ax.set_xticks(np.arange(0, int(max_diameter) + 1))
        ax.set_yticks(np.arange(30, 255, 20))
        ax.set_ylim(30, 255)
        #ax.legend([entry['Filename'] for entry in data_img], loc='upper right')
        
        # Thêm thước đo trên cả bốn cạnh
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(axis='x', direction='in', length=6, width=2)
        ax.tick_params(axis='y', direction='in', length=6, width=2)
        
        # Lưu đồ thị vào thư mục process
        plot_path = os.path.join(os.getcwd(), 'contours_diameter_pixel_values.png')
        fig.savefig(plot_path)
        
        # Kiểm tra và thiết lập layout cho plot_frame nếu cần
        if plot_frame.layout() is None:
            plot_frame.setLayout(QVBoxLayout())
        
        # Làm sạch layout trước khi thêm đồ thị mới
        layout = plot_frame.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Thêm canvas vào plot_frame và cập nhật FigureCanvas để hiển thị đồ thị
        layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignCenter)  # Căn giữa nếu có không gian trống
        canvas.draw()

    def open_ruler(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Chọn ảnh", "", "Images (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.img_original = cv2.imread(file_path)
            if self.img_original is None:
                QMessageBox.warning(self, "Lỗi", "Không thể mở ảnh")
                return

            cv2.imshow("Ruler", self.img_original.copy())
            cv2.setMouseCallback("Ruler", self.click_event)

            cv2.waitKey(0)
            cv2.destroyAllWindows()

            if self.line_length > 0:
                self.uic.ruler.setText(f"{self.line_length:.2f} px")

    def click_event(self, event, x, y, flags, param):
        img = self.img_original.copy()

        if event == cv2.EVENT_LBUTTONDOWN:
            if not self.drawing:
                # Click lần 1 -> lưu điểm bắt đầu
                self.start_point = (x, y)
                self.drawing = True
                cv2.circle(img, self.start_point, 5, (0, 0, 255), -1)
                cv2.imshow("Ruler", img)
            else:
                # Click lần 2 -> vẽ line và tính khoảng cách
                end_point = (x, y)
                cv2.line(img, self.start_point, end_point, (0, 255, 0), 2)
                cv2.circle(img, end_point, 5, (255, 0, 0), -1)
                cv2.imshow("Ruler", img)

                # Tính khoảng cách
                x1, y1 = self.start_point
                x2, y2 = end_point
                self.line_length = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

                print(f"Line length: {self.line_length:.2f} px")
                mm_per_pixel = 10 / self.line_length
                print(f"Khíc thước thực tế: {mm_per_pixel}")
                # Reset để đo tiếp
                self.start_point = None
                self.drawing = False

        elif event == cv2.EVENT_MOUSEMOVE and self.drawing:
            # Khi rê chuột, vẽ line tạm
            cv2.line(img, self.start_point, (x, y), (0, 255, 255), 1)
            cv2.circle(img, self.start_point, 5, (0, 0, 255), -1)
            cv2.imshow("Ruler", img)
    
        
    ###end page2
    
    ###start page3
    def openFolder2(self):
        dir_path = QFileDialog.getExistingDirectory(
        parent=self,
        caption="Select directory",
        directory="${HOME}",
        options=QFileDialog.Option.DontUseNativeDialog,
        )
        self.folder3 = dir_path
        self.uic.folder_label2.setText(self.folder3) 
        
    def multiprocessing2(self):
        self.thread = ImageProcessingThread2(folder_path=self.folder3, df=self.data_frame,ignore="phatquang", max_d= self.max_d)
        self.thread.finished.connect(self.processing_finished2)
        self.thread.start()
    

    def processing_finished2(self, data_frame):
        print(data_frame)
        data_frame.to_excel(os.path.join(os.getcwd(),'data_phatquang.xlsx'), index=False, engine='openpyxl')
        self.setTable2(data_frame, self.uic.data_frame_3) 
        self.uic.data_frame_3.setStyleSheet("background-color: rgb(255,255,255);")
        self.plot_diameter_pixel_values2(data_frame, self.uic.plot_data2)
        
    def setTable2(self,data_frame, table):
        table.setRowCount(len(data_frame))
        table.setColumnCount(len(data_frame.columns))  # Đặt số cột dựa trên số lượng cột của DataFrame
        table.setHorizontalHeaderLabels(data_frame.columns)  # Đặt tên cột dựa trên tên cột của DataFrame
        
        for i in range(len(data_frame)):
            for j in range(len(data_frame.columns)):
                # Lấy giá trị từ DataFrame tại hàng i và cột j
                value = data_frame.iat[i, j]
                
                # Tạo item và căn giữa
                item = QTableWidgetItem(str(value))
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                
                # Đặt item vào ô tương ứng
                table.setItem(i, j, item)

    def plot_diameter_pixel_values2(self, data_img, plot_frame):
        data_img = data_img.to_dict(orient='records')
        
        # Xóa mọi đồ thị trước đó khỏi plot_frame
        for widget in plot_frame.findChildren(FigureCanvas):
            widget.setParent(None)
        
        # Lấy kích thước của plot_frame để điều chỉnh Figure cho phù hợp
        frame_width = plot_frame.width()
        frame_height = plot_frame.height()

        # Tạo một Figure với kích thước phù hợp
        fig = Figure(figsize=(20, 5), dpi=100)
        canvas = FigureCanvas(fig)
        
        # Đặt kích thước cố định cho canvas để không vượt quá plot_frame
        canvas.setFixedSize(frame_width, frame_height)

        # Vẽ đồ thị lên Figure
        ax = fig.add_subplot(111)
        max_diameter = max(len(entry['Diameter Pixel Values']) for entry in data_img)
        for entry in data_img:
            diameter_pixel_values = entry['Diameter Pixel Values']
            ax.plot(diameter_pixel_values, linestyle='-')
        
        # Thiết lập các thuộc tính cho biểu đồ
        ax.set_xlabel('Pixel trên đường kính')
        ax.set_ylabel('Cường độ xám')
        ax.set_title('Cường độ xám trên đường kính lớn nhất của các contour')
        ax.grid(True, which='both', linestyle='--', linewidth=0.5)
        ax.minorticks_on()
        ax.grid(True, which='minor', linestyle=':', linewidth=0.5)
        ax.set_xticks(np.arange(0, int(max_diameter) + 1))
        ax.set_yticks(np.arange(30, 255, 20))
        ax.set_ylim(30, 255)
        #ax.legend([entry['Filename'] for entry in data_img], loc='upper right')
        
        # Thêm thước đo trên cả bốn cạnh
        ax.xaxis.set_ticks_position('both')
        ax.yaxis.set_ticks_position('both')
        ax.tick_params(axis='x', direction='in', length=6, width=2)
        ax.tick_params(axis='y', direction='in', length=6, width=2)
        
        # Lưu đồ thị vào thư mục process
        plot_path = os.path.join(os.getcwd(), 'contours_diameter_pixel_values_phatquang.png')
        fig.savefig(plot_path)
        
        # Kiểm tra và thiết lập layout cho plot_frame nếu cần
        if plot_frame.layout() is None:
            plot_frame.setLayout(QVBoxLayout())
        
        # Làm sạch layout trước khi thêm đồ thị mới
        layout = plot_frame.layout()
        for i in reversed(range(layout.count())):
            widget = layout.itemAt(i).widget()
            if widget is not None:
                widget.deleteLater()
        
        # Thêm canvas vào plot_frame và cập nhật FigureCanvas để hiển thị đồ thị
        layout.addWidget(canvas, alignment=Qt.AlignmentFlag.AlignCenter)  # Căn giữa nếu có không gian trống
        canvas.draw()
    ###end page3
if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_win = MainWindow()
    main_win.show()
    sys.exit(app.exec())