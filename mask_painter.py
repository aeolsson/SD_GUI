import numpy as np

import tkinter as tk
from PIL import Image, ImageOps, ImageTk, ImageDraw

import prompt_modifiers
import utils

class Mask_painter:
    def __init__(self,
                 image,
                 scaling=1.0,
                 init_prompt='',
                 init_negative_prompt='',
                 init_tags=[],
                 init_strength=0.5,
                 init_mask=None):
        self.scaling = scaling
        
        self.root = tk.Tk()
        self.root.title('Mask painter')
        
        entries_frame = tk.Frame(self.root)
        entries_frame.grid(row=0, column=0, columnspan=1000, sticky='nw')
        
        prompt_label = tk.Label(entries_frame, text='prompt')
        prompt_label.grid(row=0, column=0, sticky='nw')
        self.prompt_entry = tk.Entry(entries_frame, width=140)
        self.prompt_entry.grid(row=0, column=1)
        self.prompt_entry.insert(0, init_prompt)
        negative_prompt_label = tk.Label(entries_frame, text='negative prompt')
        negative_prompt_label.grid(row=1, column=0, sticky='nw')
        self.negative_prompt_entry = tk.Entry(entries_frame, width=140)
        self.negative_prompt_entry.grid(row=1, column=1)
        self.negative_prompt_entry.insert(0, init_negative_prompt)
        
        tags_frame = tk.Frame(self.root)
        tags_frame.grid(row=1, column=0, columnspan=1000, sticky='nw')
        
        self._tag_inclusions = {}
        for i, tag in enumerate(prompt_modifiers.prompt_suffixes.keys()):
            var = tk.IntVar(master=self.root)
            var.set(tag in init_tags)
            self._tag_inclusions[tag] = var
            
            box = tk.Checkbutton(tags_frame,
                                 variable=var,
                                 text=tag,
                                 onvalue=True,
                                 offvalue=False)
            box.grid(row=0, column=i, sticky='nw')
        
        painting_frame = tk.Frame(self.root)
        painting_frame.grid(row=2, column=0, sticky='nw')
        
        self.mask_button = tk.Button(painting_frame, text='mask', command=self.activate_mask)
        self.mask_button.grid(row=0, column=0)

        self.demask_button = tk.Button(painting_frame, text='demask', command=self.activate_demask)
        self.demask_button.grid(row=0, column=1)
        
        self.fill_button = tk.Button(painting_frame, text='fill', command=self.fill)
        self.fill_button.grid(row=0, column=2)
        
        self.fill_button = tk.Button(painting_frame, text='unfill', command=self.unfill)
        self.fill_button.grid(row=0, column=3)
        
        sliders_frame = tk.Frame(self.root)
        sliders_frame.grid(row=2, column=1, sticky='nw')
        self.choose_size_button = tk.Scale(sliders_frame,
                                           from_=1,
                                           to=50,
                                           label='brush size',
                                           orient=tk.HORIZONTAL)
        self.choose_size_button.grid(row=0, column=0, sticky='nw')
        self.choose_size_button.set(25)
        self.strength_scale = tk.Scale(sliders_frame,
                                       from_=0,
                                       to=1,
                                       command=self.update_canvas,
                                       resolution=0.05,
                                       label='prompt strength',
                                       orient=tk.HORIZONTAL)
        self.strength_scale.grid(row=0, column=1, sticky='nw')
        self.strength_scale.set(init_strength)
        
        
        
        self.line_width = self.choose_size_button.get()
        
        self.mask_on = True
        self.active_button = self.mask_button
        self.active_button.config(relief=tk.SUNKEN)
        
        self.w, self.h = image.size
        
        self.canvas = tk.Canvas(self.root,
                                width=int(scaling*self.w),
                                height=int(scaling*self.h),
                                highlightthickness=1,
                                highlightbackground="black")
        self.canvas.grid(row=4, column=0, columnspan=1000, sticky='nw')
        self.canvas.bind('<B1-Motion>', self.paint)
        self.canvas.bind('<Button-1>', self.paint)
        self.canvas.bind('<ButtonRelease-1>', self.release)
        
        self.img = image
        
        if (not init_mask) or (init_mask.size[0] != self.w) or (init_mask.size[1] != self.h):
            self.img_mask = Image.new('1', (self.w, self.h), color=0)
        else:
            self.img_mask = init_mask
        
        self.background = Image.new('RGB', (self.w, self.h), color='blue')
        
        self.canvas_image = ImageTk.PhotoImage(image=self.img,
                                               master=self.root)
        self.image_container = self.canvas.create_image(0, 0,
                                                        anchor='nw',
                                                        image=self.canvas_image)
        
        buttons_frame = tk.Frame(self.root)
        buttons_frame.grid(row=5, column=1000, sticky='se')
        self.cancel_button = tk.Button(buttons_frame, text='cancel', command=self.cancel)
        self.cancel_button.grid(row=0, column=0, sticky='se')
        self.done_button = tk.Button(buttons_frame, text='done', command=self.done)
        self.done_button.grid(row=0, column=1, sticky='se')
        
        self.finished = False
        
        self.update_canvas()
        
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        utils.center(self.root)
        
        self.root.mainloop()

    def draw(self):
        self.canvas_image = ImageTk.PhotoImage(image=self.result.resize(int(self.scaling*s) for s in self.result.size),
                                               master=self.root)
        
        self.canvas.itemconfig(self.image_container, image=self.canvas_image)

    def update_canvas(self, *argv):
        strength = self.strength_scale.get()
        
        draw_mask = self.img_mask.convert('L')
        pixels = np.asarray(draw_mask)
        pixels = (strength*pixels).astype(np.int8)
        draw_mask = Image.fromarray(pixels, mode='L')
        draw_mask = ImageOps.invert(draw_mask).convert('L')
        
        self.result = Image.composite(self.img,
                                      self.background,
                                      draw_mask)
        self.draw()
        
        

    def activate_mask(self):
        self.activate_button(self.mask_button)
        self.mask_on = True

    def activate_demask(self):
        self.activate_button(self.demask_button)
        self.mask_on = False

    def fill(self):
        self.img_mask = Image.new('1', (self.w, self.h), color=1)
        self.update_canvas()
        
    def unfill(self):
        self.img_mask = Image.new('1', (self.w, self.h), color=0)
        self.update_canvas()
    
    def done(self):
        self.prompt = self.prompt_entry.get()
        self.negative_prompt = self.negative_prompt_entry.get()
        
        self.tags = [s for s in prompt_modifiers.prompt_suffixes.keys() if self._tag_inclusions[s].get()]
        
        self.strength = self.strength_scale.get()
        self.finished = True
        
        self.root.quit()
        self.root.destroy()

    def cancel(self):
        self.finished = False
        self.root.quit()
        self.root.destroy()

    def activate_button(self, button):
        self.active_button.config(relief=tk.RAISED)
        button.config(relief=tk.SUNKEN)
        self.active_button = button

    def paint(self, event):
        x, y = (int(c / self.scaling) for c in (event.x, event.y))
        
        self.line_width = self.choose_size_button.get()
        
        fill = 1 if self.mask_on else 0
        
        draw = ImageDraw.Draw(self.img_mask)
        shape = (x - self.line_width,
                 y - self.line_width,
                 x + self.line_width,
                 y + self.line_width,)
        draw.ellipse(xy=shape,
                     fill=fill)
        
        self.update_canvas()

    def release(self, event):
        pass

if __name__ == '__main__':
    p = Mask_painter(Image.new('RGB', (768, 512), color=(100, 100, 100)))
    p()