import tkinter as tk
from tkinter import ttk

class GridVisualization:
    def __init__(self, size):
        self.size = size
        self.camera_x = 0
        self.camera_y = 0
        self.cell_colors = [[None for _ in range(size)] for _ in range(size)]  # Инициализация массива цветов
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.window = tk.Tk()
        self.window.title("Game of Life (F1 - открыть меню)")
        
        # Флаг для отслеживания состояния всплывающего окна
        self.popup_visible = False
        
        # Размер одной ячейки
        self.cell_base_size = 20

        self.canvas = tk.Canvas(self.window, width=size*self.cell_base_size, height=size*self.cell_base_size)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Параметры масштабирования
        self.scale = 1.0
        self.target_scale = 1.0
        self.min_scale = 1.0
        self.max_scale = 10.0
        self.zoom_smoothness = 0.085  # Коэффициент плавности зума
        self.zoom_speed = 0.4  # Коэффициент скорости масштабирования (0.1 = медленно, 0.5 = быстро)
        self.dragging = False  # Инициализируем состояние перетаскивания
        
        # Привязываем обработчик изменения размера окна
        self.window.bind("<Configure>", self.on_window_resize)
        self.draw_grid()
        
        # Bind mouse events and keyboard
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux down
        self.window.bind("<F1>", self.toggle_popup)  # Добавляем обработку F1
        self.window.bind("<Escape>", lambda e: self.close_popup() if self.popup_visible else None)  # Закрытие по Escape
        
        # Анимация масштабирования
        self.animate_zoom()

    def set_cell_colors(self, colors):
        """Установка цветов для ячеек сетки"""
        if len(colors) != self.size or any(len(row) != self.size for row in colors):
            raise ValueError(f"Размер массива цветов должен быть {self.size}x{self.size}")
        self.cell_colors = colors
        self.draw_grid()

    def draw_grid(self):
        self.canvas.delete("all")  # Clear the canvas
        # Получаем текущие размеры canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Текущий размер ячейки с учетом масштаба
        cell_size = self.cell_base_size * self.scale
        
        # Сначала рисуем цветные ячейки
        # Добавляем дополнительный ряд ячеек слева и сверху для плавного перехода
        for i in range(-1, self.size):
            for j in range(-1, self.size):
                # Заворачиваем координаты для бесконечного поля
                wrapped_i = i % self.size
                wrapped_j = j % self.size
                wrapped_x = (i * cell_size - self.camera_x) % (self.size * cell_size)
                wrapped_y = (j * cell_size - self.camera_y) % (self.size * cell_size)
                
                # Если для ячейки задан цвет, рисуем её
                if self.cell_colors[wrapped_j][wrapped_i] is not None:
                    # Рисуем основную ячейку
                    self.canvas.create_rectangle(
                        wrapped_x, wrapped_y,
                        wrapped_x + cell_size, wrapped_y + cell_size,
                        fill=self.cell_colors[wrapped_j][wrapped_i],
                        outline=""
                    )
                    
                    # Дублируем ячейки на границах для плавного перехода
                    if wrapped_x + cell_size > self.size * cell_size:
                        self.canvas.create_rectangle(
                            wrapped_x - self.size * cell_size, wrapped_y,
                            wrapped_x - self.size * cell_size + cell_size, wrapped_y + cell_size,
                            fill=self.cell_colors[wrapped_j][wrapped_i],
                            outline=""
                        )
                        # Добавляем дублирование для левого верхнего угла
                        if wrapped_y + cell_size > self.size * cell_size:
                            self.canvas.create_rectangle(
                                wrapped_x - self.size * cell_size, wrapped_y - self.size * cell_size,
                                wrapped_x - self.size * cell_size + cell_size, wrapped_y - self.size * cell_size + cell_size,
                                fill=self.cell_colors[wrapped_j][wrapped_i],
                                outline=""
                            )
                    if wrapped_y + cell_size > self.size * cell_size:
                        self.canvas.create_rectangle(
                            wrapped_x, wrapped_y - self.size * cell_size,
                            wrapped_x + cell_size, wrapped_y - self.size * cell_size + cell_size,
                            fill=self.cell_colors[wrapped_j][wrapped_i],
                            outline=""
                        )
        
        # Затем рисуем линии сетки поверх ячеек
        # Добавляем дополнительные линии для плавного перехода
        for i in range(-1, self.size + 1):
            # Заворачиваем координаты для бесконечного поля
            wrapped_x = (i * cell_size - self.camera_x) % (self.size * cell_size)
            wrapped_y = (i * cell_size - self.camera_y) % (self.size * cell_size)
            
            # Vertical lines
            self.canvas.create_line(wrapped_x, 0, 
                                  wrapped_x, canvas_height, 
                                  fill="gray")
            # Horizontal lines
            self.canvas.create_line(0, wrapped_y, 
                                  canvas_width, wrapped_y, 
                                  fill="gray")

    def start_drag(self, event):
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y

    def drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        # Обновляем как текущие, так и целевые координаты камеры
        self.camera_x -= dx  # Инвертируем движение по оси X
        self.camera_y -= dy  # Инвертируем движение по оси Y
        self.target_camera_x = self.camera_x  # Синхронизируем целевые координаты
        self.target_camera_y = self.camera_y
        
        self.last_x = event.x
        self.last_y = event.y
        self.draw_grid()  # Redraw the grid with the new camera position

    def stop_drag(self, event):
        self.dragging = False
        
    def on_window_resize(self, event):
        # Перерисовываем сетку при изменении размера окна
        self.draw_grid()

    def on_mouse_wheel(self, event):
        # Определяем направление прокрутки
        if event.num == 5 or event.delta < 0:  # прокрутка вниз
            zoom_factor = 1.0 - self.zoom_speed
        else:  # прокрутка вверх
            zoom_factor = 1.0 + self.zoom_speed
            
        # Получаем позицию мыши
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        
        # Рассчитываем новый масштаб
        new_scale = min(max(self.scale * zoom_factor, self.min_scale), self.max_scale)
        
        if new_scale != self.scale:
            # Сохраняем позицию курсора относительно центра до масштабирования
            self.target_scale = new_scale
            
            # Рассчитываем целевое положение камеры
            scale_factor = (new_scale / self.scale) - 1
            self.target_camera_x = self.camera_x + (mouse_x + self.camera_x) * scale_factor
            self.target_camera_y = self.camera_y + (mouse_y + self.camera_y) * scale_factor
    
    def animate_zoom(self):
        # Плавное изменение масштаба
        if abs(self.target_scale - self.scale) > 0.001:
            self.scale += (self.target_scale - self.scale) * self.zoom_smoothness
            
            # Плавное изменение положения камеры только если не перетаскиваем
            if not self.dragging:
                self.camera_x += (self.target_camera_x - self.camera_x) * self.zoom_smoothness
                self.camera_y += (self.target_camera_y - self.camera_y) * self.zoom_smoothness
            
            self.draw_grid()
        
        # Планируем следующий кадр анимации
        self.window.after(8, self.animate_zoom)  # примерно 120 FPS
        
    def run(self):
        self.window.mainloop()

    def toggle_popup(self, event=None):
        if self.popup_visible:
            self.close_popup()
        else:
            self.show_popup()

    def show_popup(self):
        # Создаем полупрозрачный затемняющий фон
        self.overlay = tk.Toplevel(self.window)
        self.overlay.overrideredirect(True)  # Убираем заголовок окна
        self.overlay.attributes('-topmost', True)  # Держим оверлей поверх всех окон
        
        # Получаем координаты и размеры основного окна
        x = self.window.winfo_rootx()
        y = self.window.winfo_rooty()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        # Устанавливаем положение и размер оверлея точно по размеру основного окна
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        # Создаем черный фон с прозрачностью
        overlay_canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='black')
        overlay_canvas.pack(fill='both', expand=True)
        self.overlay.attributes('-alpha', 0.5)  # Устанавливаем прозрачность
        
        # Добавляем обработчик клика по затемненной области
        overlay_canvas.bind("<Button-1>", lambda e: self.close_popup())
        
        # Обновляем положение оверлея при перемещении основного окна
        def update_overlay_position(event=None):
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                x = self.window.winfo_rootx()
                y = self.window.winfo_rooty()
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        # Привязываем обновление позиции к событиям перемещения и изменения размера окна
        self.window.bind('<Configure>', lambda e: (update_overlay_position(), self.update_popup_position()))

        # Создаем всплывающее окно
        self.popup = tk.Toplevel(self.window)
        self.popup.withdraw()  # Скрываем окно на время настройки
        self.popup.transient(self.window)
        self.popup.attributes('-topmost', True)  # Держим окно поверх всех окон
        self.popup.overrideredirect(True)  # Убираем стандартное оформление окна
        self.popup.configure(bg='white')
        
        # Устанавливаем начальное положение окна
        self.update_popup_position()
        
        # Создаем интерфейс всплывающего окна
        # Создаем заголовок с возможностью перетаскивания
        title_frame = tk.Frame(self.popup, bg='#e1e1e1', height=30)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Меню", bg='#e1e1e1', font=('Arial', 10, 'bold'))
        title_label.pack(side='left', padx=10)
        
        # Добавляем обработчики перетаскивания окна
        title_frame.bind('<Button-1>', self.start_window_drag)
        title_frame.bind('<B1-Motion>', self.window_drag)
        title_frame.bind('<ButtonRelease-1>', self.stop_window_drag)
        title_label.bind('<Button-1>', self.start_window_drag)
        title_label.bind('<B1-Motion>', self.window_drag)
        title_label.bind('<ButtonRelease-1>', self.stop_window_drag)
        
        # Добавляем кнопку закрытия в заголовок
        close_button = tk.Button(title_frame, text="×", 
                               command=self.close_popup,
                               font=('Arial', 12),
                               bg='#e1e1e1',
                               relief='flat',
                               width=2,
                               highlightthickness=0,
                               bd=0,
                               activebackground='#ff5555',  # Цвет при наведении
                               cursor='hand2')  # Курсор в виде руки при наведении
        close_button.pack(side='right', padx=5)
        
        # Добавляем кнопку настроек во всплывающее окно
        content_frame = tk.Frame(self.popup, bg='white')
        content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        settings_button = tk.Button(content_frame, text="Настройки", 
                                  command=self.open_settings,
                                  relief='flat',
                                  bg='#4a90e2',
                                  fg='white',
                                  activebackground='#357abd',
                                  activeforeground='white',
                                  width=20,
                                  cursor='hand2',
                                  font=('Arial', 10),
                                  pady=8)
        settings_button.pack(pady=10)
        
        # Добавляем подсказку внизу окна
        hint_label = tk.Label(content_frame, 
                            text="ESC или клик вне окна для закрытия",
                            bg='white',
                            fg='#666666',
                            font=('Arial', 8))
        hint_label.pack(side='bottom', pady=(0, 5))

        # После создания всего интерфейса показываем окно
        self.window.after(100, lambda: (
            self.popup.deiconify(),  # Показываем окно
            self.popup.lift(),  # Поднимаем окно поверх всех остальных
            setattr(self, 'popup_visible', True)
        ))

    def close_popup(self):
        if hasattr(self, 'overlay'):
            self.overlay.destroy()
        if hasattr(self, 'popup'):
            self.popup.destroy()
        self.popup_visible = False

    def start_window_drag(self, event):
        self._drag_start_x = event.x_root - self.popup.winfo_x()
        self._drag_start_y = event.y_root - self.popup.winfo_y()

    def window_drag(self, event):
        if hasattr(self, '_drag_start_x'):
            x = event.x_root - self._drag_start_x
            y = event.y_root - self._drag_start_y
            self.popup.geometry(f"+{x}+{y}")
            
    def stop_window_drag(self, event):
        if hasattr(self, '_drag_start_x'):
            delattr(self, '_drag_start_x')
            delattr(self, '_drag_start_y')

    def update_popup_position(self):
        if hasattr(self, 'popup') and self.popup.winfo_exists():
            x = self.window.winfo_rootx()
            y = self.window.winfo_rooty()
            width = self.window.winfo_width()
            height = self.window.winfo_height()
            popup_width = int(width * 0.4)
            popup_height = int(height * 0.3)
            popup_x = x + (width - popup_width) // 2
            popup_y = y + (height - popup_height) // 2
            self.popup.geometry(f"{popup_width}x{popup_height}+{popup_x}+{popup_y}")

    def open_settings(self):
        self.close_popup()  # Закрываем всплывающее окно
        # Создаем новое окно настроек
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Настройки масштабирования")
        settings_window.geometry("400x100")
        settings_window.resizable(False, False)
        settings_window.transient(self.window)  # Делаем окно зависимым от основного
        
        # Создаем фрейм для элементов управления
        frame = tk.Frame(settings_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Добавляем метку и слайдер
        tk.Label(frame, text="Скорость масштабирования:").pack(side=tk.LEFT)
        slider = tk.Scale(frame, from_=0.05, to=0.5, resolution=0.05,
                         orient=tk.HORIZONTAL,
                         command=lambda value: setattr(self, 'zoom_speed', float(value)))
        slider.set(self.zoom_speed)  # Устанавливаем текущее значение
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

if __name__ == "__main__":
    import random

    # Определяем набор доступных цветов
    available_colors = [
        "#FF0000",  # красный
        "#00FF00",  # зеленый
        "#0000FF",  # синий
        "#FFFF00",  # желтый
        "#FF00FF",  # пурпурный
        "#00FFFF",  # голубой
        None        # прозрачный
    ]
    
    # Создаем сетку размером grid_size
    grid_size = 16
    visualization = GridVisualization(grid_size)
    
    # Создаем массив случайных цветов для ячеек
    colors = []
    for i in range(grid_size):
        row = []
        for j in range(grid_size):
            row.append(random.choice(available_colors))
        colors.append(row)
    
    # Устанавливаем цвета ячеек
    visualization.set_cell_colors(colors)
    
    # Запускаем визуализацию
    visualization.run()
