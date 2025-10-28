# -*- coding: utf-8 -*-
"""
Created on Fri Aug 22 13:27:52 2025

@author: jost
"""
import os
import sys
import json
import copy

from write_exif_helpers import exif_class, \
  process_logbook, EditExifDialog, SaveDialog, mymap, open_images_dialog, \
  LogBookWarning

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
from tkinter import messagebox

#import threading
#import queue

class ParentApp(tk.Tk):
  def __init__(self):
    super().__init__()
    self.title("Write Exif to Analog Images")
    #self.geometry("400x300")
    self.focus_force()
    self.minsize(1200, 500)

    # Load settings
    self.image_folder = ''
    self.log_folder = ''
    self.Copyright = ''
    # Get the user's home directory
    home_dir = os.path.expanduser("~")
    self.settings_file_path = os.path.join(home_dir, ".write_exif.json")
    try:
      with open(self.settings_file_path, "r") as file:
        loaded_settings = json.load(file)
      if 'last_image_folder' in loaded_settings:
        self.image_folder = loaded_settings['last_image_folder']
      if 'last_log_folder' in loaded_settings:
        self.log_folder = loaded_settings['last_log_folder']
      if 'Copyright' in loaded_settings:
        self.Copyright = loaded_settings['Copyright']
        print(f'Loaded settings with Copyright = {self.Copyright}')
      if 'image_map_mode' in loaded_settings:
        self.image_map_mode = loaded_settings['image_map_mode']
      else:
        self.image_map_mode = 'street'
      if 'log_map_mode' in loaded_settings:
        self.log_map_mode = loaded_settings['log_map_mode']
      else:
        self.log_map_mode = 'street'
      if 'ignore_log_warning' in loaded_settings:
        self.ignore_log_warning = loaded_settings['ignore_log_warning']
      else:
        self.ignore_log_warning = False
    except Exception: 
        print('No Settings file yet.')

    self.current_index = 0
    self.image_box = ttk.LabelFrame(self, text="Images", padding=(10, 10))
    self.image_box.grid(column=0, row=1, padx=20, pady=20)
    self.image_box.propagate(True)
    
    self.left_button = tk.Button(self.image_box, text='<', command=self.prev_image)#, anchor=tk.W)
    self.left_button.grid(column=0, row=1, ipadx=5, ipady=5)
    self.left_button.config(state=tk.DISABLED)
    self.right_button = tk.Button(self.image_box, text='>', command=self.next_image)#, anchor=tk.W)
    self.right_button.grid(column=2, row=1, ipadx=5, ipady=5)
    self.right_button.config(state=tk.DISABLED)
    self.exif_edit_button = tk.Button(self.image_box, text='edit', command=self.exif_edit_dialog)
    self.exif_edit_button.grid(column=2, row=3, ipadx=5, ipady=5)
    self.exif_edit_button.config(state=tk.DISABLED)
    self.exif_info = tk.Text(self.image_box, height=6, width=22, bg="grey90")
    self.exif_info.grid(column=1, row=3, ipadx=5, ipady=5)
    self.exif_info.config(state=tk.DISABLED)
    #if self.film_images[self.current_index].exif.Copyright == '':
    #  exifs = ' '
    #else:
    #  exifs = exif_string(self.film_images[self.current_index].exif)
    #self.exif_info.insert("1.0", exifs)
    self.current_index2 = 0
    
    self.log_box = ttk.LabelFrame(self, text="Log Entries", padding=(10, 10))
    self.log_box.grid(column=1, row=1, padx=20, pady=20, sticky="nsew")
    self.grid_rowconfigure(1, weight=1)
    self.grid_columnconfigure(1, weight=1)
    self.open_images_button = tk.Button(self.image_box, text='Open Images', command=self.open_images)
    self.open_images_button.grid(column=1, row=0, ipadx=5, ipady=5)
  
    self.log_navigation = tk.Frame(self.log_box)
    self.log_navigation.grid(column=0, row=0)
    #self.log_navigation.grid_rowconfigure(1, weight=1)
    #self.log_navigation.grid_columnconfigure(1, weight=1)

    self.open_log_button = tk.Button(self.log_navigation, text='Open Logbook', 
                                     command=self.open_logbook_confirmation)
    self.open_log_button.grid(column=1, row=0, ipadx=5, ipady=5)
    
    self.image_thumb = tk.Label(self.image_box) #, width=2, height=2) #, padx=5, pady=5)
    self.image_thumb.grid(column=1, row=1, ipadx=5, ipady=5)
    self.caption = tk.Label(self.image_box, text=' - ')
    self.caption.grid(column=1, row=2, ipadx=5, ipady=5)
       
    self.loading_images = False

    self.transfer_button = tk.Button(self.log_navigation, text='<<- Transfer to Image', command=self.transfer)
    self.transfer_button.grid(column=1, row=4, ipadx=5, ipady=5)
    self.transfer_button.config(state=tk.DISABLED)
    
    self.org = sys.stdout

    self.copyright_var = tk.StringVar()
    self.copyright_var.set(self.Copyright)
    self.copyright_label = tk.Label(self.image_box, text='Copyright')
    self.copyright_label.grid(column=1, row=4, ipadx=5, ipady=5)
    self.copyright_entry = tk.Entry(self.image_box, textvariable=self.copyright_var)
    self.copyright_entry.grid(column=1, row=5, ipadx=5, ipady=5)
    self.write_button = tk.Button(self.image_box, text="Save Changes", command=self.write)
    self.write_button.grid(column=1, row=6, ipadx=5, ipady=5)
    self.write_button.config(state=tk.DISABLED)

    self.map_widget = mymap(self.log_box, map_mode_callback=self.on_log_gps_mode_change, 
                            map_mode=self.log_map_mode)#, width=300, height=300)
    self.map_widget.grid(column=1, row=0, padx=20, pady=20, sticky="nsew")
    self.log_box.grid_rowconfigure(0, weight=1)
    self.log_box.grid_columnconfigure(1, weight=1)

    self.protocol("WM_DELETE_WINDOW", self.on_closing)


  def exif_string(self, exifp: exif_class):
    s = exifp.DateTimeOriginal
    a, b = exif_class.rational_to_fraction(exifp.ExposureTime)
    s += f'\nExposure: {a}/{b}'
    s += f'\nFNumber: {exifp.FNumber}'
    s += f'\nGPS {exifp.longitude:.4f} {exifp.latitude:.4f}'
    #s += f'\n{exifp.Make} {exifp.Model}'
    s += f'\n{exifp.LensMake} {exifp.LensModel}'
    return s

  def update_image(self):
    #global image_box, image_thumb, exif_info, caption
    try:
      self.film_images
    except NameError:
      return
    self.image_thumb.config(image=self.film_images[self.current_index].tk_image)
    mod_s = ' *' if self.film_images[self.current_index].modified else ''
    self.caption.config(text=f'Image {self.current_index+1}/{len(self.film_images)} {mod_s}')
    self.left_button.config(image=self.film_images[(self.current_index - 1) % \
                                         len(self.film_images)].tk_mini_thumb)
    self.right_button.config(image=self.film_images[(self.current_index + 1) % \
                                          len(self.film_images)].tk_mini_thumb)
    exifs = self.exif_string(self.film_images[self.current_index].exif)
    self.exif_info.config(state=tk.NORMAL)
    self.exif_info.delete('1.0', tk.END)
    self.exif_info.insert('1.0', exifs)
    self.exif_info.config(state=tk.DISABLED)
    write_enable = False
    for im in self.film_images:
      if im.modified: 
        write_enable = True
    if write_enable:
      self.write_button.config(state=tk.ACTIVE)
    else:
      self.write_button.config(state=tk.DISABLED)
      
    self.left_button.config(state=tk.ACTIVE)
    self.right_button.config(state=tk.ACTIVE)
    self.exif_edit_button.config(state=tk.ACTIVE)
      
    #self.focus()
  
  def next_image(self):
    #global current_index
    self.current_index = (self.current_index + 1) % len(self.film_images)
    self.update_image()
  
  def prev_image(self):
    #global current_index
    self.current_index = (self.current_index - 1) % len(self.film_images)
    self.update_image()
   
  def on_image_gps_mode_change(self, mode):
    #global image_map_mode
    self.image_map_mode = mode
    print(f'image_map_mode changed to {mode}')
  
  def on_log_gps_mode_change(self, mode):
    #global log_map_mode
    self.log_map_mode = mode
    print(f'log_map_mode changed to {mode}')
  
  def exif_edit_dialog(self): 
    EditExifDialog(self) #, self.film_images[self.current_index].exif) #, self.on_exif_edit_close, 
          
  def open_images(self):
    self.image_folder = fd.askdirectory(parent=self, title='Select Image Folder', initialdir = self.image_folder)
    if self.image_folder:  # Check if a folder was selected (not cancelled)
      print(f"Selected folder: {self.image_folder}")
      self.config(cursor='wait')
      self.current_index = 0
      self.loading_images = True
      open_images_dialog(self)
    else:
      print("Folder selection cancelled.")
    return
  
  def update_image2(self):
    self.log_thumb.config(image=self.log_entries[self.current_index2].tk_image)
    self.left_button2.config(image=self.log_entries[(self.current_index2 - 1) % \
                                         len(self.log_entries)].tk_mini_thumb)
    self.right_button2.config(image=self.log_entries[(self.current_index2 + 1) % \
                                          len(self.log_entries)].tk_mini_thumb)
    self.log_caption.config(text=f'Log {self.log_entries[self.current_index2].ImageNumber} ({self.current_index2 + 1}/{len(self.log_entries)})')
    exifs = self.exif_string(self.log_entries[self.current_index2].exif)
    self.exif_info2.config(state=tk.NORMAL)
    self.exif_info2.delete('1.0', tk.END)
    self.exif_info2.insert('1.0', exifs)
    self.exif_info2.config(state=tk.DISABLED)
    self.map_widget.set_position(self.log_entries[self.current_index2].exif.latitude, self.log_entries[self.current_index2].exif.longitude)
    #map_widget.delete_all_marker()
    self.map_widget.set_marker(self.log_entries[self.current_index2].exif.latitude, self.log_entries[self.current_index2].exif.longitude, text=f"log {self.current_index2}")
    try:
      self.film_images
      if (len(self.log_entries) > 0) and (len(self.film_images) > 0):
        self.transfer_button.config(state=tk.ACTIVE)
      else:
        self.transfer_button.config(state=tk.DISABLED)
    except (NameError, AttributeError):
      print("film_images not loaded yet.")
    #root.focus()
  
  def next_image2(self):
    try:
      self.log_entries
      self.current_index2 = (self.current_index2 + 1) % len(self.log_entries)
      self.update_image2()
    except NameError:
      print("Object does not exist.")
  	  
  def prev_image2(self):
    try:
      self.log_entries
      self.current_index2 = (self.current_index2 - 1) % len(self.log_entries)
      self.update_image2()
    except NameError:
      print("Object does not exist.")
      
  def open_logbook_confirmation(self):
    if self.ignore_log_warning:
      self.open_logbook()
    else:
      dialog = LogBookWarning(self) #, self.open_logbook)
      self.wait_window(dialog)
      print(f"LogBookWarning returned: {dialog.result}")
      if dialog.result:
        self.open_logbook()
    
  def open_logbook(self):
    #global log_folder, log_entries
    #global left_button2, log_thumb, right_button2, log_caption, exif_info2
    #global root, map_widget
    self.log_folder = fd.askdirectory(parent=self, title='Select Logbook Folder', initialdir = self.log_folder)
    if self.log_folder:  # Check if a folder was selected (not cancelled)
      print(f"Selected folder: {self.log_folder}")
      self.config(cursor='wait')
      self.update()
      self.update_idletasks()
      self.log_entries = process_logbook(self.log_folder)
      self.config(cursor='')
      if len(self.log_entries) == 0: 
        return
      self.left_button2 = tk.Button(self.log_navigation, text='<', command=self.prev_image2)#, anchor=tk.W)
      self.left_button2.grid(column=0, row=1, ipadx=5, ipady=5)
      self.log_thumb = tk.Label(self.log_navigation, image=self.log_entries[0].tk_image)
      self.log_thumb.grid(column=1, row=1, ipadx=5, ipady=5)
      self.right_button2 = tk.Button(self.log_navigation, text='>', command=self.next_image2)#, anchor=tk.W)
      self.right_button2.grid(column=2, row=1, ipadx=5, ipady=5)
      self.log_caption = tk.Label(self.log_navigation, text=f'Log {self.log_entries[self.current_index2].ImageNumber} ({self.current_index2 + 1}/{len(self.log_entries)})')
      self.log_caption.grid(column=1, row=2, ipadx=5, ipady=5)
      self.exif_info2 = tk.Text(self.log_navigation, height=6, width=22, bg="grey90")
      self.exif_info2.grid(column=1, row=3, ipadx=5, ipady=5)
      exifs = self.exif_string(self.log_entries[self.current_index2].exif)
      self.exif_info2.insert("1.0", exifs)
      self.exif_info2.config(state=tk.DISABLED)
      self.map_widget.set_position(self.log_entries[self.current_index2].exif.latitude, self.log_entries[self.current_index2].exif.longitude)  # Example: San Diego, CA
      self.map_widget.set_zoom(10)
      self.map_widget.set_marker(self.log_entries[self.current_index2].exif.latitude, self.log_entries[self.current_index2].exif.longitude, text=f"log {self.current_index2}")
      self.update_image2()
    else:
      print("Folder selection cancelled.")
    return
      
  def update_settings_file(self):
    settings = {
      "last_image_folder": self.image_folder, 
      "last_log_folder": self.log_folder, 
      "Copyright": self.copyright_var.get(),
      "image_map_mode": self.image_map_mode,
      "log_map_mode": self.log_map_mode,
      "ignore_log_warning": self.ignore_log_warning}
      
    with open(self.settings_file_path, "w") as file:
      json.dump(settings, file, indent=2)
  
  def transfer(self):
    print(f'Transferring Log entry number {self.log_entries[self.current_index2].ImageNumber}')
    # TODO figure out if deepcopy is really neccessary here
    self.film_images[self.current_index].exif = copy.deepcopy(self.log_entries[self.current_index2].exif)
    self.film_images[self.current_index].exif.Copyright = self.Copyright
    self.film_images[self.current_index].modified = True
    self.update_image()
    #canvas.itemconfig(exif_text, text=exif_string(film_images[current_index].exif))
    #canvas.itemconfig(index_text, text='Image '+str(current_index + 1)+' *')
        
  def write(self):
    self.update_settings_file()
    self.org = sys.stdout
    SaveDialog(self, self.film_images, self.on_save_dialog_close)
    #sys.stdout = org
    self.update_image()
    
  def on_save_dialog_close(self,result):
    #sys.stdout = self.org
    print(f"Save-Dialog was closed with result = {result}")
    self.update_image()
  
  
  
  
  def gps_changed(self):
    print(f'got new coordinates {self.map_widget.latitude} {self.map_widget.longitude}')
    print(f'map_mode = {self.map_mode}')
  
  def on_exif_edit_close(self,result):
      print(f"Dialog was closed with modified = {result}")
      if result:
        self.film_images[self.current_index].modified = True
        self.update_image()
  
  def on_closing(self):
    self.update_settings_file()
    try:
      self.film_images
      images_modified = False
      for im in self.film_images:
        if im.modified: 
          images_modified = True
      if images_modified:
        if messagebox.askokcancel("Quit", 
            "There are modified images. Are you sure you want to quit?"):
          print('Cleaning up images')
          for im in self.film_images:
            im.im.close()
            del im
          print('Cleaning up Log entries')
          for log in self.log_entries:
            log.im.close()
            del log
          self.destroy()
        else: 
          return
      else:
        print('Cleaning up images')
        for im in self.film_images:
          im.im.close()
          im.im_thumb.close()
          im.mini_thumb.close()
          del im.tk_image
          del im.tk_mini_thumb
          del im
        print('Cleaning up Log entries')
        for log in self.log_entries:
          log.im.close()
          im.im_thumb.close()
          im.mini_thumb.close()
          del im.tk_image
          del im.tk_mini_thumb
          del log
        self.destroy()
    except (NameError, AttributeError):
      self.destroy()
        

if __name__ == "__main__":
  print('Starting')
  app = ParentApp()
  app.update_idletasks()
  app.mainloop()