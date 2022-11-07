import tkinter as tk

import prompt_modifiers
import utils

class Prompt_popup:
    def __init__(self,
                 init_prompt='',
                 init_negative_prompt='',
                 init_tags=[]):
        self.root = tk.Tk()
        self.root.title('Prompt entry')
        
        entries_frame = tk.Frame(self.root)
        entries_frame.grid(row=0, column=0, sticky='nw')
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
        tags_frame.grid(row=1, column=0, sticky='nw')
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
            box.grid(row=0, column=i)
        
        buttons_frame = tk.Frame(self.root)
        buttons_frame.grid(row=3, column=0, sticky='se')
        self.cancel_button = tk.Button(buttons_frame, text='cancel', command=self.cancel)
        self.cancel_button.grid(row=0, column=0, sticky='se')
        self.done_button = tk.Button(buttons_frame, text='done', command=self.done)
        self.done_button.grid(row=0, column=1, sticky='se')
        
        # num_tags = len(prompt_modifiers.prompt_suffixes.keys())
        
        
        
        self.finished = False
    
    def __call__(self):
        self.root.lift()
        self.root.attributes('-topmost',True)
        self.root.attributes('-topmost',False)
        
        utils.center(self.root)
        
        self.root.mainloop()
        
    def cancel(self):
        self.finished = False
        self.root.quit()
        self.root.destroy()
    
    def done(self):
        self.prompt = self.prompt_entry.get()
        self.negative_prompt = self.negative_prompt_entry.get()
        
        self.tags = [s for s in prompt_modifiers.prompt_suffixes.keys() if self._tag_inclusions[s].get()]
        
        self.finished = True
        self.root.quit()
        self.root.destroy()

class Prompt_popup_with_strength(Prompt_popup):
    def __init__(self,
                 init_prompt='',
                 init_negative_prompt='',
                 init_tags=[],
                 init_strength=0.5):
        super().__init__(init_prompt=init_prompt,
                         init_negative_prompt=init_negative_prompt,
                         init_tags=init_tags)
        
        strength_frame = tk.Frame(self.root)
        strength_frame.grid(row=2, column=0, sticky='nw')
        self.strength_scale = tk.Scale(strength_frame,
                                       from_=0,
                                       to=1,
                                       resolution=0.05,
                                       label='prompt strength',
                                       length=800,
                                       orient=tk.HORIZONTAL)
        self.strength_scale.grid(row=0, column=0)
        self.strength_scale.set(init_strength)
    
    def done(self):
        self.strength = self.strength_scale.get()
        super().done()

if __name__ == '__main__':
    # p = Prompt_popup()
    p = Prompt_popup_with_strength()
    p()