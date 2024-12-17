import tkinter as tk
from tkinter import ttk
import numpy as np

class GridVisualization:
    def __init__(self, size):
        self.size = size
        self.camera_x = 0
        self.camera_y = 0
        # Используем NumPy массив вместо вложенных списков
        self.cell_colors = np.full((size, size), None, dtype=object)
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.window = tk.Tk()
        self.window.title("Game of Life (F1 - открыть меню)")
        
        self.popup_visible = False
        self.cell_base_size = 20

        self.canvas = tk.Canvas(self.window, width=size*self.cell_base_size, height=size*self.cell_base_size)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.scale = 1.0
        self.target_scale = 1.0
        self.min_scale = 1.0
        self.max_scale = 10.0
        self.zoom_smoothness = 0.085
        self.zoom_speed = 0.4
        self.dragging = False
        
        # Кэш для оптимизации
        self._cell_positions_cache = None
        self._last_camera_params = None
        
        self.window.bind("<Configure>", self.on_window_resize)
        self.draw_grid()
        
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux down
        self.window.bind("<F1>", self.toggle_popup)  # Добавляем обработку F1
        self.window.bind("<Escape>", lambda e: self.close_popup() if self.popup_visible else None)  # Закрытие по Escape
        
        self.animate_zoom()

    def set_cell_colors(self, colors):
        """Установка цветов для ячеек сетки с использованием NumPy"""
        colors_array = np.array(colors, dtype=object)
        if colors_array.shape != (self.size, self.size):
            raise ValueError(f"Размер массива цветов должен быть {self.size}x{self.size}")
        self.cell_colors = colors_array
        self.draw_grid()

    def _calculate_cell_positions(self):
        """Вычисление позиций ячеек с использованием векторизованных операций"""
        cell_size = self.cell_base_size * self.scale
        
        # Создаем сетку координат с помощью NumPy
        i = np.arange(-1, self.size)
        j = np.arange(-1, self.size)
        I, J = np.meshgrid(i, j)
        
        # Вычисляем координаты с учетом камеры
        wrapped_x = (I * cell_size - self.camera_x) % (self.size * cell_size)
        wrapped_y = (J * cell_size - self.camera_y) % (self.size * cell_size)
        
        return wrapped_x, wrapped_y, cell_size

    def draw_grid(self):
        self.canvas.delete("all")
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # Проверяем кэш
        current_params = (self.camera_x, self.camera_y, self.scale)
        if self._last_camera_params != current_params:
            self._last_camera_params = current_params
            self._cell_positions_cache = self._calculate_cell_positions()
        
        wrapped_x, wrapped_y, cell_size = self._cell_positions_cache
        
        # Отрисовка цветных ячеек с использованием векторизованных операций
        for i in range(wrapped_x.shape[0]):
            for j in range(wrapped_x.shape[1]):
                wrapped_i = i % self.size
                wrapped_j = j % self.size
                
                if self.cell_colors[wrapped_j, wrapped_i] is not None:
                    x, y = wrapped_x[i, j], wrapped_y[i, j]
                    
                    # Основная ячейка
                    self.canvas.create_rectangle(
                        x, y,
                        x + cell_size, y + cell_size,
                        fill=self.cell_colors[wrapped_j, wrapped_i],
                        outline=""
                    )
                    
                    # Дублирование на границах
                    if x + cell_size > self.size * cell_size:
                        self.canvas.create_rectangle(
                            x - self.size * cell_size, y,
                            x - self.size * cell_size + cell_size, y + cell_size,
                            fill=self.cell_colors[wrapped_j, wrapped_i],
                            outline=""
                        )
                        if y + cell_size > self.size * cell_size:
                            self.canvas.create_rectangle(
                                x - self.size * cell_size, y - self.size * cell_size,
                                x - self.size * cell_size + cell_size, y - self.size * cell_size + cell_size,
                                fill=self.cell_colors[wrapped_j, wrapped_i],
                                outline=""
                            )
                    if y + cell_size > self.size * cell_size:
                        self.canvas.create_rectangle(
                            x, y - self.size * cell_size,
                            x + cell_size, y - self.size * cell_size + cell_size,
                            fill=self.cell_colors[wrapped_j, wrapped_i],
                            outline=""
                        )
        
        # Отрисовка линий сетки
        for i in range(-1, self.size + 1):
            wrapped_x = (i * cell_size - self.camera_x) % (self.size * cell_size)
            wrapped_y = (i * cell_size - self.camera_y) % (self.size * cell_size)
            
            self.canvas.create_line(wrapped_x, 0, wrapped_x, canvas_height, fill="gray")
            self.canvas.create_line(0, wrapped_y, canvas_width, wrapped_y, fill="gray")

    def start_drag(self, event):
        self.dragging = True
        self.last_x = event.x
        self.last_y = event.y

    def drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        
        self.camera_x -= dx
        self.camera_y -= dy
        self.target_camera_x = self.camera_x
        self.target_camera_y = self.camera_y
        
        self.last_x = event.x
        self.last_y = event.y
        self.draw_grid()

    def stop_drag(self, event):
        self.dragging = False
        
    def on_window_resize(self, event):
        self.draw_grid()

    def on_mouse_wheel(self, event):
        if event.num == 5 or event.delta < 0:
            zoom_factor = 1.0 - self.zoom_speed
        else:
            zoom_factor = 1.0 + self.zoom_speed
            
        mouse_x = self.canvas.canvasx(event.x)
        mouse_y = self.canvas.canvasy(event.y)
        
        new_scale = np.clip(self.scale * zoom_factor, self.min_scale, self.max_scale)
        
        if new_scale != self.scale:
            self.target_scale = new_scale
            
            scale_factor = (new_scale / self.scale) - 1
            self.target_camera_x = self.camera_x + (mouse_x + self.camera_x) * scale_factor
            self.target_camera_y = self.camera_y + (mouse_y + self.camera_y) * scale_factor
    
    def animate_zoom(self):
        if abs(self.target_scale - self.scale) > 0.001:
            self.scale += (self.target_scale - self.scale) * self.zoom_smoothness
            
            if not self.dragging:
                self.camera_x += (self.target_camera_x - self.camera_x) * self.zoom_smoothness
                self.camera_y += (self.target_camera_y - self.camera_y) * self.zoom_smoothness
            
            self.draw_grid()
        
        self.window.after(8, self.animate_zoom)
        
    def run(self):
        self.window.mainloop()

    def toggle_popup(self, event=None):
        if self.popup_visible:
            self.close_popup()
        else:
            self.show_popup()

    def show_popup(self):
        self.overlay = tk.Toplevel(self.window)
        self.overlay.overrideredirect(True)
        self.overlay.attributes('-topmost', True)
        
        x = self.window.winfo_rootx()
        y = self.window.winfo_rooty()
        width = self.window.winfo_width()
        height = self.window.winfo_height()
        
        self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        overlay_canvas = tk.Canvas(self.overlay, highlightthickness=0, bg='black')
        overlay_canvas.pack(fill='both', expand=True)
        self.overlay.attributes('-alpha', 0.5)
        
        overlay_canvas.bind("<Button-1>", lambda e: self.close_popup())
        
        def update_overlay_position(event=None):
            if hasattr(self, 'overlay') and self.overlay.winfo_exists():
                x = self.window.winfo_rootx()
                y = self.window.winfo_rooty()
                width = self.window.winfo_width()
                height = self.window.winfo_height()
                self.overlay.geometry(f"{width}x{height}+{x}+{y}")
        
        self.window.bind('<Configure>', lambda e: (update_overlay_position(), self.update_popup_position()))

        self.popup = tk.Toplevel(self.window)
        self.popup.withdraw()
        self.popup.transient(self.window)
        self.popup.attributes('-topmost', True)
        self.popup.overrideredirect(True)
        self.popup.configure(bg='white')
        
        self.update_popup_position()
        
        title_frame = tk.Frame(self.popup, bg='#e1e1e1', height=30)
        title_frame.pack(fill='x', side='top')
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(title_frame, text="Меню", bg='#e1e1e1', font=('Arial', 10, 'bold'))
        title_label.pack(side='left', padx=10)
        
        title_frame.bind('<Button-1>', self.start_window_drag)
        title_frame.bind('<B1-Motion>', self.window_drag)
        title_frame.bind('<ButtonRelease-1>', self.stop_window_drag)
        title_label.bind('<Button-1>', self.start_window_drag)
        title_label.bind('<B1-Motion>', self.window_drag)
        title_label.bind('<ButtonRelease-1>', self.stop_window_drag)
        
        close_button = tk.Button(title_frame, text="×", 
                               command=self.close_popup,
                               font=('Arial', 12),
                               bg='#e1e1e1',
                               relief='flat',
                               width=2,
                               highlightthickness=0,
                               bd=0,
                               activebackground='#ff5555',
                               cursor='hand2')
        close_button.pack(side='right', padx=5)
        
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
        
        hint_label = tk.Label(content_frame, 
                            text="ESC или клик вне окна для закрытия",
                            bg='white',
                            fg='#666666',
                            font=('Arial', 8))
        hint_label.pack(side='bottom', pady=(0, 5))

        self.window.after(100, lambda: (
            self.popup.deiconify(),
            self.popup.lift(),
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
        self.close_popup()
        settings_window = tk.Toplevel(self.window)
        settings_window.title("Настройки масштабирования")
        settings_window.geometry("400x100")
        settings_window.resizable(False, False)
        settings_window.transient(self.window)
        
        frame = tk.Frame(settings_window)
        frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame, text="Скорость масштабирования:").pack(side=tk.LEFT)
        slider = tk.Scale(frame, from_=0.05, to=0.5, resolution=0.05,
                         orient=tk.HORIZONTAL,
                         command=lambda value: setattr(self, 'zoom_speed', float(value)))
        slider.set(self.zoom_speed)
        slider.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

if __name__ == "__main__":
    import random
    import numpy as np

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
    
    grid_size = 32
    visualization = GridVisualization(grid_size)
    
    # Используем NumPy для генерации случайных цветов
    colors = np.random.choice(available_colors, size=(grid_size, grid_size))
    
    visualization.set_cell_colors(colors)
    visualization.run()
