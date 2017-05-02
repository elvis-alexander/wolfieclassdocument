import os
from bson import Binary
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask_restful import Resource, Api
from flask import Flask, current_app, request, render_template, url_for, make_response
from mimetypes import MimeTypes
import urllib

UPLOAD_FOLDER = '/home/ubuntu/deposits'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 735344
api = Api(app)


# /deposit { contents: (type=file) }
class Deposit(Resource):
    # save image on cassandra
    def post(self):
	print request.values
	print request.form
        file = request.files['file']
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
	response = make_response("OK")
	response.headers.add('Access-Control-Allow-Origin', '*')
	return response
        #return {"status": "OK"}


# /retrieve { filename: }
class Retrieve(Resource):
    def get(self, docId):
        client = MongoClient("127.0.0.1", 27017)
        db = client.wolfieclass
        docs = db.docs
        document = docs.find_one({"_id": ObjectId(docId)})
        response = make_response(document["content"])
	mime = MimeTypes()
	url = urllib.pathname2url(document["filename"])
        response.headers['Content-Type'] = mime.guess_type(url)[0]
        return response


# retrieves all links associated with a courseId
class Links(Resource):
    def get(self, courseId):
	print 'courseId:', courseId
        client = MongoClient("127.0.0.1", 27017)
        db = client.wolfieclass
        docs = db.docs
	courses = db.courses
        course = courses.find_one({"courseId": courseId})
	output = {"status": "OK", "links": []}
	for docId in course["docIds"]:
		document = docs.find_one({"_id": ObjectId(docId)})
		output.get("links").append({"link": docId, "filename": document["filename"]})
	return output
        #return {"status": "OK", "docIds": doc["docIds"]}

api.add_resource(Deposit, '/deposit')
api.add_resource(Retrieve, '/retrieve/<docId>')
api.add_resource(Links, '/links/<courseId>')

if __name__ == '__main__':
    app.run(debug=True)

