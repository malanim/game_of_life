import tkinter as tk

class GridVisualization:
    def __init__(self, size):
        self.size = size
        self.camera_x = 0
        self.camera_y = 0
        self.target_camera_x = 0
        self.target_camera_y = 0
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=size*20, height=size*20)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Параметры масштабирования
        self.scale = 1.0
        self.target_scale = 1.0
        self.min_scale = 0.25
        self.max_scale = 10.0
        self.cell_base_size = 20
        self.zoom_smoothness = 0.15  # Коэффициент плавности зума
        
        # Привязываем обработчик изменения размера окна
        self.window.bind("<Configure>", self.on_window_resize)
        self.draw_grid()
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)  # Windows
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)    # Linux up
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)    # Linux down
        
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
        self.last_x = event.x
        self.last_y = event.y

    def drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y
        self.camera_x -= dx  # Инвертируем движение по оси X
        self.camera_y -= dy  # Инвертируем движение по оси Y
        self.last_x = event.x
        self.last_y = event.y
        self.draw_grid()  # Redraw the grid with the new camera position

    def stop_drag(self, event):
        pass  # You can add any additional logic here if needed
        
    def on_window_resize(self, event):
        # Перерисовываем сетку при изменении размера окна
        self.draw_grid()

    def on_mouse_wheel(self, event):
        # Определяем направление прокрутки
        if event.num == 5 or event.delta < 0:  # прокрутка вниз
            zoom_factor = 0.9
        else:  # прокрутка вверх
            zoom_factor = 1.1
            
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
            
            # Плавное изменение положения камеры
            self.camera_x += (self.target_camera_x - self.camera_x) * self.zoom_smoothness
            self.camera_y += (self.target_camera_y - self.camera_y) * self.zoom_smoothness
            
            self.draw_grid()
        
        # Планируем следующий кадр анимации
        self.window.after(16, self.animate_zoom)  # примерно 60 FPS
        
    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    grid_size = 32  # Size of the grid
    grid_visualization = GridVisualization(grid_size)
    grid_visualization.run()
