# -*- coding: utf-8 -*-
"""
Created on Mon Aug 25 09:56:48 2025

@author: jost
"""
import piexif
import piexif.helper
#from datetime import datetime as dt
import os#, sys
import time
import tkinter as tk
from tkinter import simpledialog
from tkintermapview import TkinterMapView
from urllib.parse import quote_plus
import requests
  
from PIL import Image, ImageTk
import io# , sys

class exif_class:
  def __init__(self):
    self.Copyright = ''
    self.ImageDescription = ''
    self.DocumentName = ''
    self.FileSource = 1
    self.Make = ''
    self.Model = ''
    self.LensMake = ''
    self.LensModel = ''
    self.FocalLength = 50
    self.FocalLengthIn35mmFormat = 50
    self.MaxApertureValue = 2.0
    self.ISO = 50
    self.ISOSpeed = 50
    self.ImageUniqueID = ''
    self.UserComment = ''
    self.FNumber = 2.0
    self.ExposureTime = 1.0/60
		  
    self.longitude = 0
    self.latitude = 0
		  
    self.DateTimeOriginal = '2025:01:01 00:00:00'
    self.SpectralSensitivity = ''
    
  def rational_to_fraction(r):
    from fractions import Fraction
    num = Fraction(r).limit_denominator(100000).numerator
    nom = Fraction(r).limit_denominator(100000).denominator
    return (num, nom)

class aimage:

  def __init__(self, file_path, logtype= False):
    
    self.exif = exif_class()
		
    self.ImageNumber = 0
    self.file_path = file_path
    self.im = Image.open(file_path)#.copy()
    self.read_exif()
    self.modified = False

    self.w, self.h = self.im.size
    thumbnail = self.exif_dict.pop("thumbnail")
    #print(f' thumb size = {sys.getsizeof(thumbnail)}')
    if thumbnail is not None:
      # print(f'Found Thumb of size {sys.getsizeof(thumbnail)} in file {file_path}')
      # Convert thumbnail data to an image
      self.im_thumb = Image.open(io.BytesIO(thumbnail))
      th_w, th_h = self.im_thumb.size
      #print(f'Found Thumb of size {th_w}x{th_h} in file {file_path}')
      #print(f'Raw thumbnail size = {sys.getsizeof(thumbnail)}')
      if max(th_w, th_h) != 200:
        self.im_thumb = self.im.copy()
        self.im_thumb.thumbnail((200, 200))
        if not logtype:
          print(f'setting the file {self.file_path} to modified ' \
                'to get a chance to write a proper thumbnail to the file')
          self.modified = True
      #else:        
      #  print('using thumnail from exif')
    else:
      self.im_thumb = self.im.copy()
      self.im_thumb.thumbnail((200, 200))
      if not logtype:
        print(f'setting the file {self.file_path} to modified ' \
              'to get a chance to write a proper thumbnail to the file')
        self.modified = True
    #self.im_thumb = self.im.resize((thumb_w, thumb_h))  # Resize the image
     #, resample=Image.Resampling.BICUBIC, reducing_gap=3.0) 
    self.mini_thumb = self.im_thumb.copy()
    self.mini_thumb.thumbnail((70,70))
    self.tk_mini_thumb = ImageTk.PhotoImage(self.mini_thumb)
 
		# Convert the image to a format Tkinter can use
    self.tk_image = ImageTk.PhotoImage(self.im_thumb)
		
  def read_exif(self):  
    self.exif_dict = piexif.load(self.im.info["exif"])
    if piexif.ImageIFD.Copyright in self.exif_dict["0th"]:
      self.exif.Copyright = self.exif_dict["0th"][piexif.ImageIFD.Copyright]
    if piexif.ImageIFD.Make in self.exif_dict["0th"]:
      self.exif.Make = self.exif_dict["0th"][piexif.ImageIFD.Make].decode('ascii')
    if piexif.ImageIFD.Model in self.exif_dict["0th"]:
      self.exif.Model = self.exif_dict["0th"][piexif.ImageIFD.Model].decode('ascii')
    if piexif.ImageIFD.ImageDescription in self.exif_dict["0th"]:
      self.exif.ImageDescription = self.exif_dict["0th"][piexif.ImageIFD.ImageDescription]
    if piexif.ImageIFD.DocumentName in self.exif_dict["0th"]:
      self.exif.DocumentName = self.exif_dict["0th"][piexif.ImageIFD.DocumentName]
    if piexif.ExifIFD.FileSource in self.exif_dict["Exif"]:
      self.exif.FileSource = int.from_bytes(self.exif_dict["Exif"][piexif.ExifIFD.FileSource], byteorder='big')
    if piexif.ExifIFD.LensMake in self.exif_dict["Exif"]:
      self.exif.LensMake = self.exif_dict["Exif"][piexif.ExifIFD.LensMake].decode('ascii')
    if piexif.ExifIFD.LensModel in self.exif_dict["Exif"]:
      self.exif.LensModel = self.exif_dict["Exif"][piexif.ExifIFD.LensModel].decode('ascii')
    if piexif.ExifIFD.FocalLength in self.exif_dict["Exif"]:
      a, b = self.exif_dict["Exif"][piexif.ExifIFD.FocalLength]
      self.exif.FocalLength = int(a/b)
    if piexif.ExifIFD.FocalLengthIn35mmFilm in self.exif_dict["Exif"]:
      a = self.exif_dict["Exif"][piexif.ExifIFD.FocalLengthIn35mmFilm]
      self.exif.FocalLengthIn35mmFormat = a
    if piexif.ExifIFD.MaxApertureValue in self.exif_dict["Exif"]:
      a, b = self.exif_dict["Exif"][piexif.ExifIFD.MaxApertureValue]
      self.exif.MaxApertureValue = round(a/b, 1)
    if piexif.ExifIFD.FNumber in self.exif_dict["Exif"]:
      a, b = self.exif_dict["Exif"][piexif.ExifIFD.FNumber]
      self.exif.FNumber = round(a/b, 1)
    if piexif.ExifIFD.ExposureTime in self.exif_dict["Exif"]:
      a, b = self.exif_dict["Exif"][piexif.ExifIFD.ExposureTime]
      self.exif.ExposureTime = round(a/b, 8)
      #print(f'ExposureTime from exif = {a}/{b}={self.exif.ExposureTime}')
    if piexif.ExifIFD.DateTimeOriginal in self.exif_dict["Exif"]:
      byte_data = self.exif_dict["Exif"][piexif.ExifIFD.DateTimeOriginal]
      self.exif.DateTimeOriginal = byte_data.decode('ascii')
    if piexif.ExifIFD.DateTimeDigitized in self.exif_dict["Exif"]:
      byte_data = self.exif_dict["Exif"][piexif.ExifIFD.DateTimeDigitized]
      self.exif.DateTimeDigitized = byte_data.decode('ascii')
      #print(f'DateTimeDigitized = {self.exif.DateTimeDigitized}')
    if piexif.ExifIFD.SpectralSensitivity in self.exif_dict["Exif"]:
      self.exif.SpectralSensitivity = self.exif_dict["Exif"][piexif.ExifIFD.SpectralSensitivity]
    if piexif.ExifIFD.ISOSpeed in self.exif_dict["Exif"]:
      self.exif.ISOSpeed = self.exif_dict["Exif"][piexif.ExifIFD.ISOSpeed]
    if piexif.ExifIFD.ISOSpeedRatings in self.exif_dict["Exif"]:
      self.exif.ISO = int(self.exif_dict["Exif"][piexif.ExifIFD.ISOSpeedRatings])
    if piexif.ExifIFD.UserComment in self.exif_dict["Exif"]:
      try:
        self.exif.UserComment = piexif.helper.UserComment.load(self.exif_dict["Exif"][piexif.ExifIFD.UserComment])
        #print(self.exif.UserComment)
      except ValueError:
        pass
    if piexif.GPSIFD.GPSLatitudeRef in self.exif_dict["GPS"]:
      lat_ref = self.exif_dict["GPS"][piexif.GPSIFD.GPSLatitudeRef].decode('ascii')
      lng_ref = self.exif_dict["GPS"][piexif.GPSIFD.GPSLongitudeRef].decode('ascii')
      (d1,d2),(m1,m2),(s1,s2) = self.exif_dict["GPS"][piexif.GPSIFD.GPSLatitude]
      lat_deg = d1/d2 + (m1/m2)/60.0 + (s1/s2)/3600.0
      (d1,d2),(m1,m2),(s1,s2) = self.exif_dict["GPS"][piexif.GPSIFD.GPSLongitude]
      lng_deg = d1/d2 + (m1/m2)/60.0 + (s1/s2)/3600.0
      if lat_ref[0] == 'S':
        lat_deg = -lat_deg
      if lng_ref[0] == 'W': 
        lng_deg = -lng_deg
      self.exif.latitude = lat_deg
      self.exif.longitude = lng_deg
      #print(f'GPS from exif: {lat_deg} {lng_deg}')
    #if piexif.ImageIFD.JPEGInterchangeFormat in self.exif_dict["1st"]:
    #  print(f'JPEGInterchangeFormat = \
    #        {self.exif_dict["1st"][piexif.ImageIFD.JPEGInterchangeFormat]}')
    #  print(f'JPEGInterchangeFormatLength = \
    #        {self.exif_dict["1st"][piexif.ImageIFD.JPEGInterchangeFormatLength]}')
      
    		
  def write_exif(self):
    #import io, sys
    from write_exif_helpers import exif_class
    zeroth_ifd = {
            piexif.ImageIFD.Copyright: self.exif.Copyright,
            piexif.ImageIFD.Make: self.exif.Make,  # ASCII, count any
            piexif.ImageIFD.Model: self.exif.Model,
            piexif.ImageIFD.XResolution: (self.w, 1),  # RATIONAL, count 1
            piexif.ImageIFD.YResolution: (self.h, 1),  # RATIONAL, count 1
            piexif.ImageIFD.Software: "write_exif",  # ASCII, count any	
            piexif.ImageIFD.ImageDescription: self.exif.ImageDescription,
            piexif.ImageIFD.DocumentName: self.exif.DocumentName
            }
    encoded_comment = piexif.helper.UserComment.dump(self.exif.UserComment, encoding="unicode")
    exif_ifd = {piexif.ExifIFD.ExifVersion: b"\x00\x02\x03\x00",  # UNDEFINED, count 4
            piexif.ExifIFD.FileSource: self.exif.FileSource.to_bytes(1, 'big', signed=False),
            piexif.ExifIFD.LensMake: self.exif.LensMake,  # ASCII, count any
            piexif.ExifIFD.LensModel: self.exif.LensModel,
            piexif.ExifIFD.FocalLength: (self.exif.FocalLength, 1),
            piexif.ExifIFD.FocalLengthIn35mmFilm: self.exif.FocalLengthIn35mmFormat,
            piexif.ExifIFD.MaxApertureValue: (int(self.exif.MaxApertureValue * 10), 10),
            piexif.ExifIFD.ApertureValue: (int(self.exif.FNumber * 10), 10),
            #piexif.ExifIFD.ShutterSpeedValue: (1, int(1.0/self.exif.ExposureTime)),
            piexif.ExifIFD.ISOSpeed: self.exif.ISOSpeed,
            piexif.ExifIFD.ISOSpeedRatings: self.exif.ISO,
            piexif.ExifIFD.ImageUniqueID: self.exif.ImageUniqueID,
            piexif.ExifIFD.UserComment: encoded_comment,
            piexif.ExifIFD.FNumber: (int(self.exif.FNumber * 10), 10),
            piexif.ExifIFD.ExposureTime: exif_class.rational_to_fraction(self.exif.ExposureTime),
            piexif.ExifIFD.DateTimeOriginal: self.exif.DateTimeOriginal,
            piexif.ExifIFD.DateTimeDigitized: self.exif.DateTimeOriginal,
            piexif.ExifIFD.SpectralSensitivity: self.exif.SpectralSensitivity
          }
    exif_1st = {
            piexif.ImageIFD.JPEGInterchangeFormat: 1,
            piexif.ImageIFD.JPEGInterchangeFormatLength: 1
      }
    def to_deg(value, ref):
      degrees = int(value)
      minutes = int((value - degrees) * 60)
      seconds = round((value - degrees - minutes / 60) * 3600, 5)
      return [(degrees, 1), (minutes, 1), (int(seconds * 100), 100)], ref
    lng = self.exif.longitude
    lat = self.exif.latitude
    lat_deg, lat_ref = to_deg(abs(lat), "N" if lat >= 0 else "S")
    lng_deg, lng_ref = to_deg(abs(lng), "E" if lng >= 0 else "W")
    gps_ifd = {piexif.GPSIFD.GPSVersionID: (2, 0, 0, 0),  # BYTE, count 4
               piexif.GPSIFD.GPSAltitudeRef: 1,  # BYTE, count 1 ... also be accepted '(1,)'
               piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode(),
               piexif.GPSIFD.GPSLatitude: lat_deg,
               piexif.GPSIFD.GPSLongitudeRef: lng_ref.encode(),
               piexif.GPSIFD.GPSLongitude: lng_deg,
           }
    o = io.BytesIO()
    #self.im_thumb.thumbnail((50, 50))
    #self.im_thumb.save(o, "jpeg")
    thumbnail_image = self.im.copy()
    thumbnail_image.thumbnail((200, 200), Image.Resampling.LANCZOS) # Use LANCZOS for better quality
    thumbnail_image.save(o, "jpeg")
    thumbnail_bytes = o.getvalue()
    #print(f'Size of thumbnail is {sys.getsizeof(thumbnail_bytes)}')
    #exif_dict["thumbnail"] = thumbnail_bytes
    #exif_dict["1st"][513] = 1 # JPEGInterchangeFormat
    #exif_dict["1st"][514] = 1 # JPEGInterchangeFormatLength
    #thumbnail = self.exif_dict['thumbnail']
    exif_dict = {"0th":zeroth_ifd, "Exif":exif_ifd, "GPS":gps_ifd, "1st":exif_1st, "thumbnail": thumbnail_bytes}
    #print(exif_dict)
		
    exif_bytes = piexif.dump(exif_dict)

    if self.file_path.lower().rfind('jpeg'):
      index = self.file_path.lower().rfind('jpeg')
    else:
      index = self.file_path.lower().rfind('jpg')
    new_file = self.file_path[:index] + '-exif.jpeg'
    try:
      self.im.save(new_file, "jpeg", exif=exif_bytes, quality=100, optimize=True)
      #self.im.close()
      os.remove(self.file_path)
      os.rename(new_file, self.file_path)
      #self.im.open(self.file_path)
      success = True
    except Exception as e:
      print(f'Failed to save image {self.ImageNumber}. Exception {e}')
      success = False
    return success
  
def process_image_files(image_folder, q): #, thumb):
  image_files = [os.path.join(image_folder, file) for file in os.listdir(image_folder) if file.endswith(".jpg")]
  image_files.sort()
  film_images = []
  
  current_index = 0
  for file in image_files:
    current_index += 1
    film_images.append(aimage(file))
    film_images[current_index-1].ImageNumber = current_index
    q.put(f'Loading {current_index}/{len(image_files)}')
    #if current_index == 1:
    #  thumb.config(image=film_images[0].tk_image)
  print(f'Loaded {len(film_images)} images')
  return film_images

def process_logbook(log_folder):
  import json
  # Load the logbook
  log_files = [os.path.join(log_folder, file) for file in os.listdir(log_folder) if file.endswith(".json")]
  log_json_file = open(log_files[0], 'r')
  log_json = json.load(log_json_file)
  log_entries = []
  for log_entry in log_json:
    image_number = int(log_entry['ImageNumber'])
    log_image_path = log_folder + '/images/' + str(image_number) + '.jpeg'
    #print(log_image_path)
    log_entries.append(aimage(log_image_path, logtype= True))
    log_entries[len(log_entries)-1].ImageNumber = image_number
    log_entries[len(log_entries)-1].exif.ImageDescription = log_entry['Description']
    log_entries[len(log_entries)-1].exif.DocumentName = log_entry['DocumentName']
    log_entries[len(log_entries)-1].exif.DateTimeOriginal = log_entry['DateTimeOriginal']
    log_entries[len(log_entries)-1].exif.FileSource = log_entry['FileSource']
    log_entries[len(log_entries)-1].exif.ExposureTime = log_entry['ExposureTime']
    log_entries[len(log_entries)-1].exif.FNumber = log_entry['FNumber']
    log_entries[len(log_entries)-1].exif.FocalLength = log_entry['FocalLength']
    log_entries[len(log_entries)-1].exif.FocalLengthIn35mmFormat = log_entry['FocalLengthIn35mmFormat']
    log_entries[len(log_entries)-1].exif.Make = log_entry['Make']
    log_entries[len(log_entries)-1].exif.Model = log_entry['Model']
    log_entries[len(log_entries)-1].exif.LensMake = log_entry['LensMake']
    log_entries[len(log_entries)-1].exif.LensModel = log_entry['LensModel']
    log_entries[len(log_entries)-1].exif.ISO = log_entry['ISO']
    log_entries[len(log_entries)-1].exif.ISOSpeed = log_entry['ISOSpeed']
    log_entries[len(log_entries)-1].exif.ImageUniqueID = log_entry['ImageUniqueId']
    log_entries[len(log_entries)-1].exif.UserComment = log_entry['UserComment']
    log_entries[len(log_entries)-1].exif.SpectralSensitivity = log_entry['SpectralSensitivity']
    def to_angle(s):
      D = int(s[:s.find("deg")])
      M = int(s[s.find("deg")+4:s.find("'")])
      S = float(s[s.find("'")+2:s.find("\"")])
      p = 1
      if s.find("N")>0: 
        p = 1
      if s.find("S")>0: 
        p = -1
      if s.find("W")>0: 
        p = -1
      if s.find("E")>0: 
        p = 1
      #print(f's = {s} and angle is {p*(D + M/60.0 + S/3600.0)}')
      return p*(D + M/60.0 + S/3600.0)
    longitude_s = log_entry['GPSLongitude']
    latitude_s = log_entry['GPSLatitude']
    log_entries[len(log_entries)-1].exif.longitude = to_angle(longitude_s)
    log_entries[len(log_entries)-1].exif.latitude = to_angle(latitude_s)
    
  print(f'Loaded {len(log_entries)} log entries')
  return log_entries

class EditExifDialog(tk.Toplevel):
  def __init__(self, parent):
    super().__init__(parent)  # Initialize the Toplevel window
    #self.callback = callback
    # Create a Toplevel window
    #self.top = tk.Toplevel(parent)
    self.parent = parent
    self.minsize(850, 650)
    self.title("Edit EXIF data")
    self.grab_set()  # Make the dialog modal
    self.exifp = self.parent.film_images[self.parent.current_index].exif
    self.map_mode = self.parent.image_map_mode
    #self.map_mode_change = on_image_map_mode_change
    print(f'EditExifDialog: map_mode({self.map_mode})')
    self.create_widgets()
   
  def on_gps_changed(self): #, event):
    self.longitude = self.map_widget.longitude
    self.latitude = self.map_widget.latitude
    text=f'Long: {round(self.longitude, 5)} Lat: {round(self.latitude, 5)}'
    self.label_gps.config(text=text)
    print(f'map_mode = {self.map_mode}')
    self.is_modified()
    return
  
  def map_mode_change(self, map_mode):
    print(f' got callback in Edit_exif dialog for map_mode change to {map_mode}')
    self.parent.image_map_mode = map_mode
    return
     
  def on_key_release(self, event):
    self.is_modified()
    
  def go_left(self):
    self.is_modified(commit=True)
    self.parent.current_index = (self.parent.current_index - 1) % len(self.parent.film_images)
    self.update()
    self.parent.update_image()
    self.is_modified()
    
  def go_right(self):
    self.is_modified(commit=True)
    self.parent.current_index = (self.parent.current_index + 1) % len(self.parent.film_images)
    self.update()
    self.parent.update_image()
    self.is_modified()
    
  def update(self):
    self.exifp = self.parent.film_images[self.parent.current_index].exif
    self.date_entry.delete(0, tk.END)
    self.date_entry.insert(0, self.exifp.DateTimeOriginal)
    num, nom = exif_class.rational_to_fraction(self.exifp.ExposureTime)
    self.ET_num_entry.delete(0, tk.END)
    self.ET_num_entry.insert(0, num)
    self.ET_nom_entry.delete(0, tk.END)
    self.ET_nom_entry.insert(0, nom)
    self.FN_entry.delete(0, tk.END)
    self.FN_entry.insert(0, self.exifp.FNumber)
    
    text=f'Long: {round(self.exifp.longitude, 5)} Lat: {round(self.exifp.latitude, 5)}'
    self.longitude = round(self.exifp.longitude, 5)
    self.latitude = round(self.exifp.latitude, 5)
    self.label_gps.config(text=text) 
    
    self.LM_entry.delete(0, tk.END)
    self.LM_entry.insert(0, self.exifp.LensMake)
    self.LMDL_entry.delete(0, tk.END)
    self.LMDL_entry.insert(0, self.exifp.LensModel)
    
    self.map_widget.set_position(self.exifp.latitude, self.exifp.longitude)
    self.map_widget.set_marker(self.exifp.latitude, self.exifp.longitude, \
                          text=f"{round(self.exifp.longitude,5)} {round(self.exifp.latitude,5)}")

    self.image_thumb.config(image=self.parent.film_images[self.parent.current_index].tk_image)
    self.caption.config(text=f'Image {self.parent.film_images[self.parent.current_index].ImageNumber}')

    
  def create_widgets(self):
    edit_frame = tk.Frame(self)
    edit_frame.grid(column=0, row=0, sticky="ne")
    # Add a label
    label = tk.Label(edit_frame, text="date:", anchor=tk.E)
    label.grid(column=0, row=0, sticky=tk.E)
    label = tk.Label(edit_frame, text="ExposureTime:", anchor=tk.E)
    label.grid(column=0, row=1, sticky=tk.E)
    label = tk.Label(edit_frame, text="FNumber:", anchor=tk.E)
    label.grid(column=0, row=2, sticky=tk.E)
    label = tk.Label(edit_frame, text="GPS:", anchor=tk.E)
    label.grid(column=0, row=3, sticky=tk.E)
    label = tk.Label(edit_frame, text="LensMake", anchor=tk.E)
    label.grid(column=0, row=4, sticky=tk.E)
    label = tk.Label(edit_frame, text="LensModel", anchor=tk.E)
    label.grid(column=0, row=5, sticky=tk.E)

    # Date Time entry
    self.date_entry = tk.Entry(edit_frame) #, textvariable=date_var)
    self.date_entry.grid(column=1, row=0, sticky=tk.W) #columnspan=3
    self.date_entry.bind("<KeyRelease>", self.on_key_release)
    # ExposureTime Entry
    sub_frame = tk.Frame(edit_frame, padx=0, pady=0)
    sub_frame.grid(column=1, row=1, sticky=tk.W)
    num, nom = exif_class.rational_to_fraction(self.exifp.ExposureTime)
    #print(f'Exposure {self.exifp.ExposureTime}')
    self.ET_num_entry = tk.Entry(sub_frame, width=3)  #textvariable=self.ET_num_var, width=4)
    self.ET_num_entry.grid(column=0, row=0, sticky=tk.W)
    self.ET_num_entry.bind("<KeyRelease>", self.on_key_release)
    label_ET = tk.Label(sub_frame, text="/")
    label_ET.grid(column=1, row=0)    
    self.ET_nom_entry = tk.Entry(sub_frame, width=5)
    self.ET_nom_entry.grid(column=2, row=0, sticky=tk.W)
    self.ET_nom_entry.bind("<KeyRelease>", self.on_key_release)
    # Fnumber Entry
    self.FN_entry = tk.Entry(edit_frame, width=4)
    self.FN_entry.grid(column=1, row=2, sticky=tk.W)
    self.FN_entry.bind("<KeyRelease>", self.on_key_release)
    # GPS
    self.label_gps = tk.Label(edit_frame)#, text=text) #, anchor=tk.W)
    self.label_gps.grid(column=1, row=3, sticky=tk.W)
    # # LensMake
    self.LM_entry = tk.Entry(edit_frame, width=10)
    self.LM_entry.grid(column=1, row=4, sticky=tk.W)
    self.LM_entry.bind("<KeyRelease>", self.on_key_release)
    
    # LensModel
    self.LMDL_entry = tk.Entry(edit_frame, width=35)
    self.LMDL_entry.grid(column=1, row=5, sticky=tk.W)
    self.LMDL_entry.bind("<KeyRelease>", self.on_key_release)
    
    # Interactive Map View
    self.map_widget = mymap(self, self.on_gps_changed, 
            map_mode_callback=self.map_mode_change, map_mode=self.map_mode)#, width=600, height=600)
    self.map_widget.set_zoom(17)
    self.map_widget.grid(column=1, row=0, padx=5, pady=5, columnspan=2, sticky="nesw")
    
    # label that indicates modification
    self.mod_label = tk.Label(edit_frame)
    self.mod_label.grid(column=0, row= 6, columnspan=2)
      
    # show the thumbnail for reference
    self.image_thumb = tk.Label(edit_frame) #, width=2, height=2) #, padx=5, pady=5)
    self.image_thumb.grid(column=0, row=7, columnspan=2, ipadx=0, ipady=5)
    self.caption = tk.Label(edit_frame)
    self.caption.grid(column=0, row=8, columnspan=2)

    self.update()
        
    # add navigate buttons
    sub_frame2 = tk.Frame(edit_frame, padx=0, pady=0)
    sub_frame2.grid(column=0, row=9, columnspan=2)#, sticky=tk.W)
    left_button = tk.Button(sub_frame2, text='<', command = self.go_left)
    left_button.grid(column=0, row=0, sticky='e')
    right_button = tk.Button(sub_frame2, text='>', command = self.go_right)
    right_button.grid(column=1, row=0, sticky='w')
   
    # Add a submit button
    save_button = tk.Button(self, text="Save", command=self.save)
    save_button.grid(column=0, row=10, columnspan=3, padx=20, pady=20)
    
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(1, weight=1)
    
    self.update_idletasks()    

  def is_modified(self, commit=False):
    modified = False
    #print(f'DT = {self.date_entry.get()}, DT-org = {self.exifp.DateTimeOriginal}')
    if self.exifp.DateTimeOriginal != self.date_entry.get():
      if commit:
        self.exifp.DateTimeOriginal = self.date_entry.get()
      modified = True
    #print(f'ExposureTime-org = {self.exifp.ExposureTime}, and actual = {int(self.ET_num_entry.get())/int(self.ET_nom_entry.get())}')
    if round(self.exifp.ExposureTime, 5) != round(int(self.ET_num_entry.get())/int(self.ET_nom_entry.get()), 5):
      if commit:
        self.exifp.ExposureTime = round(int(self.ET_num_entry.get())/int(self.ET_nom_entry.get()), 5)
      modified = True
      #print('ExposureTime modified')
    if self.exifp.FNumber != float(self.FN_entry.get()):
      if commit:
        self.exifp.FNumber = float(self.FN_entry.get())
      modified = True
    if round(self.exifp.longitude, 5) != self.longitude:
      if commit:
        self.exifp.longitude = self.longitude
      modified = True
      #print('Longitude modified')
    if round(self.exifp.latitude, 5) != self.latitude:
      if commit:
        self.exifp.latitude = self.latitude
      modified = True
      #print('Latitude modified')
    if self.exifp.LensMake != self.LM_entry.get():
      if commit:
        self.exifp.LensMake = self.LM_entry.get()
      modified = True
    if self.exifp.LensModel != self.LMDL_entry.get():
      if commit:
        self.exifp.LensModel = self.LMDL_entry.get()
      modified = True
    if modified:
      self.mod_label.config(text='*modified*')
      if commit:
        self.parent.film_images[self.parent.current_index].modified = True
    else:
      self.mod_label.config(text='')
    return modified

  def save(self):
    if self.is_modified(commit=True):
      print(f'modified is {True}')
      #self.callback(modified)
      self.parent.film_images[self.parent.current_index].modified = True
      self.parent.update_image()
    #self.q.put(True)
    self.destroy()  # Close the dialog
    
class SaveDialog(tk.Toplevel):
  def close(self):
    print('Closing...')
    self.callback(True)
    self.destroy()

  def __init__(self, parent, images, callback):
    super().__init__(parent)  # Initialize the Toplevel window
    self.callback = callback
    self.title("Save EXIF data")
    self.grab_set()  # Make the dialog modal
    self.images = images
    self.create_widgets()
    self.protocol("WM_DELETE_WINDOW", self.close)
        
  def save(self):
    print('Saving...')
    self.save_button.config(state=tk.DISABLED)
    self.close_button.config(state=tk.DISABLED)
    self.update_idletasks()
    for im in self.images:
      if im.modified:
        m = f'Writing EXIF for Image {im.ImageNumber}'
        self.text_widget.insert(tk.END, m + '\n')
        self.text_widget.see(tk.END)
        print(m)
        if im.write_exif():
          m = f'Successfully written Image {im.ImageNumber}'
          self.text_widget.insert(tk.END, m + '\n')
          self.text_widget.see(tk.END)
          print(m)
          im.modified = False
          self.update_idletasks()
        else:
          m = f'Failed to write Image {im.ImageNumber}' + \
            '\n make sure, the image is not open somewhere.'
          self.text_widget.insert(tk.END, m + '\n')
          self.text_widget.see(tk.END)
          print(m)
    self.text_widget.insert(tk.END, 'Finished\n')
    self.text_widget.see(tk.END)
    self.save_button.config(state=tk.ACTIVE)
    self.close_button.config(state=tk.ACTIVE)

  def create_widgets(self):
    self.text_widget = tk.Text(self, wrap="word", height=15, width=50)
    self.text_widget.grid(column=0, row=0, columnspan=2)
    
    self.text_widget.insert(tk.END,"The following images will be saved:\n")
    ims = ''
    for im in self.images:
      if im.modified:
        ims += f'{im.ImageNumber}, '
    ims = ims[:len(ims)-2] + '\n'
    self.text_widget.insert(tk.END,ims)
    self.save_button = tk.Button(self, text="Save", command=self.save)
    self.save_button.grid(column=0, row=1, sticky=tk.E, pady=5)
    
    self.close_button = tk.Button(self, text='Close', command=self.close)
    self.close_button.grid(column=1, row=1, sticky=tk.W, pady=5)
    
class mymap(tk.Frame):
  def __init__(self, parent, gps_changed_callback=None, map_mode_callback=None, 
               map_mode='street', *args, **kwargs):
    tk.Frame.__init__(self, parent, borderwidth=2, relief="sunken", *args, **kwargs)
    self.grid_propagate(True)
    self.latitude = 32.7
    self.longitude = -117.05
    if gps_changed_callback is not None:
      self.gps_changed_callback = gps_changed_callback
    #self.top = parent
    self.map_widget = TkinterMapView(self)#, width=300, height=300)
    self.on_map_mode_changed = map_mode_callback
    self.map_mode = map_mode
    #print(f'mymap: map_mode({map_mode}): {id(map_mode)}, self.map_mode: {id(self.map_mode)}')
    if map_mode != 'street':
      self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", max_zoom=20)
    self.map_widget.grid(column=0, row=0, columnspan=2, padx=5, pady=5, sticky="nsew")
    self.map_widget.set_position(self.latitude, self.longitude)
    self.map_widget.set_zoom(5)
    #map_widget.delete_all_marker()
    self.map_widget.set_marker(self.latitude, self.longitude, \
                          text=f"{round(self.longitude,5)} {round(self.latitude,5)}")
    if gps_changed_callback is not None:
      self.map_widget.canvas.bind("<Double-Button-1>", self.on_double_click)
      label_hint = tk.Label(self, text='double click on map to redifine marker')
      label_hint.grid(column=0, row=1)
    option_frame = tk.Frame(self)
    option_frame.grid(column=0, row=2, columnspan=2, sticky="sew")
    address_button = tk.Button(option_frame, text='enter address', command=self.enter_address)
    address_button.grid(column=0, row=0, sticky='w')
    self.map_option = tk.StringVar(value=self.map_mode)
    radio_sat = tk.Radiobutton(option_frame, text="Satellite", 
                  variable=self.map_option, value="sat", command=self.map_view)
    radio_sat.grid(column=1, row=0, sticky="e")
    radio_street = tk.Radiobutton(option_frame, text="Default", 
                  variable=self.map_option, value="street", command=self.map_view)
    radio_street.grid(column=2, row=0, sticky="ew")
    
    
    self.grid_rowconfigure(0, weight=1)
    self.grid_columnconfigure(0, weight=1)

  def enter_address(self):
    user_input = simpledialog.askstring("Input", "Please enter an address:")
    #find_address = self.map_widget.set_address("12956 Christman Lane, Poway, CA")
    #print(user_input)
    #print(quote_plus(user_input))

    url = "https://nominatim.openstreetmap.org/search"
    params = {
      'q': quote_plus(user_input),
      "format": "json",
      "addressdetails": "1",
      "limit": "1"
    }
    headers = {
      "User-Agent": "write_exit/1.0 (https://myapp.dev.net; jost@diederi.net)",
      "Referer": "https://myapp.dev.net"
    }

    response = requests.get(url, params=params, headers=headers)
    #print(response)
    #print(response.json())
    # print(f'{find_address}')
    if str(response).find('200') >= 0:
      lat = float(response.json()[0]["lat"])
      lon = float(response.json()[0]["lon"])
      #self.set_position(lat, lon)
      self.map_widget.delete_all_marker()
      self.map_widget.set_marker(lat, lon, \
                        text=f"{round(lon,5)} {round(lat,5)}")
      self.map_widget.set_position(lat, lon)
      self.map_widget.set_zoom(15)
    
  def map_view(self):
    print(f'setting map server, map_option = {self.map_option.get()}')
    if self.map_option.get() == 'sat':
      #self.map_mode = 'sat'
      print(f'mymap/map_view: map_mode({self.map_mode}): {id(self.map_mode)}')
      self.map_widget.set_tile_server("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", max_zoom=20)
      #self.map_widget.set_overlay_tile_server("https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}", max_zoom=19)
      self.on_map_mode_changed('sat')
    else:
      #self.map_mode = 'street'
      self.map_widget.set_tile_server("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png")  # OpenStreetMap (default)
      self.on_map_mode_changed('street')

  def on_double_click(self, event):
    # Get the coordinates of the double-click
    x, y = event.x, event.y
    lat, lon = self.map_widget.convert_canvas_coords_to_decimal_coords(x, y)
    #print(f"Double-clicked at canvas coordinates: ({x}, {y})")
    #print(f"Corresponding latitude and longitude: ({lat}, {lon})")
    self.map_widget.delete_all_marker()
    self.map_widget.set_marker(lat, lon, \
                      text=f"{round(lon,5)} {round(lat,5)}")
    text=f'Long: {round(lon, 5)} Lat: {round(lat, 5)}'
    print(text)
    self.longitude = round(lon, 5)
    self.latitude = round(lat, 5)
    self.gps_changed_callback()
    return
  
  def set_position(self, lat, lon):
    self.map_widget.set_position(lat, lon)
    
  def set_marker(self, lat, lon, text=''):
    self.map_widget.delete_all_marker()
    self.map_widget.set_marker(lat, lon, text=text)

  def set_zoom(self, level):
    self.map_widget.set_zoom(level)
    
class open_images_dialog(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)  # Initialize the Toplevel window
        self.parent = parent
        self.title("Open Images")
        self.geometry("200x100")
        self.grab_set()

        # Add widgets to the child dialog
        progress = tk.Label(self, text="Loading Image")
        progress.pack(pady=10)
        start_time = time.process_time()
        image_files = [os.path.join(self.parent.image_folder, file) for file in os.listdir(self.parent.image_folder) if file.endswith(".jpg")]
        image_files.sort()
        self.parent.film_images = []
        
        current_index = 0
        for file in image_files:
          current_index += 1
          self.parent.film_images.append(aimage(file))
          self.parent.film_images[current_index-1].ImageNumber = current_index
          progress.config(text=f'Loading {current_index}/{len(image_files)}')
          if current_index == 1:
            self.parent.image_thumb.config(image=self.parent.film_images[0].tk_image)
          self.update_idletasks()
        print(f'Loaded {len(self.parent.film_images)} images')
        end_time = time.process_time()
        elapsed_time = end_time - start_time
        print(f"Elapsed process time: {elapsed_time:.6f} seconds")
        
        self.parent.update_image()
        self.parent.config(cursor='')
        self.destroy()

class LogBookWarning(tk.Toplevel):
  def cancel(self):
    self.destroy()

  def __init__(self, parent): #, callback):
    super().__init__(parent)  # Initialize the Toplevel window
    #self.callback = callback
    self.result = None
    self.parent = parent
    self.title("About LightMe Logbook")
    self.grab_set()  # Make the dialog modal
    self.create_widgets()
    self.protocol("WM_DELETE_WINDOW", self.cancel)
        
  def cont(self):
    self.result = True
    self.destroy()
    #self.callback(True)
    
  def checkbox(self):
    if self.checkbox_var.get():
      self.parent.ignore_log_warning = True
    
  def create_widgets(self):
    message = tk.Message(self, text='The Open Logbook function imports ' +\
      'Logbooks from LightMe that have been exported from LightMe with ' +\
      'JSON and Images option. \n' +\
      'In the next step, just select the folder, in which the json file resides.',
      width=300)
    message.grid(column=0, row=0, columnspan=2, padx=10, pady=10)
    cancel_button = tk.Button(self, text="Cancel", command=self.cancel)
    cancel_button.grid(column=0, row=1, sticky=tk.E, pady=5)
    
    continue_button = tk.Button(self, text='Continue', command=self.cont)
    continue_button.grid(column=1, row=1, sticky=tk.W, pady=5)
    
    self.checkbox_var = tk.BooleanVar()
    checkbox = tk.Checkbutton(self, text='Do not show again', command=self.checkbox,
                              variable=self.checkbox_var)
    checkbox.grid(column=0, row=2, columnspan=2)
