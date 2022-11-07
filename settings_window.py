import tkinter as tk

import global_variables
import params
import utils


class Settings_window:
    def __init__(self):
        self.root = tk.Tk()
        self.root.configure(background='gray')
        self.root.title('Image synthesis settings')
        
        fill_frame = tk.Frame(self.root, bg='white', height=10)
        fill_frame.grid(row=0, column=1, sticky='nw')
        
        
        model_frame = tk.Frame(self.root, bg='white', width=50)
        model_frame.grid(row=1, column=0, sticky='nw')
        l1 = tk.Label(model_frame, text='Model: ', bg='white')
        l1.grid(row=0, column=0, sticky='nw')
        self.model_var = tk.StringVar(master=self.root)
        w = tk.OptionMenu(model_frame, self.model_var, *params.models.keys())
        w.grid(row=0, column=1, sticky='nw')
        self.model_var.set(global_variables.model.version)
        # l2 = tk.Label(model_frame, text='{}, {}'.format(global_variables.model.model_id, global_variables.model.revision), bg='white')
        # l2.grid(row=0, column=1, sticky='nw')
        
        fill_frame = tk.Frame(self.root, bg='white', height=10)
        fill_frame.grid(row=2, column=1, sticky='nw')
        
        device_frame = tk.Frame(self.root, bg='white', width=50)
        device_frame.grid(row=3, column=0, sticky='nw')
        l1 = tk.Label(device_frame, text='Device: ', bg='white')
        l1.grid(row=0, column=0, sticky='nw')
        self.device_var = tk.StringVar(master=self.root)
        w = tk.OptionMenu(device_frame, self.device_var, *params.devices)
        w.grid(row=0, column=1, sticky='nw')
        self.device_var.set(global_variables.model.device)
        # l2 = tk.Label(device_frame, text='{}'.format(global_variables.model.device), bg='white')
        # l2.grid(row=0, column=1, sticky='nw')
        
        fill_frame = tk.Frame(self.root, bg='white', height=10)
        fill_frame.grid(row=4, column=1, sticky='nw')
        
        seed_frame = tk.Frame(self.root, bg='white', width=50)
        seed_frame.grid(row=5, column=0, sticky='nw')
        l1 = tk.Label(seed_frame, text='Random seed: ', bg='white')
        l1.grid(row=0, column=0, sticky='nw')
        self.seed_entry = tk.Entry(seed_frame)
        self.seed_entry.insert(0, global_variables.model.seed)
        self.seed_entry.grid(row=0, column=1, sticky='nw')
        
        fill_frame = tk.Frame(self.root, bg='white', height=10)
        fill_frame.grid(row=6, column=1, sticky='nw')
        
        run_frame = tk.Frame(self.root, bg='white', width=50)
        run_frame.grid(row=7, column=0, sticky='nw')
        l1 = tk.Label(run_frame, text='Inference steps: ', bg='white')
        l1.grid(row=0, column=0, sticky='nw')
        self.steps_scale = tk.Scale(run_frame,
                                    from_=1,
                                    to=100,
                                    resolution=1,
                                    command=None,
                                    # length=200,
                                    orient=tk.HORIZONTAL,
                                    bg='white')
        self.steps_scale.grid(row=0, column=1, sticky='nw')
        self.steps_scale.set(global_variables.model.num_inference_steps)
        l2 = tk.Label(run_frame, text='Guidance scale: ', bg='white')
        l2.grid(row=1, column=0, sticky='nw')
        l3 = tk.Label(run_frame, text='Number of images: ', bg='white')
        l3.grid(row=2, column=0, sticky='nw')
        self.scale_scale = tk.Scale(run_frame,
                                    from_=1,
                                    to=20,
                                    resolution=0.5,
                                    command=None,
                                    # length=200,
                                    orient=tk.HORIZONTAL,
                                    bg='white')
        self.scale_scale.grid(row=1, column=1, sticky='nw')
        self.scale_scale.set(global_variables.model.guidance_scale)
        self.num_images_scale = tk.Scale(run_frame,
                                         from_=1,
                                         to=9,
                                         resolution=1,
                                         command=None,
                                         # length=200,
                                         orient=tk.HORIZONTAL,
                                         bg='white')
        self.num_images_scale.grid(row=2, column=1, sticky='nw')
        self.num_images_scale.set(global_variables.model.num_images)
        
        
        fill_frame = tk.Frame(self.root, bg='white', height=10)
        fill_frame.grid(row=8, column=0, sticky='nw')
        
        censor_frame = tk.Frame(self.root, bg='white', width=50)
        censor_frame.grid(row=9, column=0, sticky='nw')
        l1 = tk.Label(censor_frame, text='Block \"adult\" content', bg='white')
        l1.grid(row=0, column=0, sticky='nw')
        self.censor_var = tk.IntVar(master=self.root)
        self.censor_var.set(global_variables.model.censor_nsfw)
        censor_box = tk.Checkbutton(censor_frame,
                                    variable=self.censor_var,
                                    onvalue=True,
                                    offvalue=False,
                                    bg='white')
        censor_box.grid(row=0, column=1, sticky='nw')
        
        fill_frame = tk.Frame(self.root, bg='white', height=10)
        fill_frame.grid(row=10, column=0, sticky='nw')
        
        done_frame = tk.Frame(self.root, bg='white', width=50)
        done_frame.grid(row=11, column=0, sticky='nw')
        self.cancel_button = tk.Button(done_frame, text='Cancel', command=self.cancel)
        self.cancel_button.grid(row=0, column=0, sticky='nw')
        self.done_button = tk.Button(done_frame, text='Done', command=self.done)
        self.done_button.grid(row=0, column=1, sticky='nw')
        
    
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        utils.center(self.root)
        
        self.root.mainloop()
    
    def done(self):
        if not global_variables.model.version == self.model_var.get():
            global_variables.model.set_model(self.model_var.get())
        
        if not global_variables.model.device == self.device_var.get():
            global_variables.model.set_device(self.device_var.get())
        
        seed = int(self.seed_entry.get())
        global_variables.model.set_seed(seed)
        
        num_inference_steps = self.steps_scale.get()
        global_variables.model.set_inference_steps(num_inference_steps)
        
        guidance_scale = self.scale_scale.get()
        global_variables.model.set_guidance_scale(guidance_scale)
        
        censor = self.censor_var.get()
        global_variables.model.set_censor(censor)
        
        self.cancel()
    
    def cancel(self):
        self.root.quit()
        self.root.destroy()

if __name__ == '__main__':
    global_variables.init()
    w = Settings_window()
    w()