import tkinter as tk
from PIL import Image, ImageTk

import utils

class Confirmation_window:
    def __init__(self, image, scaling=1.0):
        self.root = tk.Tk()
        self.root.title('New generated image')
        
        self.scaled_w, self.scaled_h = (int(scaling*s) for s in image.size)
        self.canvas = tk.Canvas(self.root,
                                width=self.scaled_w,
                                height=self.scaled_h,
                                highlightthickness=1,
                                highlightbackground="black")
        self.canvas.grid(row=0, column=0, sticky='nw')
        self.img = image
        self.canvas_image = ImageTk.PhotoImage(image=self.img.resize((self.scaled_w, self.scaled_h)),
                                               master=self.root)
        self.image_container = self.canvas.create_image(0, 0,
                                                        anchor='nw',
                                                        image=self.canvas_image)
        
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=1, column=0, sticky='ne')
        
        self.reject_button = tk.Button(button_frame, text='Reject', command=self.reject)
        self.reject_button.grid(row=0, column=0, sticky='ne')
        
        self.accept_button = tk.Button(button_frame, text='Accept', command=self.accept)
        self.accept_button.grid(row=0, column=1, sticky='ne')
        
        self.accepted = False
    
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        utils.center(self.root)
        
        self.root.mainloop()
    
    def reject(self):
        self.accepted = False
        self.root.quit()
        self.root.destroy()
    
    def accept(self):
        self.accepted = True
        self.root.quit()
        self.root.destroy()


if __name__ == '__main__':
    cw = Confirmation_window(Image.new('RGB', (512, 512), color=(100, 100, 100)))
    cw()