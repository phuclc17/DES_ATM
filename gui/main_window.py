import os
from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QMessageBox, 
                             QInputDialog, QLineEdit, QDialog, QFormLayout, QDialogButtonBox, QLabel, 
                             QFileDialog, QGroupBox, QPushButton)
from PyQt5.QtCore import Qt

from gui.components.atm_keypad import ATMKeypad
from gui.components.server_logger import ServerLogger
from gui.components.visualizer import AvalancheVisualizer
from core.iso9564 import ISO9564_Processor
from core.key_scheduler import KeyScheduler
from core.des_logic import DES_Logic
from utils.converters import bin_to_hex, xor_hex_strings

# --- CLASS HỘP THOẠI NHẬP KHÓA KÉP ---
class DualKeyDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Nạp khóa Kiểm soát kép (Dual Control)")
        self.resize(700, 350)
        self.setObjectName("DualKeyDialog")
        
        self.key_a = ""
        self.key_b = ""
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout()
        
        lbl_info = QLabel("Yêu cầu 2 quản lý nhập thành phần khóa độc lập (16 ký tự Hex).\nHệ thống sẽ XOR 2 thành phần này để tạo khóa chính.")
        lbl_info.setStyleSheet("color: #ccc; font-style: italic; margin-bottom: 15px; font-size: 13px;")
        lbl_info.setWordWrap(True)
        layout.addWidget(lbl_info)

        # --- QUẢN LÝ A ---
        group_a = QGroupBox("👤 QUẢN LÝ A (Component 1)")
        group_a.setStyleSheet("color: #00e5ff;") 
        layout_a = QHBoxLayout()
        
        self.txt_a = QLineEdit()
        self.txt_a.setPlaceholderText("Nhập khóa A hoặc chọn file...")
        self.txt_a.setEchoMode(QLineEdit.Password)
        self.txt_a.setStyleSheet("color: #00e5ff; background-color: #1a1a1a; border: 1px solid #444; padding: 6px;")
        
        btn_file_a = QPushButton("📂 File A")
        btn_file_a.setCursor(Qt.PointingHandCursor)
        btn_file_a.clicked.connect(lambda: self.load_file(self.txt_a))
        
        layout_a.addWidget(self.txt_a)
        layout_a.addWidget(btn_file_a)
        group_a.setLayout(layout_a)
        layout.addWidget(group_a)

        # --- QUẢN LÝ B ---
        group_b = QGroupBox("👤 QUẢN LÝ B (Component 2)")
        group_b.setStyleSheet("color: #ffea00;")
        layout_b = QHBoxLayout()
        
        self.txt_b = QLineEdit()
        self.txt_b.setPlaceholderText("Nhập khóa B hoặc chọn file...")
        self.txt_b.setEchoMode(QLineEdit.Password)
        self.txt_b.setStyleSheet("color: #ffea00; background-color: #1a1a1a; border: 1px solid #444; padding: 6px;")
        
        btn_file_b = QPushButton("📂 File B")
        btn_file_b.setCursor(Qt.PointingHandCursor)
        btn_file_b.clicked.connect(lambda: self.load_file(self.txt_b))
        
        layout_b.addWidget(self.txt_b)
        layout_b.addWidget(btn_file_b)
        group_b.setLayout(layout_b)
        layout.addWidget(group_b)

        # --- BUTTONS ---
        layout.addSpacing(20)
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Ok).setText("Xác Nhận && Trộn Khóa")
        btn_box.button(QDialogButtonBox.Cancel).setText("Hủy Bỏ")
        
        btn_box.accepted.connect(self.validate)
        btn_box.rejected.connect(self.reject)
        
        layout.addStretch()
        layout.addWidget(btn_box)
        self.setLayout(layout)

    def load_file(self, target_input):
        fname, _ = QFileDialog.getOpenFileName(self, "Chọn file khóa", "", "Text Files (*.txt);;All Files (*)")
        if fname:
            try:
                with open(fname, 'r') as f:
                    content = f.read().strip()
                    target_input.setText(content)
            except: pass

    def validate(self):
        ka = self.txt_a.text().strip()
        kb = self.txt_b.text().strip()

        import string
        valid_chars = string.hexdigits
        
        if len(ka) != 16 or not all(c in valid_chars for c in ka):
            QMessageBox.warning(self, "Lỗi Quản Lý A", "Khóa A không hợp lệ!\nPhải đủ 16 ký tự Hex (0-9, A-F).")
            return
            
        if len(kb) != 16 or not all(c in valid_chars for c in kb):
            QMessageBox.warning(self, "Lỗi Quản Lý B", "Khóa B không hợp lệ!\nPhải đủ 16 ký tự Hex (0-9, A-F).")
            return

        self.key_a = ka.upper()
        self.key_b = kb.upper()
        self.accept()

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Đồ án ATTT - Mô phỏng Bảo mật ATM (DES White-box)")
        self.resize(1200, 750)

        self.des = DES_Logic()
        
        self.master_key = None 
        self.subkeys = [] 
        self.current_cipher = None 
        self.current_pan = None    
        self.current_input_block = None

        self.setup_ui()
        self.load_styles()

    def setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)

        self.atm_panel = ATMKeypad()
        self.atm_panel.transaction_signal.connect(self.handle_transaction)

        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        
        self.logger = ServerLogger()
        # Kết nối các nút bấm
        self.logger.generate_key_signal.connect(self.handle_keygen_dual_control)
        self.logger.decrypt_signal.connect(self.handle_decryption)
        self.logger.manual_check_signal.connect(self.open_manual_decrypt_tool)

        self.visualizer = AvalancheVisualizer()
        self.visualizer.run_test_signal.connect(self.handle_avalanche_test)

        right_layout.addWidget(self.logger, stretch=4)
        right_layout.addWidget(self.visualizer, stretch=1)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(self.atm_panel)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 800])
        
        main_layout.addWidget(splitter)

        # LOG TRẠNG THÁI CHỜ
        self.logger.log("HỆ THỐNG KHỞI ĐỘNG...", "THÔNG TIN")
        self.logger.log("⚠️ CHƯA CÓ KHÓA BẢO MẬT (MASTER KEY)!", "LỖI")
        self.logger.log("Vui lòng bấm nút 'SINH KHÓA' để nạp khóa.", "LỖI")

    def load_styles(self):
        try:
            style_path = os.path.join(os.path.dirname(__file__), "styles.qss")
            with open(style_path, "r", encoding="utf-8") as f:
                self.setStyleSheet(f.read())
        except: pass

    # --- [ĐÃ SỬA] HIỆN FULL MASTER KEY ---
    def handle_keygen_dual_control(self):
        self.logger.clear_log()
        self.logger.log("🛠️ BẮT ĐẦU QUY TRÌNH NẠP KHÓA...", "XỬ LÝ")
        
        dialog = DualKeyDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            k1 = dialog.key_a
            k2 = dialog.key_b
            
            try:
                self.master_key = xor_hex_strings(k1, k2)
            except:
                self.logger.log("❌ Lỗi trộn khóa.", "LỖI")
                return

            # Che thành phần khóa
            masked_k1 = "****" + k1[-4:] if len(k1) > 4 else k1
            masked_k2 = "****" + k2[-4:] if len(k2) > 4 else k2
            
            # [SỬA] Hiện Full Master Key để kiểm tra
            full_mk = self.master_key

            self.logger.log(f"   Đã nhận Component 1: {masked_k1}", "THÔNG TIN")
            self.logger.log(f"   Đã nhận Component 2: {masked_k2}", "THÔNG TIN")
            # Dòng dưới đây sẽ hiện đầy đủ khóa Master
            self.logger.log(f"   -> Master Key (XOR): {full_mk}", "MÃ HÓA")
            
            # Sinh khóa
            self.subkeys = KeyScheduler.generate_subkeys(self.master_key)
            
            self.logger.log(f"   > Đã sinh 16 khóa con (Subkeys):", "THÔNG TIN")
            for i, k in enumerate(self.subkeys):
                k_hex = bin_to_hex(k)
                self.logger.log(f"     K{i+1:02d}: {k_hex}", "THÔNG TIN")
            
            self.logger.log("✅ HỆ THỐNG SẴN SÀNG.", "KẾT QUẢ")
        else:
            self.logger.log("❌ Đã hủy nạp khóa.", "LỖI")

    # --- CÁC HÀM KHÁC (GIỮ NGUYÊN) ---
    def handle_transaction(self, pin, pan):
        if not self.subkeys:
            QMessageBox.critical(self, "Lỗi", "Chưa có khóa bảo mật!")
            return
        if not pan:
            QMessageBox.warning(self, "Lỗi", "Chưa có thẻ (PAN).")
            return
        if len(pin) < 4:
            QMessageBox.warning(self, "Lỗi", "PIN quá ngắn.")
            return
        
        self.logger.clear_log()
        self.logger.log(f"📡 [ATM] NHẬN GIAO DỊCH...", "THÔNG TIN")
        self.logger.log(f"   PAN: {pan}", "THÔNG TIN")

        try:
            input_block_hex = ISO9564_Processor.create_input_block(pin, pan)
            self.logger.log(f"🔄 [ATM] ĐÓNG GÓI ISO 9564: {input_block_hex}", "XỬ LÝ")
            
            self.logger.log(f"🔒 [ATM] MÃ HÓA DES...", "MÃ HÓA")
            
            cipher_hex, trace_logs = self.des.run_des_block(input_block_hex, self.subkeys)
            
            for log_line in trace_logs:
                log_vi = log_line.replace("R", "V").replace("K:", "Key:").replace("INIT IP", "KHỞI TẠO")
                self.logger.log(f"   {log_vi}", "THÔNG TIN")

            self.logger.log(f"📦 [MẠNG] GÓI TIN GỬI ĐI: {cipher_hex}", "KẾT QUẢ")
            
            self.current_cipher = cipher_hex
            self.current_pan = pan
            self.current_input_block = input_block_hex
            self.logger.log("⏳ [SERVER] ĐÃ NHẬN GÓI TIN. CHỜ XỬ LÝ...", "LỖI")
            self.logger.enable_decrypt_button(True) 
        except Exception as e:
            self.logger.log(f"Lỗi: {str(e)}", "LỖI")

    def handle_decryption(self):
        if not self.current_cipher: return
        self.logger.log(f"🔓 [SERVER] GIẢI MÃ...", "XỬ LÝ")
        
        decrypted_hex, _ = self.des.run_des_block(self.current_cipher, self.subkeys, is_decrypt=True)
        extracted_pin = ISO9564_Processor.extract_pin(decrypted_hex, self.current_pan)
        
        self.logger.log(f"   Block giải mã: {decrypted_hex}", "THÔNG TIN")
        
        if decrypted_hex == self.current_input_block:
            self.logger.log(f"✅ CHẤP NHẬN: PIN {extracted_pin}", "KẾT QUẢ")
            QMessageBox.information(self, "Thành Công", f"PIN Hợp lệ: {extracted_pin}")
            self.atm_panel.clear_pin()
        else:
            self.logger.log("❌ TỪ CHỐI: SAI MÃ PIN!", "LỖI")
            QMessageBox.critical(self, "Thất Bại", "Sai mã PIN!")
        self.logger.enable_decrypt_button(False)
        self.current_cipher = None

    def open_manual_decrypt_tool(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Công cụ Giải mã Thủ công")
        dialog.resize(500, 300)
        dialog.setStyleSheet("background-color: #2d2d2d; color: white;")
        layout = QVBoxLayout()
        form = QFormLayout()
        
        txt_key = QLineEdit()
        txt_key.setPlaceholderText("Master Key (Hex)")
        if self.master_key: txt_key.setText(self.master_key) 
            
        txt_cipher = QLineEdit()
        txt_cipher.setPlaceholderText("Ciphertext (Hex)")
        if self.current_cipher: txt_cipher.setText(self.current_cipher) 
            
        txt_pan = QLineEdit()
        txt_pan.setPlaceholderText("PAN (Số thẻ)")
        if self.current_pan: txt_pan.setText(self.current_pan)

        for w in [txt_key, txt_cipher, txt_pan]:
            w.setStyleSheet("background-color: #1e1e1e; color: #00e5ff; border: 1px solid #444; padding: 5px;")

        form.addRow("Master Key:", txt_key)
        form.addRow("Bản mã:", txt_cipher)
        form.addRow("Số thẻ:", txt_pan)
        
        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.button(QDialogButtonBox.Ok).setText("Thử Giải Mã")
        btn_box.button(QDialogButtonBox.Cancel).setText("Đóng")
        layout.addLayout(form)
        
        lbl_result = QLabel("...")
        lbl_result.setStyleSheet("color: #aaa; font-size: 13px; margin-top: 20px;")
        lbl_result.setAlignment(Qt.AlignCenter)
        layout.addWidget(lbl_result)
        layout.addWidget(btn_box)
        dialog.setLayout(layout)

        def perform_manual_decrypt():
            k, c, p = txt_key.text().strip(), txt_cipher.text().strip(), txt_pan.text().strip()
            if len(k) != 16 or len(c) != 16:
                lbl_result.setText("❌ Lỗi: Key/Cipher phải đủ 16 ký tự Hex!")
                return
            try:
                manual_subkeys = KeyScheduler.generate_subkeys(k)
                decrypted, _ = self.des.run_des_block(c, manual_subkeys, is_decrypt=True)
                pin = ISO9564_Processor.extract_pin(decrypted, p)
                if pin:
                    lbl_result.setText(f"✅ THÀNH CÔNG! PIN: {pin}")
                    lbl_result.setStyleSheet("color: #00e676; font-weight: bold;")
                else:
                    lbl_result.setText(f"⚠️ RA RÁC (SAI KHÓA?)")
                    lbl_result.setStyleSheet("color: #ffea00;")
            except Exception as e: lbl_result.setText(f"Lỗi: {str(e)}")

        btn_box.accepted.connect(perform_manual_decrypt)
        btn_box.rejected.connect(dialog.reject)
        dialog.exec_()

    def handle_avalanche_test(self, pin1, pin2):
        if not self.subkeys:
            QMessageBox.warning(self, "Lỗi", "Chưa có khóa.")
            return
        if not pin1 or not pin2:
            QMessageBox.warning(self, "Lỗi", "Thiếu input.")
            return
        
        pan = "4987123456789012" 
        self.logger.clear_log()
        self.logger.log(f"--- 🧪 KIỂM THỬ TUYẾT LỞ ---", "MÃ HÓA")
        block1 = ISO9564_Processor.create_input_block(pin1, pan)
        block2 = ISO9564_Processor.create_input_block(pin2, pan)
        
        cipher1, _ = self.des.run_des_block(block1, self.subkeys)
        cipher2, _ = self.des.run_des_block(block2, self.subkeys)
        
        from utils.converters import hex_to_bin
        bin1, bin2 = hex_to_bin(cipher1), hex_to_bin(cipher2)
        diff = sum(1 for a, b in zip(bin1, bin2) if a != b)
        percent = (diff / 64) * 100
        
        self.logger.log(f"Bản mã A: {cipher1}", "THÔNG TIN")
        self.logger.log(f"Bản mã B: {cipher2}", "THÔNG TIN")
        self.logger.log(f"Khác biệt: {diff} bits ({percent:.2f}%)", "KẾT QUẢ")
        self.visualizer.update_progress(percent)