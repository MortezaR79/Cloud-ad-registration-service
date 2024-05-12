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
from starlette.background import BackgroundTask
import pika


def cleanup(temp_file):
    os.remove(temp_file)

# class Item(BaseModel):
#     text: str
#     image: str
#     email: str
app = FastAPI()
s3 = S3Client()



@app.on_event("startup")
def startup_db_client():
    app.mongodb_client = MongoClient("mongodb+srv://cchw:Dfwc7O8ybY1N0Z0y@cluster0.4qejztu.mongodb.net/?retryWrites=true&w=majority")
    app.database = app.mongodb_client["Cluster0"]
    print("Connected to the MongoDB database!")
    app.collection = app.database["customers"]

@app.on_event("shutdown")
def shutdown_db_client():
    app.mongodb_client.close()

@app.put("/create/")
async def create_item( image: UploadFile, text: str = Form(), email: str = Form()):
    try:
        mydict = {"text": text, "email": email, "state": "pending", "category": None}
        x = app.collection.insert_one(mydict)
        filename = f"{x.inserted_id}.png"
        with open(filename, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        uploaded = s3.upload_to_aws(filename, 'cchw1', str(x.inserted_id))
        print(text, email)

        os.remove(f"./{filename}")
        connection = pika.BlockingConnection(pika.URLParameters("amqps://eyhzuagn:8Un16jJwLo3xnx1X5IHc-g4FeWMWBkSD@hawk.rmq.cloudamqp.com/eyhzuagn"))
        channel = connection.channel()
        channel.queue_declare(queue='postQueue')
        channel.basic_publish(exchange='', routing_key='postQueue', body=f"{x.inserted_id}")
        print(f" sent {x.inserted_id}")
        connection.close()
        return f"succesful {x.inserted_id}"
    except:
        pass


@app.get("/items/{object_id}")
def read_root(object_id: str, response: Response):
    try:
        id = object_id
        objInstance = ObjectId(id)
        mydoc = app.collection.find_one({"_id": objInstance})
        filename = f"{id}.png"
        s3.download_from_aws(filename, 'cchw1', id)

        headers = {"X-text": mydoc["text"], "X-category": mydoc["category"] if mydoc["category"] is not None else "none","X-state": mydoc["state"]  }
        print(mydoc)



        # return FileResponse(path=filename, filename=filename, media_type='image/png', headers=headers)
        if mydoc["state"] == "pending":
            os.remove(f"./{filename}")
            return "ad pending"
        if mydoc["state"] == "rejected":
            os.remove(f"./{filename}")
            return "ad rejected"

        # os.remove(f"./{filename}")
        return FileResponse(path=filename, filename=filename, media_type='image/png', headers=headers, background = BackgroundTask(cleanup, filename))
    except:
        pass

