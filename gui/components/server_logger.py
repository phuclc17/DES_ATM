from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QLabel, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtGui import QTextCursor
from PyQt5.QtCore import Qt, pyqtSignal

class ServerLogger(QWidget):
    # Các tín hiệu gửi về MainWindow
    generate_key_signal = pyqtSignal()
    decrypt_signal = pyqtSignal()
    manual_check_signal = pyqtSignal() # [MỚI] Signal mở công cụ thủ công

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # --- CONTROL PANEL (SERVER) ---
        control_frame = QFrame()
        control_frame.setStyleSheet("background-color: #252525; border-bottom: 1px solid #444; padding: 5px;")
        control_layout = QHBoxLayout(control_frame)

        lbl_title = QLabel("🖥️ SERVER ADMIN:")
        lbl_title.setStyleSheet("color: #00e5ff; font-weight: bold;")
        
        # Nút Sinh Khóa
        self.btn_init = QPushButton("🔑 SINH KHÓA")
        self.btn_init.setCursor(Qt.PointingHandCursor)
        self.btn_init.setStyleSheet("background-color: #e65100; color: white; font-weight: bold; padding: 5px;")
        self.btn_init.clicked.connect(lambda: self.generate_key_signal.emit())

        # Nút Giải Mã Tự Động
        self.btn_decrypt = QPushButton("🔓 GIẢI MÃ TỰ ĐỘNG")
        self.btn_decrypt.setCursor(Qt.PointingHandCursor)
        self.btn_decrypt.setStyleSheet("background-color: #2e7d32; color: #aaa; font-weight: bold; padding: 5px;")
        self.btn_decrypt.setEnabled(False) # Ban đầu ẩn đi
        self.btn_decrypt.clicked.connect(lambda: self.decrypt_signal.emit())

        # [MỚI] Nút Kiểm Tra Thủ Công
        self.btn_manual = QPushButton("🛠️ TOOL TEST")
        self.btn_manual.setCursor(Qt.PointingHandCursor)
        self.btn_manual.setStyleSheet("background-color: #455a64; color: white; border: 1px solid #aaa; padding: 5px;")
        self.btn_manual.setToolTip("Mở công cụ nhập Khóa và Bản mã bằng tay để kiểm tra")
        self.btn_manual.clicked.connect(lambda: self.manual_check_signal.emit())

        control_layout.addWidget(lbl_title)
        control_layout.addWidget(self.btn_init)
        control_layout.addWidget(self.btn_decrypt)
        control_layout.addWidget(self.btn_manual)
        layout.addWidget(control_frame)
        # ------------------------------

        self.console = QTextEdit()
        self.console.setObjectName("ServerLog")
        self.console.setReadOnly(True)
        layout.addWidget(self.console)
        
        self.setLayout(layout)

    def log(self, message, level="THÔNG TIN"):
        colors = {
            "THÔNG TIN": "#b0bec5",    
            "XỬ LÝ": "#29b6f6", 
            "MÃ HÓA": "#fdd835", 
            "KẾT QUẢ": "#69f0ae",  
            "LỖI": "#ff5252"    
        }
        color = colors.get(level, "#ffffff")
        
        html = f"""
        <div style="margin-bottom: 2px;">
            <span style="color: {color}; font-weight: bold;">[{level}]</span>
            <span style="color: #e0e0e0;">{message}</span>
        </div>
        """
        self.console.append(html)
        self.console.moveCursor(QTextCursor.End)

    def clear_log(self):
        self.console.clear()
    
    def enable_decrypt_button(self, enable=True):
        self.btn_decrypt.setEnabled(enable)
        if enable:
             self.btn_decrypt.setStyleSheet("background-color: #00c853; color: white; font-weight: bold; padding: 5px;")
        else:
             self.btn_decrypt.setStyleSheet("background-color: #2e7d32; color: #aaa; font-weight: bold; padding: 5px;")