import tkinter as tk

class GridVisualization:
    def __init__(self, size):
        self.size = size
        self.camera_x = 0
        self.camera_y = 0
        self.window = tk.Tk()
        self.canvas = tk.Canvas(self.window, width=size*20, height=size*20)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Привязываем обработчик изменения размера окна
        self.window.bind("<Configure>", self.on_window_resize)
        self.draw_grid()
        
        # Bind mouse events
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def draw_grid(self):
        self.canvas.delete("all")  # Clear the canvas
        # Получаем текущие размеры canvas
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        # Рисуем сетку с учетом текущих размеров
        for i in range(self.size):
            # Vertical lines
            self.canvas.create_line(i * 20 - self.camera_x, 0, 
                                  i * 20 - self.camera_x, canvas_height, 
                                  fill="gray")
            # Horizontal lines
            self.canvas.create_line(0, i * 20 - self.camera_y, 
                                  canvas_width, i * 20 - self.camera_y, 
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

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    grid_size = 32  # Size of the grid
    grid_visualization = GridVisualization(grid_size)
    grid_visualization.run()
