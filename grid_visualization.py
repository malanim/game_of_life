import tkinter as tk

class GridVisualization:
    def __init__(self, size):
        self.size = size
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.window = tk.Tk()
        self.window.title("Game of Life (F1 - открыть меню)")
        
        # Флаг для отслеживания состояния всплывающего окна
        self.popup_visible = False
        
        self.canvas = tk.Canvas(self.window, width=size*20, height=size*20)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Параметры масштабирования
        self.scale = 1.0
        self.target_scale = 1.0
        self.min_scale = 0.25
        self.max_scale = 10.0
        self.cell_base_size = 20
        self.zoom_smoothness = 0.15  # Коэффициент плавности зума
        self.zoom_speed = 0.1  # Коэффициент скорости масштабирования (0.1 = медленно, 0.5 = быстро)
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

    def draw_grid(self):
        self.canvas.delete("all")  # Clear the canvas
        # Получаем текущие размеры canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Текущий размер ячейки с учетом масштаба
        cell_size = self.cell_base_size * self.scale
        
        # Рисуем сетку с учетом текущих размеров и масштаба
        for i in range(self.size):
            # Vertical lines
            x_pos = i * cell_size - self.camera_x
            self.canvas.create_line(x_pos, 0, 
                                  x_pos, canvas_height, 
                                  fill="gray")
            # Horizontal lines
            y_pos = i * cell_size - self.camera_y
            self.canvas.create_line(0, y_pos, 
                                  canvas_width, y_pos, 
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
        self.window.after(8, self.animate_zoom)  # примерно 60 FPS
        
    def run(self):
        self.window.mainloop()

    def toggle_popup(self, event=None):
        if self.popup_visible:
            self.close_popup()
        else:
            self.show_popup()

    def show_popup(self):
        # Создаем полупрозрачный затемняющий фон
        self.overlay = tk.Canvas(self.window)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.overlay.configure(bg='black')
        # Устанавливаем прозрачность через создание прямоугольника
        self.overlay.create_rectangle(0, 0, 10000, 10000, fill='black', stipple='gray50')
        # Добавляем обработчик клика по затемненной области
        self.overlay.bind("<Button-1>", lambda e: self.close_popup())

        # Создаем всплывающее окно
        self.popup = tk.Frame(self.window, bg='white', bd=2, relief='raised')
        self.popup.place(relx=0.5, rely=0.5, anchor='center', relwidth=0.4, relheight=0.3)

        # Создаем заголовок всплывающего окна
        title_frame = tk.Frame(self.popup, bg='#e1e1e1', height=30)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Меню", bg='#e1e1e1', font=('Arial', 10, 'bold'))
        title_label.pack(side='left', padx=10)
        
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

        self.popup_visible = True

    def close_popup(self):
        if hasattr(self, 'overlay'):
            self.overlay.destroy()
        if hasattr(self, 'popup'):
            self.popup.destroy()
        self.popup_visible = False

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
    grid_size = 32  # Size of the grid
    visualization = GridVisualization(grid_size)
    visualization.run()
