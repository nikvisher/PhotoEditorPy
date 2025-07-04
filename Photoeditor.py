import sys
import cv2
import numpy as np
import shutil
import os
import tempfile
import subprocess
from PyQt6.QtWidgets import (QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QVBoxLayout, QWidget, QSlider, QHBoxLayout, QGroupBox, QLineEdit, QComboBox, QMessageBox )
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import Qt, QTimer, QUrl
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from moviepy import *

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Главное меню")
        self.setGeometry(100, 100, 400, 200)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        layout = QVBoxLayout()

        self.photo_editor_button = QPushButton("Редактировать фото", self)
        self.photo_editor_button.setStyleSheet("background-color: #FF8C00; padding: 10px; border-radius: 5px; color: white;")
        self.photo_editor_button.clicked.connect(self.open_photo_editor)

        self.video_editor_button = QPushButton("Редактировать видео", self)
        self.video_editor_button.setStyleSheet("background-color: #FF8C00; padding: 10px; border-radius: 5px; color: white;")
        self.video_editor_button.clicked.connect(self.open_video_editor)

        layout.addWidget(self.photo_editor_button)
        layout.addWidget(self.video_editor_button)

        container = QWidget(self)
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.photo_editor = None
        self.video_editor = None
        
        self.center()

    def center(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def open_photo_editor(self):
        self.photo_editor = PhotoEditor(self)
        self.photo_editor.show()
        self.hide()

    def open_video_editor(self):
        self.video_editor = VideoEditor(self)  
        self.video_editor.show()
        self.hide()

    

class PhotoEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Фоторедактор")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        # Создание виджетов
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_label.setStyleSheet("border: 2px solid #FF8C00; background-color: #444;")

        self.open_button = QPushButton("Открыть изображение", self)
        self.open_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.open_button.clicked.connect(self.load_image)

        # Инструменты для редактирования
        # Яркость
        self.brightness_slider = self.create_slider("Яркость", self.adjust_brightness)
        self.brightness_label = QLabel("Яркость: 0", self)
        self.brightness_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.brightness_label.setFixedSize(100, 20)  # Фиксированный размер: ширина 100, высота 20

        # Контрастность
        self.contrast_slider = self.create_slider("Контрастность", self.adjust_contrast)
        self.contrast_label = QLabel("Контрастность: 0", self)
        self.contrast_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.contrast_label.setFixedSize(100, 20)  # Фиксированный размер: ширина 100, высота 20

        # Насыщенность
        self.saturation_slider = self.create_slider("Насыщенность", self.adjust_saturation)
        self.saturation_label = QLabel("Насыщенность: 0", self)
        self.saturation_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.saturation_label.setFixedSize(100, 20)  # Фиксированный размер: ширина 100, высота 20

        # Гаммма
        self.gamma_slider = self.create_slider("Гамма", self.adjust_gamma)
        self.gamma_label = QLabel("Гамма: 0", self)
        self.gamma_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.gamma_label.setFixedSize(100, 20)  # Фиксированный размер: ширина 100, высота 20

        # Кнопки
        self.rotate_button = QPushButton("Повернуть", self)
        self.rotate_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.rotate_button.clicked.connect(self.rotate_image)

        self.grayscale_button = QPushButton("Серый оттенок", self)
        self.grayscale_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.grayscale_button.clicked.connect(self.apply_grayscale)

        self.save_button = QPushButton("Сохранить изображение", self)
        self.save_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.save_button.clicked.connect(self.save_image)

        self.back_to_menu_button = QPushButton("Вернуться в меню", self)
        self.back_to_menu_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.back_to_menu_button.clicked.connect(self.back_to_menu)
 
        self.reset_button = QPushButton("Сбросить изменения", self)
        self.reset_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.reset_button.clicked.connect(self.reset_image)

        # Размещение инструментов в вертикальном порядке
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.open_button)

        # Яркость
        controls_layout.addWidget(self.brightness_label)
        controls_layout.addSpacing(5)  # Отступ 5 пикселей  
        controls_layout.addWidget(self.brightness_slider)

        # Контрастность
        controls_layout.addWidget(self.contrast_label)  # Метка сверху
        controls_layout.addSpacing(5)  # Отступ 5 пикселей
        controls_layout.addWidget(self.contrast_slider)

        # Насыщенность
        controls_layout.addWidget(self.saturation_label)  # Метка сверху
        controls_layout.addSpacing(5)  # Отступ 5 пикселей
        controls_layout.addWidget(self.saturation_slider)


        # Гамма
        controls_layout.addWidget(self.gamma_label)  # Метка сверху
        controls_layout.addSpacing(5)  # Отступ 5 пикселей
        controls_layout.addWidget(self.gamma_slider)

        controls_layout.addWidget(self.rotate_button)
        controls_layout.addWidget(self.grayscale_button)
        controls_layout.addWidget(self.save_button)
        controls_layout.addWidget(self.back_to_menu_button)
        controls_layout.addWidget(self.reset_button)

        controls_group = QGroupBox("Настройки изображения", self)
        controls_group.setStyleSheet("border: 2px solid #FF8C00; background-color: #333;")
        controls_group.setLayout(controls_layout)

        # Главное окно с изображением и панелью инструментов
        main_layout = QHBoxLayout()
        main_layout.addWidget(self.image_label, 2)
        main_layout.addWidget(controls_group, 1)

        container = QWidget(self)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.image = None
        self.original_image = None
        self.modified_image = None

        self.center()

    def center(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def create_slider(self, label, function):
        slider = QSlider(Qt.Orientation.Horizontal, self)
        slider.setMinimum(-100)
        slider.setMaximum(100)
        slider.setValue(0)
        slider.setStyleSheet("background-color: #555;")
        slider.valueChanged.connect(function)
        slider_label = QLabel(label, self)
        slider_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return slider

    def load_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "", "Изображения (*.png *.jpg *.bmp)")
        if file_path:
            self.original_image = cv2.imread(file_path)
            self.original_image = cv2.cvtColor(self.original_image, cv2.COLOR_BGR2RGB)
            self.image = self.original_image.copy()
            self.modified_image = self.original_image.copy()
            self.display_image()

    def display_image(self):
        if self.image is not None:
            height, width, channel = self.image.shape
            bytes_per_line = 3 * width
            q_image = QImage(self.image.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(q_image)
            pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio)  # Масштабируем изображение
            self.image_label.setPixmap(pixmap)

    def adjust_brightness(self, value):
        if self.original_image is not None:
            hsv = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            v = np.clip(v.astype(np.int16) + value, 0, 255).astype(np.uint8)
            hsv = cv2.merge([h, s, v])
            self.image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            self.display_image()
        self.brightness_label.setText(f"Яркость: {value}")  

    def adjust_contrast(self, value):
        if self.original_image is not None:
            alpha = 1 + value / 100.0
            beta = 0
            self.image = cv2.convertScaleAbs(self.original_image, alpha=alpha, beta=beta)
            self.display_image()
        self.contrast_label.setText(f"Контрастность: {value}")

    def adjust_saturation(self, value):
        if self.original_image is not None:
            hsv = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2HSV)
            h, s, v = cv2.split(hsv)
            s = np.clip(s.astype(np.int16) + value, 0, 255).astype(np.uint8)
            hsv = cv2.merge([h, s, v])
            self.image = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
            self.display_image()
        self.saturation_label.setText(f"Насыщенность: {value}")

    def adjust_gamma(self, value):
        if self.original_image is not None:
            gamma = 1 + value / 100.0
            look_up_table = np.array([((i / 255.0) ** gamma) * 255 for i in range(256)], dtype=np.uint8)
            self.image = cv2.LUT(self.original_image, look_up_table)
            self.display_image()
        self.gamma_label.setText(f"Гамма: {value}") 


    def rotate_image(self):
        if self.image is not None:
            self.image = cv2.rotate(self.image, cv2.ROTATE_90_CLOCKWISE)  
            self.display_image()

    def apply_grayscale(self):
        if self.original_image is not None:
            self.image = cv2.cvtColor(self.original_image, cv2.COLOR_RGB2GRAY)
            self.image = cv2.cvtColor(self.image, cv2.COLOR_GRAY2RGB)  # Возвращаем изображение в цветной формат
            self.display_image()

    def save_image(self):
        if self.image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить изображение", "", "Изображения (*.png *.jpg *.bmp)")
            if file_path:
                cv2.imwrite(file_path, cv2.cvtColor(self.image, cv2.COLOR_RGB2BGR))

    def back_to_menu(self):
        self.hide()  # Скрыть текущее окно редактора
        self.parent().show()  # Показать главное меню

    def reset_image(self):
        if self.original_image is not None:
            self.image = self.original_image.copy()  # Сбрасываем изображение к оригиналу
            self.display_image()

            # Сбрасываем слайдеры в исходное положение
            self.brightness_slider.setValue(0)
            self.contrast_slider.setValue(0)
            self.saturation_slider.setValue(0)
            self.gamma_slider.setValue(0)

class VideoEditor(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Видеоредактор")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #2E2E2E; color: white;")

        # Виджеты
        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.video_label.setStyleSheet("border: 2px solid #FF8C00; background-color: #444;")

        # Кнопки управления
        self.open_button = QPushButton("Открыть видео", self)
        self.open_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.open_button.clicked.connect(self.open_video)

        self.play_button = QPushButton("Воспроизвести", self)
        self.play_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.play_button.clicked.connect(self.play_video)

        self.pause_button = QPushButton("Пауза", self)
        self.pause_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.pause_button.clicked.connect(self.pause_video)

        # Кнопка "Сохранить изменённое видео"
        self.save_video_button = QPushButton("Сохранить изменённое видео", self)
        self.save_video_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.save_video_button.clicked.connect(self.save_video)

        # Кнопка "Вернуться в меню"
        self.back_to_menu_button = QPushButton("Вернуться в меню", self)
        self.back_to_menu_button.setStyleSheet("background-color: #FF8C00; padding: 5px 10px; border-radius: 5px; color: white;")
        self.back_to_menu_button.clicked.connect(self.back_to_menu)

        # Слайдер для перемотки видео
        self.slider = QSlider(Qt.Orientation.Horizontal, self)
        self.slider.setRange(0, 100)
        self.slider.setValue(0)
        self.slider.setStyleSheet("background-color: #555;")
        self.slider.sliderMoved.connect(self.set_video_position)

        # Таймер для обновления видео
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)

        # Медиаплеер для воспроизведения звука
        self.media_player = QMediaPlayer(self)
        self.audio_output = QAudioOutput(self)
        self.media_player.setAudioOutput(self.audio_output)

        # Переменные для работы с видео
        self.cap = None
        self.video_frames = []
        self.current_frame = 0
        self.is_playing = False
        self.playback_speed = 1.0  # Скорость воспроизведения

        # Фильтры
        self.filter_combo = QComboBox(self)
        self.filter_combo.addItems(["Без фильтра", "Чёрно-белый", "Сепия", "Негатив"])
        self.filter_combo.setStyleSheet("background-color: #555; color: white; padding: 5px;")
        self.filter_combo.currentTextChanged.connect(self.apply_filter)

        # Скорость воспроизведения
        self.speed_combo = QComboBox(self)
        self.speed_combo.addItems(["1x", "2x", "0.5x"])
        self.speed_combo.setStyleSheet("background-color: #555; color: white; padding: 5px;")
        self.speed_combo.currentTextChanged.connect(self.change_speed)

        # Размещение виджетов
        controls_layout = QVBoxLayout()
        controls_layout.addWidget(self.open_button)
        controls_layout.addWidget(self.play_button)
        controls_layout.addWidget(self.pause_button)
        controls_layout.addWidget(self.save_video_button)  # Кнопка "Сохранить изменённое видео"
        controls_layout.addWidget(self.slider)
        controls_layout.addWidget(self.filter_combo)
        controls_layout.addWidget(self.speed_combo)
        controls_layout.addWidget(self.back_to_menu_button)  # Кнопка "Вернуться в меню"

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.video_label, 2)
        main_layout.addLayout(controls_layout, 1)

        container = QWidget(self)
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        self.center()

    def center(self):
        screen_geometry = QApplication.primaryScreen().geometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def open_video(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть видео", "", "Видео (*.mp4 *.avi *.mov)")
        if file_path:
            self.cap = cv2.VideoCapture(file_path)
            self.video_frames = []
            self.current_frame = 0
            self.is_playing = False
            self.timer.stop()

            # Загружаем все кадры видео
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    break
                self.video_frames.append(frame)

            # Устанавливаем слайдер
            self.slider.setRange(0, len(self.video_frames) - 1)
            self.slider.setValue(0)

            # Показываем первый кадр
            self.show_frame(self.video_frames[0])

            # Загружаем звук, но не воспроизводим его сразу
            self.media_player.setSource(QUrl.fromLocalFile(file_path))
            self.media_player.pause()  # Звук не запускается автоматически

    def show_frame(self, frame):
        # Применяем фильтр
        frame = self.apply_filter_to_frame(frame)

        # Преобразуем BGR в RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        height, width, channel = frame_rgb.shape
        bytes_per_line = 3 * width
        q_image = QImage(frame_rgb.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        pixmap = pixmap.scaled(800, 600, Qt.AspectRatioMode.KeepAspectRatio)
        self.video_label.setPixmap(pixmap)

    def play_video(self):
        if self.video_frames and not self.is_playing:
            self.is_playing = True
            self.timer.start(int(30 / self.playback_speed))  # Учитываем скорость воспроизведения
            self.media_player.play()

    def pause_video(self):
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            self.media_player.pause()

    def update_frame(self):
        if self.current_frame < len(self.video_frames) - 1:
            self.current_frame += 1
            self.slider.setValue(self.current_frame)
            self.show_frame(self.video_frames[self.current_frame])
        else:
            self.timer.stop()
            self.is_playing = False

    def set_video_position(self, position):
        if self.video_frames:
            self.current_frame = position
            self.show_frame(self.video_frames[self.current_frame])
            self.media_player.setPosition(int(self.current_frame / len(self.video_frames) * self.media_player.duration()))

    def apply_filter(self):
        # Применяем фильтр к текущему кадру
        if self.video_frames:
            self.show_frame(self.video_frames[self.current_frame])

    def apply_filter_to_frame(self, frame):
        filter_type = self.filter_combo.currentText()
        if filter_type == "Чёрно-белый":
            return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        elif filter_type == "Сепия":
            kernel = np.array([[0.272, 0.534, 0.131],
                              [0.349, 0.686, 0.168],
                              [0.393, 0.769, 0.189]])
            return cv2.transform(frame, kernel)
        elif filter_type == "Негатив":
            return 255 - frame
        else:
            return frame

    def change_speed(self):
        speed_text = self.speed_combo.currentText()
        if speed_text == "1x":
            self.playback_speed = 1.0
        elif speed_text == "2x":
            self.playback_speed = 2.0
        elif speed_text == "0.5x":
            self.playback_speed = 0.5

        # Устанавливаем скорость воспроизведения звука
        self.media_player.setPlaybackRate(self.playback_speed)

        if self.is_playing:
            self.timer.start(int(30 / self.playback_speed))  # Обновляем таймер с новой скоростью

    def save_video(self):
        """Сохраняет видео с учётом:
        - Применённых фильтров (если они есть).
        - Оригинального звука (если скорость = 1.0).
        - Изменённой скорости (видео+аудио, если скорость ≠ 1.0).
        """
        try:
            # Проверка данных
            if not hasattr(self, 'video_frames') or not self.video_frames:
                QMessageBox.warning(self, "Ошибка", "Нет данных для сохранения!")
                return

            # Диалог сохранения
            default_path = os.path.join(os.path.expanduser("~"), "Desktop", "output.mp4")
            file_path, _ = QFileDialog.getSaveFileName(
                self, "Сохранить видео", default_path, "Видео (*.mp4)"
            )
            if not file_path:
                return

            # Временная папка
            temp_dir = tempfile.mkdtemp(prefix='video_edit_')
            temp_video = os.path.join(temp_dir, "video.mp4")
            temp_audio = os.path.join(temp_dir, "audio.aac")

            # Параметры видео
            height, width = self.video_frames[0].shape[:2]
            fps = int(self.cap.get(cv2.CAP_PROP_FPS)) if hasattr(self, 'cap') else 30

            # Сохраняем кадры с применением фильтров (если они есть)
            writer = cv2.VideoWriter(
                temp_video,
                cv2.VideoWriter_fourcc(*'mp4v'),
                fps,
                (width, height)
            )
            for frame in self.video_frames:
                # Применяем фильтры, если они заданы
                if hasattr(self, 'apply_filter_to_frame'):
                    frame = self.apply_filter_to_frame(frame)  # Ваш метод обработки кадров
                writer.write(frame)
            writer.release()

            # Если скорость не изменена (1.0) — копируем оригинальное аудио
            if not hasattr(self, 'playback_speed') or self.playback_speed == 1.0:
                subprocess.run([
                    'ffmpeg',
                    '-y',
                    '-i', temp_video,
                    '-i', self.media_player.source().toLocalFile(),
                    '-c:v', 'libx264',  # Перекодируем видео (чтобы применить фильтры)
                    '-c:a', 'copy',     # Аудио без изменений
                    '-map', '0:v',
                    '-map', '1:a',
                    '-preset', 'fast',
                    file_path
                ], check=True)
            
            # Если скорость изменена — обрабатываем видео и аудио
            else:
                # Извлекаем аудио
                subprocess.run([
                    'ffmpeg',
                    '-y',
                    '-i', self.media_player.source().toLocalFile(),
                    '-vn',
                    '-c:a', 'aac',
                    temp_audio
                ], check=True)

                # Применяем скорость и фильтры (уже применены к кадрам)
                subprocess.run([
                    'ffmpeg',
                    '-y',
                    '-i', temp_video,
                    '-i', temp_audio,
                    '-filter_complex',
                    f'[0:v]setpts={1/self.playback_speed}*PTS[v];[1:a]atempo={self.playback_speed}[a]',
                    '-map', '[v]',
                    '-map', '[a]',
                    '-c:v', 'libx264',
                    '-c:a', 'aac',
                    '-preset', 'fast',
                    file_path
                ], check=True)

            QMessageBox.information(self, "Готово", f"Видео сохранено: {file_path}")

        except subprocess.CalledProcessError as e:
            QMessageBox.critical(self, "Ошибка FFmpeg", f"Ошибка:\n{e.stderr.decode('utf-8')}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить видео:\n{str(e)}")
        finally:
            if 'temp_dir' in locals():
                shutil.rmtree(temp_dir, ignore_errors=True)

    def back_to_menu(self):
        self.hide() 
        self.parent().show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_menu = MainMenu()
    main_menu.show()
    sys.exit(app.exec())