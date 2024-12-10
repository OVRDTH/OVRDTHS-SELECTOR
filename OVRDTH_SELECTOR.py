import sys
import os

if sys.platform == "win32" and hasattr(sys, "frozen"):
    if hasattr(os, "frozen"):
        if hasattr(os, "add_dll_directory"):
            os.add_dll_directory(os.path.dirname(sys.executable))
        else:
            os.environ["PATH"] = os.path.dirname(sys.executable) + os.pathsep + os.environ["PATH"]

import shutil
import winsound
import keyboard
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDialog, QLabel, QFileIconProvider, QTreeView, QMessageBox, QInputDialog, QAbstractItemView, QFrame
)
from PyQt5.QtCore import Qt, pyqtSignal, QDir, QModelIndex, QPoint
from PyQt5.QtGui import QFont, QIcon, QPixmap
from PyQt5.QtWidgets import QFileSystemModel

__version__ = '4.4.0'
last_selected_save = None
current_keybind = 'alt+s'
settings_backup_path = os.path.join(os.getenv('LOCALAPPDATA'), 'VersionTest54', 'Saved', 'SaveGames', 'settings_backup.sav')


class KeybindDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Keybind")
        self.setModal(True)
        self.label = QLabel("Press the desired key combination now (including ALT). Press Enter to confirm.", self)
        layout = QVBoxLayout(self)
        layout.addWidget(self.label)
        self.pressed_key = None
        self.pressed_mods = None

    def keyPressEvent(self, event):
        mods = []
        if event.modifiers() & Qt.ControlModifier:
            mods.append("ctrl")
        if event.modifiers() & Qt.ShiftModifier:
            mods.append("shift")
        if event.modifiers() & Qt.AltModifier:
            mods.append("alt")
        if event.modifiers() & Qt.MetaModifier:
            mods.append("win")

        key = event.key()
        if key in (Qt.Key_Return, Qt.Key_Enter):
            if self.pressed_key is not None:
                self.accept()
            else:
                self.label.setText("No key combo captured. Press a key combination, then Enter.")
            return
        if key == Qt.Key_Escape:
            self.reject()
            return

        text = event.text()
        if not text:
            self.label.setText("Invalid key. Try another combination and press Enter.")
            return

        self.pressed_mods = mods
        self.pressed_key = text.lower()
        combo = "+".join(self.pressed_mods + [self.pressed_key])
        self.label.setText(f"Captured: {combo}. Press Enter to confirm or another key to change.")

    def get_keybind(self):
        if self.pressed_key is None:
            return None
        combo = "+".join(self.pressed_mods + [self.pressed_key]) if self.pressed_mods else self.pressed_key
        return combo


class NoIconProvider(QFileIconProvider):
    def icon(self, type_or_info):
        return QIcon()

    def iconType(self, info):
        return QIcon()


class MyFileSystemModel(QFileSystemModel):
    def __init__(self, root_path, parent=None):
        super().__init__(parent)
        self.setReadOnly(False)
        self.root_path = os.path.abspath(root_path)
        self.iconProvider = NoIconProvider()
        self.setIconProvider(self.iconProvider)

    def hasChildren(self, parent=QModelIndex()):
        if parent.isValid():
            folder_path = self.filePath(parent)
            loadout_file = os.path.join(folder_path, 'SG Player Equipment.sav')
            if os.path.exists(loadout_file):
                return False
        return super().hasChildren(parent)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.FontRole and index.column() == 0:
            folder_path = self.filePath(index)
            loadout_file = os.path.join(folder_path, 'SG Player Equipment.sav')
            font = QFont()
            font.setPointSize(12)
            if not os.path.exists(loadout_file):
                font.setBold(True)
            return font
        return super().data(index, role)


class MyTreeView(QTreeView):
    def mousePressEvent(self, event):
        item = self.indexAt(event.pos())
        if not item.isValid():
            self.clearSelection()
        super().mousePressEvent(event)


class MainWindow(QMainWindow):
    loadSaveSignal = pyqtSignal()

    def __init__(self):
        super().__init__()

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)

        icon_path = self.resource_path("resources/icon.png")
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        else:
            print(f"Icon not found at path: {icon_path}")

        self.root_path = self.resource_path('pooled_saves')
        if not os.path.exists(self.root_path):
            os.makedirs(self.root_path)

        self.setGeometry(200, 100, 550, 650)

        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        central_widget.setStyleSheet("background-color: #202020;")

        self.title_bar = QFrame()
        self.title_bar.setStyleSheet("background-color: #333333; color: white;")
        self.title_bar.setFixedHeight(40)
        title_bar_layout = QHBoxLayout(self.title_bar)
        title_bar_layout.setContentsMargins(0, 0, 0, 0)

        icon_path = self.resource_path('resources/icon.png')
        if os.path.exists(icon_path):
            icon_label = QLabel(self.title_bar)
            pixmap = QPixmap(icon_path)
            pixmap = pixmap.scaled(62, 62, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            icon_label.setPixmap(pixmap)
            icon_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
            icon_label.setStyleSheet("margin-left: 10px;")
            title_bar_layout.addWidget(icon_label)
        else:
            icon_label = QLabel(self.title_bar)
            title_bar_layout.addWidget(icon_label)

        title_label = QLabel("OVRDTH'S SELECTOR")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-left: 10px;")
        title_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        title_bar_layout.addWidget(title_label)

        title_bar_layout.addStretch()

        minimize_button = QPushButton("-")
        minimize_button.setFixedSize(36, 36)
        minimize_button.setStyleSheet("""
            QPushButton {
                background-color: #444444;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #555555;
            }
        """)
        minimize_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(minimize_button)

        close_button = QPushButton("X")
        close_button.setFixedSize(36, 36)
        close_button.setStyleSheet("""
            QPushButton {
                background-color: #ff5c5c;
                color: white;
                border: none;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #ff1c1c;
            }
        """)
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)

        main_layout.addWidget(self.title_bar)

        self.is_dragging = False
        self.drag_position = None
        self.title_bar.mousePressEvent = self.start_drag
        self.title_bar.mouseMoveEvent = self.perform_drag
        self.title_bar.mouseReleaseEvent = self.end_drag

        self.setup_ui(main_layout)

        keyboard.add_hotkey(current_keybind, self.hotkey_callback)
        self.loadSaveSignal.connect(self.load_last_save_threadsafe)

    def start_drag(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = True
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()

    def perform_drag(self, event):
        if self.is_dragging:
            self.move(event.globalPos() - self.drag_position)

    def end_drag(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.drag_position = None

    def setup_ui(self, main_layout):
        top_button_frame = QWidget()
        top_button_frame.setStyleSheet("background-color: #202020;")
        top_buttons_layout = QHBoxLayout(top_button_frame)
        top_buttons_layout.setSpacing(10)
        main_layout.addWidget(top_button_frame)

        button_style = """
            QPushButton {
                background-color: #333333;
                color: white;
                border: none;
                padding: 6px 12px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #444444;
            }
        """

        create_folder_button = QPushButton("CREATE FOLDER")
        create_folder_button.clicked.connect(self.create_folder)
        create_folder_button.setStyleSheet(button_style)
        top_buttons_layout.addWidget(create_folder_button)

        rename_button = QPushButton("RENAME")
        rename_button.clicked.connect(self.rename_folder)
        rename_button.setStyleSheet(button_style)
        top_buttons_layout.addWidget(rename_button)

        set_keybind_button = QPushButton("SET KEYBIND")
        set_keybind_button.clicked.connect(self.set_custom_keybind)
        set_keybind_button.setStyleSheet(button_style)
        top_buttons_layout.addWidget(set_keybind_button)

        readme_button = QPushButton("VIEW README")
        readme_button.clicked.connect(self.open_readme)
        readme_button.setStyleSheet(button_style)
        top_buttons_layout.addWidget(readme_button)

        self.model = MyFileSystemModel(self.root_path)
        self.model.setFilter(QDir.AllDirs | QDir.NoDotAndDotDot)
        root_index = self.model.setRootPath(self.root_path)

        self.tree = MyTreeView()
        self.tree.setModel(self.model)
        self.tree.setRootIndex(root_index)
        self.tree.setDragDropMode(QTreeView.DragDrop)
        self.tree.setDefaultDropAction(Qt.MoveAction)
        self.tree.doubleClicked.connect(self.on_item_double_clicked)

        self.tree.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.tree.setHeaderHidden(True)

        font = QFont()
        font.setPointSize(12)
        self.tree.setFont(font)

        self.tree.setStyleSheet("""
            QTreeView {
                background-color: #333333;
                color: white;
                border: none;
                font-size: 12pt;
            }
            QTreeView::item:hover {
                background-color: #444444;
            }
            QTreeView::item:selected {
                background-color: #555555;
            }
        """)

        self.tree.setColumnHidden(1, True)
        self.tree.setColumnHidden(2, True)
        self.tree.setColumnHidden(3, True)

        main_layout.addWidget(self.tree)

        bottom_button_frame = QWidget()
        bottom_button_frame.setStyleSheet("background-color: #202020;")
        bottom_buttons_layout = QHBoxLayout(bottom_button_frame)
        bottom_buttons_layout.setSpacing(10)
        main_layout.addWidget(bottom_button_frame)

        save_button = QPushButton("SAVE LOADOUT")
        save_button.clicked.connect(self.save_loadout)
        save_button.setStyleSheet(button_style)
        bottom_buttons_layout.addWidget(save_button)

        delete_button = QPushButton("DELETE")
        delete_button.clicked.connect(self.delete_folder)
        delete_button.setStyleSheet(button_style)
        bottom_buttons_layout.addWidget(delete_button)

    def hotkey_callback(self):
        self.loadSaveSignal.emit()

    def load_last_save_threadsafe(self):
        self.play_default_sound()
        global last_selected_save
        if last_selected_save:
            self.load_save(last_selected_save, triggered_by_keybind=True)
        else:
            print("No save selected yet")

    def resource_path(self, relative_path):
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        return os.path.join(base_path, relative_path)

    def reload_tree(self):
        root_index = self.model.setRootPath(self.root_path)
        self.tree.setRootIndex(root_index)

    def on_item_double_clicked(self, index):
        folder_path = self.model.filePath(index)
        loadout_file = os.path.join(folder_path, 'SG Player Equipment.sav')
        if os.path.exists(loadout_file):
            self.load_save(folder_path, triggered_by_keybind=False)
        else:
            if self.tree.isExpanded(index):
                self.tree.setExpanded(index, False)
            else:
                self.tree.setExpanded(index, True)

    def load_save(self, folder_path, triggered_by_keybind=False):
        appdata_dir = os.getenv('LOCALAPPDATA')
        game_save_dir = os.path.join(appdata_dir, "VersionTest54", "Saved", "SaveGames")
        if not os.path.exists(game_save_dir):
            QMessageBox.critical(self, "Error", f"Game save directory not found: {game_save_dir}")
            return
        try:
            shutil.copytree(folder_path, game_save_dir, dirs_exist_ok=True)
            self.play_default_sound()
            global last_selected_save
            last_selected_save = folder_path

            # *** hopefully deselects double clicked loadout
            self.tree.clearSelection()
            self.tree.setCurrentIndex(QModelIndex()) 

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load save. Error: {str(e)}")

    def set_custom_keybind(self):
        dialog = KeybindDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            new_combo = dialog.get_keybind()
            if new_combo:
                global current_keybind
                keyboard.remove_hotkey(current_keybind)
                current_keybind = new_combo
                keyboard.add_hotkey(current_keybind, self.hotkey_callback)
                QMessageBox.information(self, "Keybind Set", f"New keybind '{current_keybind}' has been set.")
            else:
                QMessageBox.warning(self, "No Keybind", "No key combination was captured.")

    def delete_folder(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "No folder selected to delete.")
            return
        folder_path = self.model.filePath(index)
        confirm = QMessageBox.question(self, "Delete Folder", f"Delete '{os.path.basename(folder_path)}'?")
        if confirm == QMessageBox.Yes:
            try:
                shutil.rmtree(folder_path)
                self.reload_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to delete folder. Error: {str(e)}")

    def create_folder(self):
        selected_indexes = self.tree.selectedIndexes()
        if not selected_indexes:
            current_dir = self.root_path
        else:
            index = self.tree.currentIndex()
            if index.isValid():
                current_dir = self.model.filePath(index)
            else:
                current_dir = self.root_path

        folder_name, ok = QInputDialog.getText(self, "Create Folder", "Folder Name:")
        if ok and folder_name.strip():
            new_path = os.path.join(current_dir, folder_name.strip())

           
            if os.path.exists(new_path):
                sav_files = [file for file in os.listdir(new_path) if file.lower().endswith('.sav') and os.path.isfile(os.path.join(new_path, file))]
                if sav_files:
                    QMessageBox.warning(self, "Error", "Cannot create a folder that contains .sav files.")
                    return

            try:
                os.makedirs(new_path, exist_ok=True)
                self.reload_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to create folder. Error: {str(e)}")

    def save_loadout(self):
        selected_indexes = self.tree.selectedIndexes()
        if not selected_indexes:
            current_dir = self.root_path
        else:
            index = self.tree.currentIndex()
            if index.isValid():
                current_dir = self.model.filePath(index)
            else:
                current_dir = self.root_path

        appdata_dir = os.getenv('LOCALAPPDATA')
        game_save_dir = os.path.join(appdata_dir, "VersionTest54", "Saved", "SaveGames")
        if not os.path.exists(game_save_dir):
            QMessageBox.critical(self, "Error", f"Game save directory not found: {game_save_dir}")
            return

        folder_name, ok = QInputDialog.getText(self, "Save Loadout", "Loadout Name:")
        if ok and folder_name.strip():
            new_folder_path = os.path.join(current_dir, folder_name.strip())

           
            if os.path.exists(new_folder_path):
                sav_files = [file for file in os.listdir(new_folder_path) if file.lower().endswith('.sav') and os.path.isfile(os.path.join(new_folder_path, file))]
                if sav_files:
                    QMessageBox.warning(self, "Error", "Cannot save to a folder that contains .sav files.")
                    return

            try:
                os.makedirs(new_folder_path, exist_ok=True)

                
                sav_files_after = [file for file in os.listdir(new_folder_path) if file.lower().endswith('.sav') and os.path.isfile(os.path.join(new_folder_path, file))]
                if sav_files_after:
                    QMessageBox.warning(self, "Error", "Cannot save to a folder that contains .sav files.")
                    return

                src_file = os.path.join(game_save_dir, 'SG Player Equipment.sav')
                if os.path.exists(src_file):
                    shutil.copy(src_file, new_folder_path)
                    self.reload_tree()

                    
                    self.tree.clearSelection()
                    self.tree.setCurrentIndex(QModelIndex()) 

                else:
                    QMessageBox.warning(self, "Warning", "SG Player Equipment.sav not found in game saves.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to save loadout. Error: {str(e)}")

    def rename_folder(self):
        index = self.tree.currentIndex()
        if not index.isValid():
            QMessageBox.warning(self, "No Selection", "No folder selected to rename.")
            return

        old_path = self.model.filePath(index)
        folder_name, ok = QInputDialog.getText(self, "Rename Folder", "New Folder Name:")
        if ok and folder_name.strip():
            parent_path = os.path.dirname(old_path)
            new_path = os.path.join(parent_path, folder_name.strip())

            
            if os.path.exists(new_path):
                sav_files = [file for file in os.listdir(new_path) if file.lower().endswith('.sav') and os.path.isfile(os.path.join(new_path, file))]
                if sav_files:
                    QMessageBox.warning(self, "Error", "Cannot rename to a folder that contains .sav files.")
                    return

            if os.path.exists(new_path):
                QMessageBox.warning(self, "Error", "A folder with this name already exists.")
                return
            try:
                os.rename(old_path, new_path)
                self.reload_tree()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to rename folder. Error: {str(e)}")

    def open_readme(self):
        readme_path = self.resource_path('README.txt')
        if os.path.exists(readme_path):
            try:
                os.startfile(readme_path)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to open README file: {e}")
        else:
            QMessageBox.critical(self, "Error", "README file not found.")

    def play_default_sound(self):
        winsound.MessageBeep(winsound.MB_OK)


if __name__ == '__main__':
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    icon_path = os.path.join('resources', 'icon.png')
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
    else:
        print(f"Application icon not found at path: {icon_path}")
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
