import collections
from django.shortcuts import HttpResponse, redirect, render
import requests
from django.core.files.storage import FileSystemStorage
import pymongo
from typing import Collection
from pymongo import MongoClient
import random
import cv2
import os
from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np

def _delete_file(path):
  if os.path.isfile(path):
    os.remove(path)

class Encoder:
   encoder = None
   @staticmethod 
   def getInstance():
      if Encoder.encoder == None:
        Encoder()
      return Encoder.encoder
   def __init__(self):
      if Encoder.encoder != None:
        raise Exception("This class is a singleton!")
      else:
        Encoder.encoder = load_model("./models/encoder_20epoch.h5",compile=False) 
class Decoder:
   decoder = None
   @staticmethod 
   def getInstance():
      if Decoder.decoder == None:
        Decoder()
      return Decoder.decoder
   def __init__(self):
      if Decoder.decoder != None:
        raise Exception("This class is a singleton!")
      else:
        Decoder.decoder = load_model("./models/decoder_20epoch.h5",compile=False) 


class DBConnect:
   __instance = None
   @staticmethod 
   def getInstance():
      if DBConnect.__instance == None:
        DBConnect()
      return DBConnect.__instance
   def __init__(self):
      if DBConnect.__instance != None:
        raise Exception("This class is a singleton!")
      else:
        cluster = MongoClient("mongodb+srv://demo:demo@cluster0.csdz61e.mongodb.net/?retryWrites=true&w=majority")
        db = cluster["bachelorNeeds"]

        DBConnect.__instance = db




def main(request):
  try:
    request.session['email']
    return render(request,"home.html")
  except:
    return render(request,"login.html")

def watermarkPage(request):
  return render(request,"watermarkImage.html")
def encryptedImgPage(request):
  return render(request,"encrypted_imgsend.html")

def encryptede_image_handle(request):
  uploaded_file = request.FILES["photo"]
  fs = FileSystemStorage()   
  photo_name=fs.save(uploaded_file.name, uploaded_file)
  photo_path = fs.url(photo_name)
  img=cv2.imread('.'+photo_path)
  _delete_file('.'+photo_path)

  orig = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
  orig=orig* 1.0 / 255.0
  orig = cv2.resize(orig, (256, 256),interpolation = cv2.INTER_NEAREST)
  img = tf.expand_dims(orig, axis=0)
  encoder=Encoder.getInstance()
  encoder_output=encoder.predict(img)
  array_name="./media/"+photo_name.split(".")[0]+'.npy'
  np.save(array_name, encoder_output)
  
  return render(request,"home.html")

def watermarkMsgHandle(request):
  pass

def loginVarify(request):
  db=DBConnect.getInstance()
  collection = db['musers']
  email= request.POST['email']
  password=request.POST['password']
  if(collection.count_documents({"email":email ,"password":password})!=1):
    message = {"msg": "invalid email or password"}
    return render(request,"login.html")
  request.session['email']=email
  return render(request,"home.html")
  
def sendHandle(request):
  pass

  

  


