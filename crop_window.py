import tkinter as tk
from PIL import Image, ImageOps, ImageTk

import params
import utils

class Crop_window:
    def __init__(self, img, box_width, box_height):
        self.root = tk.Tk()
        self.root.title('Crop image')
        
        self.img = img
        self.image_width, self.image_height = img.size
        self.box_width = box_width
        self.box_height = box_height
        
        min_scale = max(self.box_width / self.image_width,
                        self.box_height / self.image_height)
        max_offset_x = int(min_scale*self.image_width) - self.box_width
        max_offset_y = int(min_scale*self.image_height) - self.box_height
        
        scales_frame = tk.Frame(self.root, bg='white')
        scales_frame.grid(row=0, column=0, sticky='nw')
        self.offset_x_scale = tk.Scale(scales_frame,
                                       from_=0,
                                       to=max_offset_x,
                                       resolution=1,
                                       command=self._update,
                                       label='Offset x',
                                        length=200,
                                       orient=tk.HORIZONTAL,
                                       bg='white')
        self.offset_x_scale.grid(row=0, column=0, columnspan=1, sticky='nw')
        self.offset_y_scale = tk.Scale(scales_frame,
                                       from_=0,
                                       to=max_offset_y,
                                       resolution=1,
                                       command=self._update,
                                       label='Offset y',
                                       length=200,
                                       orient=tk.HORIZONTAL,
                                       bg='white')
        self.offset_y_scale.grid(row=0, column=1, columnspan=1, sticky='nw')
        self.scale_scale = tk.Scale(scales_frame,
                                    from_=min_scale,
                                    to=min_scale*10,
                                    resolution=min_scale*0.1,
                                    command=self._update,
                                    label='Scale',
                                    length=200,
                                    orient=tk.HORIZONTAL,
                                    bg='white')
        self.scale_scale.grid(row=0, column=3, columnspan=1, sticky='nw')
        self.scale_scale.set(min_scale)
        
        buttons_frame = tk.Frame(self.root, bg='white')
        buttons_frame.grid(row=1, column=0, sticky='nw')
        self.rotate_button = tk.Button(buttons_frame, text='rotate', command=self.rotate)
        self.rotate_button.grid(row=0, column=0, sticky='nw')
        
        self.canvas = tk.Canvas(self.root,
                                width=self.box_width,
                                height=self.box_height,
                                highlightthickness=1,
                                highlightbackground="black")
        self.canvas.grid(row=2, column=0, sticky='nw')
        
        self.canvas_image = ImageTk.PhotoImage(image=self.img,
                                               master=self.root)
        self.image_container = self.canvas.create_image(0, 0,
                                                        anchor='nw',
                                                        image=self.canvas_image)
        
        exit_frame = tk.Frame(self.root)
        exit_frame.grid(row=3, column=0, sticky='nw')
        
        self.reject_button = tk.Button(exit_frame, text='Reject', command=self.reject)
        self.reject_button.grid(row=0, column=0, sticky='nw')
        
        self.accept_button = tk.Button(exit_frame, text='Accept', command=self.accept)
        self.accept_button.grid(row=0, column=1, sticky='nw')
        
        self.accepted = False
        
        self._update()
    
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        utils.center(self.root)
        
        self.root.mainloop()
    
    def _update(self, *argv):
        scaling = self.scale_scale.get()
        offset_x = self.offset_x_scale.get()    
        offset_y = self.offset_y_scale.get()
        
        box = (offset_x,
               offset_y,
               offset_x + self.box_width,
               offset_y + self.box_height)
        
        background_image = self.img.resize((max(int(scaling*self.image_width), 1),
                                            max(int(scaling*self.image_height), 1)))
        self.cropped_image = background_image.crop(box=box)
        
        self.canvas_image = ImageTk.PhotoImage(image=self.cropped_image,
                                               master=self.root)
        self.canvas.itemconfig(self.image_container, image=self.canvas_image)
        
        max_offset_x = max(int(scaling*self.image_width - self.box_width), 0)
        max_offset_y = max(int(scaling*self.image_height - self.box_height), 0)
        
        if self.offset_x_scale.get() >= max_offset_x:
            self.offset_x_scale.set(max_offset_x)
        
        if self.offset_y_scale.get() >= max_offset_y:
            self.offset_y_scale.set(max_offset_y)
        
        self.offset_x_scale.config(to=max_offset_x)
        self.offset_y_scale.config(to=max_offset_y)
        # self.scale_scale.config()
    
    def rotate(self):
        self.img = self.img.rotate(angle=90, expand=True)
        self.image_width, self.image_height = self.img.size
        self.offset_x_scale.set(0)
        self.offset_y_scale.set(0)
        
        min_scale = max(self.box_width / self.image_width,
                        self.box_height / self.image_height)
        self.scale_scale.config(from_=min_scale)
        
        self._update()
    
    def reject(self):
        self.accepted = False
        
        self.root.quit()
        self.root.destroy()
    
    def accept(self):
        self.accepted = True
        
        self.root.quit()
        self.root.destroy()

if __name__=='__main__':
    # from tkinter import filedialog
    # img_path = filedialog.askopenfilename()
    # img = Image.open(img_path)
    import numpy as np
    img = Image.fromarray((np.random.rand(704, 512, 3) * 255).astype('uint8')).convert('RGBA')
    cw = Crop_window(img=img,
                     box_width=352,
                     box_height=256)
    cw()