import tkinter as tk
from tkinter.colorchooser import askcolor
from tkinter import filedialog
from PIL import Image, ImageTk, ImageDraw

import global_variables
import prompt_modifiers
import params
import utils

from rescale_window import Rescale_window
from crop_window import Crop_window
from settings_window import Settings_window
from popups import Prompt_popup, Prompt_popup_with_strength
from mask_painter import Mask_painter
from confirmation_window import Confirmation_window

class Drawing_board:
    TOOLBAR_HEIGHT = 85
    TOOLBAR_WIDTH = 635
    
    def __init__(self):
        self.true_image_width, self.true_image_height = params.width, params.height
        self.scaling = 1.0
        
        self.root = tk.Tk()
        self.root.configure(background='gray')
        self.root.title('Drawing Board ({} × {})'.format(self.true_image_width, self.true_image_height))
        self.root.geometry('{}x{}'.format(max(self.true_image_width, self.TOOLBAR_WIDTH),
                                          self.true_image_height + self.TOOLBAR_HEIGHT))
        self.root.bind("<Configure>", self._on_window_resize)
        
        menubar = tk.Menu(self.root)
        self.root.configure(menu=menubar)
        
        file_menu = tk.Menu(menubar)
        file_menu.add_command(label='Resize canvas',
                              command=self.resize_canvas)
        file_menu.add_command(label='Load background image',
                              command=self.load)
        file_menu.add_command(label='Save canvas as image',
                              command=self.save)
        menubar.add_cascade(label='File',
                            menu=file_menu,
                            underline=0)
        
        paint_menu = tk.Menu(menubar)
        paint_menu.add_command(label='Paint',
                              command=self.toggle_paint)
        paint_menu.add_command(label='Erase',
                              command=self.toggle_erase)
        paint_menu.add_command(label='Change color',
                              command=self.choose_color)
        paint_menu.add_command(label='Sample color',
                              command=self.toggle_sample_color)
        paint_menu.add_command(label='Merge painting with background',
                              command=self.merge)
        menubar.add_cascade(label='Paint',
                            menu=paint_menu,
                            underline=0)
        
        box_menu = tk.Menu(menubar)
        box_menu.add_command(label='Place box',
                              command=self.toggle_box)
        box_menu.add_command(label='Reset box',
                              command=self.reset_box)
        box_menu.add_command(label='Copy',
                              command=self.copy)
        box_menu.add_command(label='Cut',
                              command=self.cut)
        box_menu.add_command(label='Paste',
                              command=self.paste)
        box_menu.add_command(label='Erase',
                              command=self.erase)
        box_menu.add_command(label='Crop',
                              command=self.crop)
        menubar.add_cascade(label='Box',
                            menu=box_menu,
                            underline=0)
        
        synthesis_menu = tk.Menu(menubar)
        synthesis_menu.add_command(label='Replace box with generation',
                                   command=self.replace)
        synthesis_menu.add_command(label='Transform box',
                                   command=self.transform)
        synthesis_menu.add_command(label='Inpaint box',
                                   command=self.inpaint)
        synthesis_menu.add_command(label='Settings',
                                   command=self.configure_model)
        menubar.add_cascade(label='Image synthesis',
                            menu=synthesis_menu,
                            underline=0)
        
        paint_frame = tk.Frame(self.root, bg='white')
        paint_frame.grid(row=0, column=0, sticky='nw')
        self.color_button = tk.Button(paint_frame, text='',width=5, command=self.choose_color, bg='black')
        self.color_button.grid(row=0, column=0, sticky='nw')
        self.sample_button = tk.Button(paint_frame, text='Sample color', command=self.toggle_sample_color)
        self.sample_button.grid(row=0, column=1, sticky='nw')
        self.paint_button = tk.Button(paint_frame, text='Paint', command=self.toggle_paint)
        self.paint_button.grid(row=0, column=2, sticky='nw')
        self.erase_button = tk.Button(paint_frame, text='Erase', command=self.toggle_erase)
        self.erase_button.grid(row=0, column=3, sticky='nw')
        self.brush_size_scale = tk.Scale(paint_frame,
                                         from_=1,
                                         to=100,
                                         label='Brush size',
                                         length=200,
                                         orient=tk.HORIZONTAL,
                                         bg='white')
        self.brush_size_scale.grid(row=1, column=0, columnspan=1000, sticky='nw')
        
        fill_frame = tk.Frame(self.root, bg='gray', width=10)
        fill_frame.grid(row=0, column=1, sticky='nw')
        
        box_frame = tk.Frame(self.root, bg='white')
        box_frame.grid(row=0, column=2, sticky='nw')
        self.box_button = tk.Button(box_frame, text='Box', command=self.toggle_box)
        self.box_button.grid(row=0, column=0, sticky='nw')
        self.box_width_scale = tk.Scale(box_frame,
                                        from_=64,
                                        to=self.true_image_width,
                                        resolution=64,
                                        command=self._on_new_box_shape,
                                        label='Box width',
                                        length=200,
                                        orient=tk.HORIZONTAL,
                                        bg='white')
        self.box_width_scale.grid(row=1, column=0, columnspan=1, sticky='nw')
        self.box_width_scale.set(self.true_image_width)
        self.box_height_scale = tk.Scale(box_frame,
                                         from_=64,
                                         to=self.true_image_height,
                                         resolution=64,
                                         command=self._on_new_box_shape,
                                         label='Box height',
                                         length=200,
                                         orient=tk.HORIZONTAL,
                                         bg='white')
        self.box_height_scale.set(self.true_image_height)
        self.box_height_scale.grid(row=1, column=1, columnspan=1, sticky='nw')
        self.box_height_scale.set(self.true_image_height)
        
        
        self.canvas = tk.Canvas(self.root,
                                width=self.true_image_width,
                                height=self.true_image_height,
                                highlightthickness=1,
                                highlightbackground="black")
        self.canvas.grid(row=1, column=0, columnspan=1000, sticky='nw')
        self.canvas.bind('<B1-Motion>', self._paint)
        self.canvas.bind('<Button-1>', self._on_click)
        self.canvas.bind('<ButtonRelease-1>', self._on_mouse_release)
        
        self.background_image = Image.new('RGB', (self.true_image_width, self.true_image_height), color=(255, 255, 255))
        self.drawing = Image.new('RGB', (self.true_image_width, self.true_image_height), color=(0, 0, 0))
        self.drawing_mask = Image.new('1', (self.true_image_width, self.true_image_height), color=1)
        
        self.canvas_image = ImageTk.PhotoImage(image=self.background_image,
                                               master=self.root)
        self.image_container = self.canvas.create_image(0, 0,
                                                        anchor='nw',
                                                        image=self.canvas_image)
        
        self.box_corner = [0, 0]
        self.box = (self.box_corner[0],
                    self.box_corner[1],
                    self.box_corner[0] + self.box_width_scale.get(),
                    self.box_corner[1] + self.box_height_scale.get())
        
        self.clipboard = None
        
        self.last_prompt = ''
        self.last_negative_prompt = ''
        self.last_tags = []
        self.last_strength = 0.5
        self.last_mask = None
        
        self.old_x = None
        self.old_y = None
        
        self.line_width = self.brush_size_scale.get()
        self.active_button = None
        
        
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        self._update_presented_image()
        self._deactivate_button(self.paint_button)
        self._deactivate_button(self.box_button)
        
        utils.center(self.root)
        
        self.root.mainloop()

    def _sync_image_with_canvas(self, *argv):
        img2show = self.result.copy()
        if self.active_button == self.box_button:
            draw = ImageDraw.Draw(img2show)
            draw.rectangle(xy=self.box,
                           fill=None,
                           outline='red',
                           width=int(8//self.scaling))
            
        self.canvas_image = ImageTk.PhotoImage(image=img2show.resize(max(int(self.scaling*s), 1) for s in img2show.size),
                                               master=self.root)
            
        self.canvas.itemconfig(self.image_container, image=self.canvas_image)

    def _update_presented_image(self, *argv):
        self.result = Image.composite(self.background_image,
                                      self.drawing,
                                      self.drawing_mask)
        self._sync_image_with_canvas()
        # self.root.update()

    def _activate_button(self, button):
        if self.active_button != button:
            self._deactivate_button(self.active_button)
            button.config(relief=tk.SUNKEN)
            self.active_button = button
        
    def _deactivate_button(self, button):
        if button:
            button.config(relief=tk.RAISED)
            self.active_button = None

    def resize_canvas(self):
        rw = Rescale_window(self.true_image_width, self.true_image_height)
        rw()
        
        if rw.accepted:
            new_width = rw.width
            new_height = rw.height
            
            if new_width == self.true_image_width and new_height == self.true_image_height:
                return
            
            new_background_image = Image.new('RGB', (new_width, new_height), color=(255, 255, 255))
            new_drawing = Image.new('RGB', (new_width, new_height), color=(0, 0, 0))
            new_drawing_mask = Image.new('1', (new_width, new_height), color=1)
            
            new_background_image.paste(self.background_image)
            new_drawing.paste(self.drawing)
            new_drawing_mask.paste(self.drawing_mask)
            
            self.background_image = new_background_image
            self.drawing = new_drawing
            self.drawing_mask = new_drawing_mask
            
            self.true_image_width, self.true_image_height = new_width, new_height
            
            self.canvas.config(width=self.true_image_width,
                               height=self.true_image_height)
            
            self.box_width_scale.config(to=self.true_image_width,
                                        resolution=64)
            
            self.box_height_scale.config(to=self.true_image_height,
                                         resolution=64)
            
            self.init_mask = None
            
            self.reset_box()
            self._on_window_resize()
            self.root.title('Drawing Board ({} × {})'.format(self.true_image_width, self.true_image_height))

    def load(self):
        img_path = filedialog.askopenfilename()
        if not img_path:
            return
        loaded_img = Image.open(img_path)
        
        if self.active_button == self.box_button:
            box_w, box_h = self.box_width_scale.get(), self.box_height_scale.get()
            cw = Crop_window(loaded_img,
                             box_w,
                             box_h)
            cw()
            if cw.accepted:
                self.background_image.paste(cw.cropped_image, box=self.box)
            # self.background_image.paste(loaded_img.resize((box_w, box_h)), box=self.box)
        else:
            box_w, box_h = self.true_image_width, self.true_image_height
            cw = Crop_window(loaded_img,
                             box_w,
                             box_h)
            cw()
            if cw.accepted:
                self.background_image = cw.cropped_image
            # self.background_image = loaded_img.resize((self.true_image_width, self.true_image_height))
        
        self._update_presented_image()
    
    def save(self):
        img_path = filedialog.asksaveasfilename(defaultextension=".jpg")
        if img_path:
            self.result.save(img_path)    

    def choose_color(self):
        self._activate_button(self.paint_button)
        
        old_color = self.color_button.cget('bg')
        new_color = askcolor(color=old_color)[1]
        
        self.color_button.config(bg=new_color)
        
    def toggle_sample_color(self):
        if self.active_button == self.sample_button:
            self._deactivate_button(self.sample_button)
        else:
            self._activate_button(self.sample_button)
        self._sync_image_with_canvas()

    def toggle_paint(self):
        if self.active_button == self.paint_button:
            self._deactivate_button(self.paint_button)
        else:
            self._activate_button(self.paint_button)
        self._sync_image_with_canvas()
        
    def toggle_erase(self):
        if self.active_button == self.erase_button:
            self._deactivate_button(self.erase_button)
        else:
            self._activate_button(self.erase_button)
        self._sync_image_with_canvas()

    def merge(self):
        self.background_image = self.result
        self.drawing = Image.new('RGB', (self.true_image_width, self.true_image_height), color=(0, 0, 0))
        self.drawing_mask = self.drawing_mask = Image.new('1', (self.true_image_width, self.true_image_height), color=1)
        self._update_presented_image()

    def toggle_box(self):
        if self.active_button == self.box_button:
            self._deactivate_button(self.box_button)
        else:
            self._activate_button(self.box_button)
        
        self._sync_image_with_canvas()
    
    def reset_box(self):
        self.box_corner = [0, 0]
        self.box_width_scale.set(self.true_image_width)
        self.box_height_scale.set(self.true_image_height)
        
        self._activate_button(self.box_button)
        
        self._update_presented_image()
    
    def copy(self):
        if self.active_button == self.box_button:
            self.clipboard = (self.background_image.crop(self.box),
                              self.drawing.crop(self.box),
                              self.drawing_mask.crop(self.box))
    
    def cut(self):
        self.copy()
        self.erase()
    
    def paste(self):
        if self.clipboard:
            self.background_image.paste(self.clipboard[0], box=self.box)
            self.drawing.paste(self.clipboard[1], box=self.box)
            self.drawing_mask.paste(self.clipboard[2], box=self.box)
            
            self._update_presented_image()
    
    def erase(self):
        if self.active_button == self.box_button:
            blank = Image.new('RGB', (self.box_width_scale.get(), self.box_height_scale.get()), color=(255, 255, 255))
            
            self.background_image.paste(blank, box=self.box)
            self.drawing.paste(blank, box=self.box)
            self.drawing_mask.paste(Image.new('1', (self.box_width_scale.get(), self.box_height_scale.get()), color=1), box=self.box)
            
            self._update_presented_image()
    
    def crop(self):
        if self.active_button == self.box_button:
            self.true_image_width, self.true_image_height = self.box_width_scale.get(), self.box_height_scale.get()
            self.canvas_width_scale.set(self.true_image_width)
            self.canvas_height_scale.set(self.true_image_height)
            
            self.background_image = self.background_image.crop(self.box)
            self.drawing = self.drawing.crop(self.box)
            self.drawing_mask = self.drawing_mask.crop(self.box)
            
            self.canvas.config(width=self.true_image_width,
                               height=self.true_image_height)
            
            self.box_width_scale.config(from_=64,
                                        to=self.true_image_width,
                                        resolution=64)
            
            self.box_height_scale.config(from_=64,
                                        to=self.true_image_height,
                                        resolution=64)
            
            self._update_presented_image()
            self._on_window_resize()
    
    
    def replace(self):
        pp = Prompt_popup(init_prompt=self.last_prompt,
                          init_negative_prompt=self.last_negative_prompt,
                          init_tags=self.last_tags)
        pp()
        if pp.finished:
            self.last_prompt = pp.prompt
            self.last_negative_prompt = pp.negative_prompt
            self.last_tags = pp.tags
            prompt = self.last_prompt
            for tag in self.last_tags:
                prompt += prompt_modifiers.prompt_suffixes[tag]
            print(prompt)
            
            images = global_variables.model.txt2img(prompt=prompt,
                                                    negative_prompt=self.last_negative_prompt,
                                                    height=self.box_height_scale.get(),
                                                    width=self.box_width_scale.get())
            image = images[0]
            print('Done generating')
            
            ci = Confirmation_window(image, scaling=self.scaling)
            ci()
            if ci.accepted:
                self.background_image.paste(image, box=self.box)
                
                self.drawing.paste(Image.new('RGB', (self.box_width_scale.get(), self.box_height_scale.get()), color=(0, 0, 0)), box=self.box)
                
                self.drawing_mask.paste(Image.new('1', (self.box_width_scale.get(), self.box_height_scale.get()), color=1), box=self.box)
                
                self._update_presented_image()
    
    def transform(self):
        self._update_presented_image()
        if self.active_button != self.box_button:
            return
            
        pp = Prompt_popup_with_strength(init_prompt=self.last_prompt,
                                        init_negative_prompt=self.last_negative_prompt,
                                        init_tags=self.last_tags,
                                        init_strength=self.last_strength)
        pp()
        if pp.finished:
            self.last_prompt = pp.prompt
            self.last_negative_prompt = pp.negative_prompt
            self.last_tags = pp.tags
            prompt = self.last_prompt
            for tag in self.last_tags:
                prompt += prompt_modifiers.prompt_suffixes[tag]
            print(prompt)
            
            self.last_strength = pp.strength
            
            cropped = self.result.crop(self.box)
            
            images = global_variables.model.img2img(prompt=prompt,
                                                    negative_prompt=self.last_negative_prompt,
                                                    init_image=cropped,
                                                    strength=self.last_strength)
            image = images[0]
            print('Done generating')
            
            ci = Confirmation_window(image, scaling=self.scaling)
            ci()
            if ci.accepted:
                self.background_image.paste(image, box=self.box)
                
                self.drawing.paste(Image.new('RGB', (self.box_width_scale.get(), self.box_height_scale.get()), color=(0, 0, 0)), box=self.box)
                
                self.drawing_mask.paste(Image.new('1', (self.box_width_scale.get(), self.box_height_scale.get()), color=1), box=self.box)
                
                self._update_presented_image()
            
            
    
    def inpaint(self):
        self._update_presented_image()
        if self.active_button != self.box_button:
            return
        
        cropped = self.result.crop(self.box)
        w, h = cropped.size
        scaling = min(self.scaling, 1)#1 / max(w / 1920, h / (1080-200))
        
        mp = Mask_painter(cropped,
                          scaling=scaling,
                          init_prompt=self.last_prompt,
                          init_negative_prompt=self.last_negative_prompt,
                          init_tags=self.last_tags,
                          init_strength=self.last_strength,
                          init_mask=self.last_mask)
        mp()
        if mp.finished:
            self.last_prompt = mp.prompt
            self.last_negative_prompt = mp.negative_prompt
            self.last_tags = mp.tags
            prompt = self.last_prompt
            for tag in self.last_tags:
                prompt += prompt_modifiers.prompt_suffixes[tag]
            print(prompt)
            self.last_strength = mp.strength
            self.last_mask = mp.img_mask
            
            images = global_variables.model.inpaint(prompt=prompt,
                                                    negative_prompt=self.last_negative_prompt,
                                                    init_image=cropped,
                                                    mask_image=self.last_mask,
                                                    strength=self.last_strength)
            image = images[0]
            image = Image.composite(image, cropped, self.last_mask)
            print('Done generating')
            
            ci = Confirmation_window(image, scaling=self.scaling)
            ci()
            if ci.accepted:
                self.background_image.paste(image, box=self.box)
                self.drawing.paste(Image.new('RGB', (self.box_width_scale.get(), self.box_height_scale.get()), color=(0, 0, 0)), box=self.box)
                self.drawing_mask.paste(Image.new('1', (self.box_width_scale.get(), self.box_height_scale.get()), color=1), box=self.box)
                
                self._update_presented_image()
            
    def configure_model(self):
        sw = Settings_window()
        sw()
    
    def _paint(self, event):
        x, y = (int(c / self.scaling) for c in (event.x, event.y))
        self.line_width = self.brush_size_scale.get()
        
        if self.active_button==self.paint_button:
            fill = self.color_button.cget('bg')
            mask_fill = 0
        elif self.active_button==self.erase_button:
            fill = (0, 0, 0)
            mask_fill = 1
        else:
            return
        
        shape = (x - self.line_width//2,
                 y - self.line_width//2,
                 x + self.line_width//2,
                 y + self.line_width//2)
        
        draw = ImageDraw.Draw(self.drawing)
        draw.ellipse(xy=shape,
                     fill=fill)
        
        draw_mask = ImageDraw.Draw(self.drawing_mask)
        draw_mask.ellipse(xy=shape,
                          fill=mask_fill)
        
        if self.old_x and self.old_y:
            draw.line((self.old_x, self.old_y, x, y),
                      fill=fill,
                      width=self.line_width)
            
            draw_mask.line((self.old_x, self.old_y, x, y),
                           fill=mask_fill,
                           width=self.line_width)
        
        
        
        self.old_x, self.old_y = x, y
        self._update_presented_image()

    def _on_click(self, event):
        if self.active_button == self.paint_button or self.active_button == self.erase_button:
            self._paint(event)
        elif self.active_button == self.sample_button:
            x, y = int(event.x/self.scaling), int(event.y/self.scaling)
            color = self.result.getpixel((x, y))
            color = utils.rgb2hex(color)
            self.color_button.config(bg=color)
            self.toggle_paint()
        elif self.active_button == self.box_button:
            self.box_corner[0] = min(int(event.x/self.scaling), self.true_image_width - self.box_width_scale.get())
            self.box_corner[1] = min(int(event.y/self.scaling), self.true_image_height - self.box_height_scale.get())
            
            self.box = (self.box_corner[0],
                        self.box_corner[1],
                        self.box_corner[0] + self.box_width_scale.get(),
                        self.box_corner[1] + self.box_height_scale.get())
            
            self._sync_image_with_canvas()

    def _on_mouse_release(self, event):
        self.old_x = self.old_y = None
    
    def _on_new_box_shape(self, *argv):
        self.box = (self.box_corner[0],
                    self.box_corner[1],
                    self.box_corner[0] + self.box_width_scale.get(),
                    self.box_corner[1] + self.box_height_scale.get())
        
        self._activate_button(self.box_button)
        self._update_presented_image()
    
    def _on_window_resize(self, *argv):
        win_w, win_h = self.root.winfo_width(), self.root.winfo_height()
        
        max_canvas_width = max(win_w - 3, 1e-3)
        max_canvas_height = max(win_h - self.TOOLBAR_HEIGHT - 3, 1e-3)
        
        self.scaling = min(max_canvas_width / self.true_image_width,
                           max_canvas_height / self.true_image_height)
        self.scaling = max(self.scaling, 0)
        
        self.canvas.config(width=int(self.scaling*self.true_image_width),
                           height=int(self.scaling*self.true_image_height))
        
        self._update_presented_image()


if __name__ == '__main__':
    d = Drawing_board()
    d()