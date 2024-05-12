from fastapi import FastAPI, File, UploadFile, Form, Response
import shutil
from S3 import S3Client
from dotenv import dotenv_values
from pymongo import MongoClient
import os
from pydantic import BaseModel
from typing import Union
from bson.objectid import ObjectId
from fastapi.responses import FileResponse
from imagga import  Imgga
import time
from mailgun import send_message
import pika, sys, os
import time

def startup_db_client():
    app.mongodb_client = MongoClient("mongodb+srv://cchw:Dfwc7O8ybY1N0Z0y@cluster0.4qejztu.mongodb.net/?retryWrites=true&w=majority")
    app.database = app.mongodb_client["Cluster0"]
    print("Connected to the MongoDB database!")
    app.collection = app.database["customers"]

app = FastAPI()
s3 = S3Client()
imga = Imgga()
startup_db_client()
connection = pika.BlockingConnection(pika.URLParameters("amqps://eyhzuagn:8Un16jJwLo3xnx1X5IHc-g4FeWMWBkSD@hawk.rmq.cloudamqp.com/eyhzuagn"))
channel = connection.channel()
channel.queue_declare(queue='postQueue')




@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

def tag_img(object_id: str):
    try:
        id = object_id
        objInstance = ObjectId(id)
        mydoc = app.collection.find_one({"_id": objInstance})
        filename = f"{id}.png"
        s3.download_from_aws(filename, 'cchw1', id)
        upload_id = imga.upload_img(object_id)
        data = imga.get_tags(upload_id)
        # print(data)
        accept = False
        max_condifence = data[0]['confidence'], data[0]["tag"]["en"]
        for i in data:
            if i['confidence'] > max_condifence[0]:
                max_condifence = i['confidence'], i["tag"]["en"]
            if i["confidence"] > 50 and i["tag"]["en"] == "vehicle":
                accept = True
        if accept:
            myquery = {"_id": objInstance}
            newvalues = {"$set": {"category": max_condifence[1]}}
            app.collection.update_one(myquery, newvalues)
            newvalues = {"$set": {"state": "accepted"}}
            app.collection.update_one(myquery, newvalues)
            send_message(mydoc["email"], "accepted")
        else:
            myquery = {"_id": objInstance}
            newvalues = {"$set": {"state": "rejected"}}
            app.collection.update_one(myquery, newvalues)
            send_message(mydoc["email"], "rejected")
        os.remove(f"./{filename}")
        return "accepted" if accept else "rejected"
    except:
        pass






def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    tag_img(body.decode("utf-8"))
    print("Task %r Done" % body)



channel.basic_consume(queue='postQueue', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()




# @app.get("/tag/{object_id}")





