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
import datetime
import base64
from cryptography.fernet import Fernet
from bson.objectid import ObjectId

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



def Encode(key,message):
    enc=[]
    for i in range(len(message)):
        key_c = key[i % len(key)]
        enc.append(chr((ord(message[i]) + ord(key_c)) % 256))
    return base64.urlsafe_b64encode("".join(enc).encode()).decode()






def Decode(key,message):
    dec=[]
    message = base64.urlsafe_b64decode(message).decode()
    for i in range(len(message)):
        key_c = key[i % len(key)]
        dec.append(chr((256 + ord(message[i])- ord(key_c)) % 256))
    return "".join(dec)




def encrypt(filename, key):
  f = Fernet(key)
  with open(filename, "rb") as file:
    file_data = file.read()    
    encrypted_data = f.encrypt(file_data)
      
  with open(filename, "wb") as file:
    file.write(encrypted_data)


def decrypt(filename, key):
  f = Fernet(key)
  with open(filename, "rb") as file:
    encrypted_data = file.read()
  decrypted_data = f.decrypt(encrypted_data)
  with open(filename, "wb") as file:
    file.write(decrypted_data)

def save_file(request,file_name):
  now_=datetime.datetime.now()
  db = DBConnect.getInstance()
  collection = db["message"]
  
  msgBlock={
        "from":request.session['email'],
        "file":file_name,
        "time":now_,
    }
  collection.insert_one(msgBlock)
  return redirect(request.META.get('HTTP_REFERER'))

def save_text(request,text_):
  now_=datetime.datetime.now()
  db = DBConnect.getInstance()
  collection = db["message"]
  
  msgBlock={
        "from":request.session['email'],
        "text":text_,
        "time":now_,
    }
  collection.insert_one(msgBlock)
  return redirect(request.META.get('HTTP_REFERER'))

def decrypt_image(array_name):
  decoder=Decoder.getInstance()
  array=np.load(array_name)
  original_output=decoder.predict(array)
  cv2.imshow(array_name,original_output[0])
  cv2.waitKey(1)
  
  
  
def viewWatermark(img_link) :
  img_with_watermark= cv2.imread(img_link)
  img1=img_with_watermark<<6
  cv2.imshow('watermark',img1)
  cv2.waitKey(1)


def encryptAll(request):
  id_=request.POST['id_']
  db = DBConnect.getInstance()
  collection = db["message"]
    
  post=collection.find_one({"_id":ObjectId(id_)})
  global key
  global text_key
  try:
    post['text']
    return render(request,"viewDecrupt.html",{'text':Decode(text_key,post['text']) })
  except:
    pass
  if(post['file'].split('.')[2]!='pdf'):
    if(post['file'].split('.')[2]=='npy'):
      decrypt_image(post['file'])
    else:
      viewWatermark(post['file'])
  
  decrypt(post['file'],key)
  response = HttpResponse(post['file'], content_type="application/pdf")
  # response['Content-Disposition'] = 'inline; filename=' +post['file']
  return response
  raise Http404
  return render(request,"home.html")
  

def main(request):
  try:
    request.session['email']
    db = DBConnect.getInstance()
    collection = db["message"]
    msgs=collection.find({})
    msgsList=[]
    
    for i in msgs:
      a={}
      a['id_']=i['_id']
      a["from"]=i['from']
      a['time']=i['time']
      try:
        a['text']=i['text']
      except:
        a['file']=i['file']
      msgsList.append(a)
    
    msgsList=sorted(msgsList,key=lambda d: d['time'])

    
    return render(request,"home.html",{'conversation':msgsList})
  except:
    return render(request,"login.html")

def fileEncryptionHandle(request):
  uploaded_file = request.FILES["file_"]
  fs = FileSystemStorage()   
  file_name=fs.save(uploaded_file.name, uploaded_file)
  file_path = fs.url(file_name)
  global key
  encrypt('.'+file_path,key)
  save_file(request,'.'+file_path)
  return render(request,"home.html")
  




def watermarkPage(request):
  return render(request,"watermarkImage.html")
def encryptedImgPage(request):
  return render(request,"encrypted_imgsend.html")
def filePage(request):
  return render(request,"file_send.html")



  



def encryptede_image_handle(request):
  uploaded_file = request.FILES["photo"]
  fs = FileSystemStorage()   
  photo_name=fs.save(uploaded_file.name, uploaded_file)
  photo_path = fs.url(photo_name)
  img=cv2.imread('.'+photo_path)
  _delete_file('.'+photo_path)

  orig = img 
  orig=orig* 1.0 / 255.0
  orig = cv2.resize(orig, (256, 256),interpolation = cv2.INTER_NEAREST)
  img = tf.expand_dims(orig, axis=0)
  encoder=Encoder.getInstance()
  encoder_output=encoder.predict(img)
  array_name="./media/"+photo_name.split(".")[0]+'.npy'
  np.save(array_name, encoder_output)
  
  save_file(request,array_name)
  
  return render(request,"home.html")

def watermarkMsgHandle(request):
  image = request.FILES["photo"]
  watermark = request.FILES["watermark"]
  fs = FileSystemStorage()
  photo_name=fs.save(image.name, image)
  photo_pathi = fs.url(photo_name)
  img=cv2.imread('.'+photo_pathi)
  _delete_file('.'+photo_pathi)
  
  photo_name=fs.save(watermark.name, watermark)
  photo_path = fs.url(photo_name)
  watermark=cv2.imread('.'+photo_path)
  _delete_file('.'+photo_path)
  img=cv2.resize(img, (500,400))
  watermark=cv2.resize(watermark, (500,400))
  img_free_2=(img>>2)<<2
  watermark_free_2=(watermark>>6)
  img_with_watermark=cv2.add(img_free_2,watermark_free_2)
  name_="./media/"+image.name
  cv2.imwrite(name_,img_with_watermark)
  
  save_file(request,name_)
  
  return render(request,"home.html")


  
  

  
  

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
  global text_key
  msg=request.POST['message']
  encoded=Encode(text_key,msg)
  save_text(request,encoded)
  return render(request,"home.html")

  

key=b'YmZSJC8FjMkKa9C98SoQVvFFKVbPk8vqoxdJDJFl56c='

text_key="2"