import tkinter as tk
import params

class Rescale_window:
    def __init__(self,
                 init_width,
                 init_height):
        self.root = tk.Tk()
        self.root.title('Rescale canvas')
        
        scales_frame = tk.Frame(self.root, bg='white')
        scales_frame.grid(row=0, column=0, columnspan=1, sticky='nw')
        self.canvas_width_scale = tk.Scale(scales_frame,
                                           from_=64,
                                           to=2048,
                                           resolution=64,
                                           command=None,
                                           label='Canvas width',
                                           length=200,
                                           orient=tk.HORIZONTAL,
                                           bg='white')
        self.canvas_width_scale.grid(row=0, column=0, columnspan=1, sticky='nw')
        self.canvas_width_scale.set(init_width)
        
        self.canvas_height_scale = tk.Scale(scales_frame,
                                            from_=64,
                                            to=2048,
                                            resolution=64,
                                            command=None,
                                            label='Canvas height',
                                            length=200,
                                            orient=tk.HORIZONTAL,
                                            bg='white')
        self.canvas_height_scale.grid(row=0, column=1, columnspan=1, sticky='nw')
        self.canvas_height_scale.set(init_height)
        
        buttons_frame = tk.Frame(self.root, bg='white')
        buttons_frame.grid(row=1, column=0,sticky='ne')
        cancel_button = tk.Button(buttons_frame, text='Cancel', command=self.cancel)
        cancel_button.grid(column=0, row=0, sticky='ne')
        accept_button = tk.Button(buttons_frame, text='Accept', command=self.accept)
        accept_button.grid(column=1, row=0, sticky='ne')
        
        
        self.accepted = False
        self.width, self.height = None, None
        
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        self.root.mainloop()
    
    def cancel(self):
        self.accepted = False
        self.root.quit()
        self.root.destroy()
    
    def accept(self):
        self.width = self.canvas_width_scale.get()
        self.height = self.canvas_height_scale.get()
        self.accepted = True
        self.root.quit()
        self.root.destroy()


if __name__ == '__main__':
    rw = Rescale_window(512, 512)
    rw()