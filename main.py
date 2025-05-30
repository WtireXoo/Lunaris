from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QStackedWidget, QCheckBox, QSlider, QSizePolicy, QSpacerItem
)
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QPainter, QColor, QBrush, QFont
import sys
import psutil
import platform
import GPUtil
import wmi
from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QIcon


def get_cpu_info():
    return platform.processor()

def get_ram_info():
    ram = psutil.virtual_memory()
    return f"Total: {ram.total / (1024**3):.2f} GB, Used: {ram.used / (1024**3):.2f} GB"

def get_gpu_info():
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        return f"{gpu.name}, {gpu.memoryTotal} MB VRAM"
    else:
        return "No GPU detected"

def get_disk_info():
    disk = psutil.disk_usage('/')
    return f"Total: {disk.total / (1024**3):.2f} GB, Free: {disk.free / (1024**3):.2f} GB"

def get_system_info():
    c = wmi.WMI()
    for os in c.Win32_OperatingSystem():
        return f"{os.Caption} {os.OSArchitecture}"

class TransparentSysInfo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(1100, 700)
        self.setWindowTitle("Lunaris")
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.old_pos = None

        self.setWindowIcon(QIcon("lunarisico.ico"))
        

        # Initial customization values
        self.transparency = 80    # background alpha (0-255)
        self.border_radius = 20    # px
        self.font_size = 20        # default font size
        self.dark_mode_enabled = True

        # Center window on screen
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(screen.center().x() - self.width() // 2, screen.center().y() - self.height() // 2)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # --- TAB BAR ---
        tab_layout = QHBoxLayout()
        self.tabs = {}
        tab_names = ["System Info", "Customization", "About"]
        for i, name in enumerate(tab_names):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setStyleSheet(self.get_tab_button_style())
            btn.clicked.connect(lambda _, index=i: self.switch_tab(index))
            tab_layout.addWidget(btn)
            self.tabs[i] = btn

        main_layout.addLayout(tab_layout)

        # --- STACKED PAGES ---
        self.stack = QStackedWidget()
# --- STACKED PAGES ---
        self.stack = QStackedWidget()
        self.stack.addWidget(self.create_system_info_page())
        self.stack.addWidget(self.create_customization_page())
        self.stack.addWidget(self.create_placeholder_page("Lunaris v0.5\nThis app is licensed."))


        # Footer label at the very bottom
        self.footer_label = QLabel("Lunaris - 0.5")
        self.footer_label.setAlignment(Qt.AlignCenter)
        self.footer_label.setStyleSheet("color: #9b59b6; font-size: 19px; font-family: Segoe UI; margin-bottom: 10px;")
        main_layout.addWidget(self.footer_label)


        main_layout.addWidget(self.stack)
        
        self.setLayout(main_layout)

        self.switch_tab(0)  # Default tab

    def get_tab_button_style(self):
        # Style for tab buttons, adapts to dark mode
        if self.dark_mode_enabled:
            return """
                QPushButton {
                    background-color: transparent;
                    color: #a18fff;
                    font-size: 20px;
                    padding: 10px 20px;
                    border: none;
                }
                QPushButton:checked {
                    color: #d19aff;
                    border-bottom: 2px solid #d19aff;
                }
            """
        else:
            return """
                QPushButton {
                    background-color: transparent;
                    color: white;
                    font-size: 20px;
                    padding: 10px 20px;
                    border: none;
                }
                QPushButton:checked {
                    color: #9b59b6;
                    border-bottom: 2px solid #9b59b6;
                }
            """

    def create_system_info_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)

        label_style = f"color: white; font-size: 24px; font-family: Segoe UI;"
        value_style = f"color: #9b59b6; font-size: 20px; font-family: Segoe UI;"

        items = [
            ("CPU:", get_cpu_info()),
            ("RAM:", get_ram_info()),
            ("GPU:", get_gpu_info()),
            ("Disk:", get_disk_info()),
            ("OS:", get_system_info())
        ]

        for title, value in items:
            lbl_title = QLabel(title)
            lbl_title.setStyleSheet(label_style)
            lbl_value = QLabel(value)
            lbl_value.setStyleSheet(value_style)
            layout.addWidget(lbl_title)
            layout.addWidget(lbl_value)

        page.setLayout(layout)
        return page

    def create_customization_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(25)

        # Transparency slider
        self.transparency_slider = QSlider(Qt.Horizontal)
        self.transparency_slider.setRange(50, 255)
        self.transparency_slider.setValue(self.transparency)
        self.transparency_slider.valueChanged.connect(self.update_transparency)
        transparency_label = QLabel(f"Background Transparency: {self.transparency}")
        transparency_label.setStyleSheet("color: white; font-size: 18px;")
        self.transparency_label = transparency_label

        layout.addWidget(transparency_label)
        layout.addWidget(self.transparency_slider)

        # Border radius slider
        self.border_radius_slider = QSlider(Qt.Horizontal)
        self.border_radius_slider.setRange(0, 50)
        self.border_radius_slider.setValue(self.border_radius)
        self.border_radius_slider.valueChanged.connect(self.update_border_radius)
        border_radius_label = QLabel(f"Border Radius: {self.border_radius}px")
        border_radius_label.setStyleSheet("color: white; font-size: 18px;")
        self.border_radius_label = border_radius_label

        layout.addWidget(border_radius_label)
        layout.addWidget(self.border_radius_slider)

        # Font size slider
        self.font_slider = QSlider(Qt.Horizontal)
        self.font_slider.setRange(10, 40)
        self.font_slider.setValue(self.font_size)
        self.font_slider.valueChanged.connect(self.update_font_size)
        font_label = QLabel(f"Font Size: {self.font_size}px")
        font_label.setStyleSheet("color: white; font-size: 18px;")
        self.font_label = font_label

        layout.addWidget(font_label)
        layout.addWidget(self.font_slider)

        # Dark mode checkbox
        self.dark_mode_checkbox = QCheckBox("Enable / Disable Dark Mode")
        self.dark_mode_checkbox.setStyleSheet("color: white; font-size: 18px;")
        self.dark_mode_checkbox.stateChanged.connect(self.toggle_dark_mode)
        layout.addWidget(self.dark_mode_checkbox)

        # Spacer to push items up nicely
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        layout.addItem(spacer)

        page.setLayout(layout)
        return page

    def update_transparency(self, value):
        self.transparency = value
        self.transparency_label.setText(f"Background Transparency: {value}")
        self.update()

    def update_border_radius(self, value):
        self.border_radius = value
        self.border_radius_label.setText(f"Border Radius: {value}px")
        self.update()

    def update_font_size(self, value):
        self.font_size = value
        self.font_label.setText(f"Font Size: {value}px")
        self.update_font_styles()

    def update_font_styles(self):
        # Update font sizes for all labels/buttons dynamically
        font_css = f"font-size: {self.font_size}px; font-family: Segoe UI;"
        # Update System Info labels
        for i in range(self.stack.widget(0).layout().count()):
            item = self.stack.widget(0).layout().itemAt(i).widget()
            if isinstance(item, QLabel):
                if i % 2 == 0:  # title labels
                    item.setStyleSheet(f"color: white; {font_css}")
                else:  # value labels
                    item.setStyleSheet(f"color: #9b59b6; {font_css}")

        # Update Customization tab widgets font sizes
        self.transparency_label.setStyleSheet(f"color: white; {font_css}")
        self.border_radius_label.setStyleSheet(f"color: white; {font_css}")
        self.font_label.setStyleSheet(f"color: white; {font_css}")
        self.dark_mode_checkbox.setStyleSheet(f"color: white; {font_css}")

        # Update tab buttons font size
        for btn in self.tabs.values():
            btn.setStyleSheet(self.get_tab_button_style())

    def toggle_dark_mode(self, state):
        self.dark_mode_enabled = (state == Qt.Checked)
        # Update tab button styles
        for btn in self.tabs.values():
            btn.setStyleSheet(self.get_tab_button_style())
        self.update()

    def create_placeholder_page(self, text):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        label = QLabel(text)
        label.setStyleSheet(f"color: white; font-size: {self.font_size + 2}px; font-family: Segoe UI;")
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        page.setLayout(layout)
        return page

    def switch_tab(self, index):
        # Update button checked state
        for i, btn in self.tabs.items():
            btn.setChecked(i == index)
        self.stack.setCurrentIndex(index)

    # Make window draggable
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.old_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = QPoint(event.globalPos() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPos()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def paintEvent(self, event):
        # Paint the translucent rounded background with purple shade
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        rect = self.rect()

        if self.dark_mode_enabled:
            bg_color = QColor(30, 30, 30, self.transparency)
            border_color = QColor(100, 50, 150, 200)
        else:
            bg_color = QColor(75, 0, 130, self.transparency)  # purple
            border_color = QColor(150, 75, 200, 200)

        painter.setBrush(QBrush(bg_color))
        painter.setPen(border_color)
        painter.drawRoundedRect(rect.adjusted(1, 1, -2, -2), self.border_radius, self.border_radius)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TransparentSysInfo()
    window.show()
    sys.exit(app.exec_())