import os
from bson import Binary
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_restful import Resource, Api
from flask import Flask, current_app, request, render_template, url_for, make_response

UPLOAD_FOLDER = '/home/ubuntu/deposits'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 735344
api = Api(app)


# /deposit { contents: (type=file) }
class Deposit(Resource):
    # save image on cassandra
    def post(self):
        file = request.files['contents']
        courseId = request.values.get('courseId')
        filename = file.filename
        client = MongoClient("127.0.0.1", 27017)
        db = client.wolfieclass
        courses = db.courses
        docs = db.docs
        new_doc = docs.insert({
            "content": Binary(file.read()),
            "filename": filename
        })
        courses.update_one({"courseId": courseId}, {"$addToSet": {"docIds": str(new_doc)}}, upsert=True)
        client.close()
        return {"status": "OK"}


# /retrieve { filename: }
class Retrieve(Resource):
    def get(self, docId):
        client = MongoClient("127.0.0.1", 27017)
        db = client.wolfieclass
        docs = db.docs
        document = docs.find_one({"_id": ObjectId(docId)})
        response = make_response(document["content"])
        response.headers['Content-Type'] = "text/plain"
        return response


# retrieves all links associated with a courseId
class Links(Resource):
    def get(self, courseId):
        client = MongoClient("127.0.0.1", 27017)
        db = client.wolfieclass
        courses = db.courses
        doc = courses.find_one({"courseId": courseId})
        return {"status": "OK", "docIds": doc["docIds"]}

api.add_resource(Deposit, '/deposit')
api.add_resource(Retrieve, '/retrieve/<docId>')
api.add_resource(Links, '/links/<courseId>')

if __name__ == '__main__':
    app.run(debug=True)

