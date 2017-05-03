import os
from bson import Binary
from random import randint
from pymongo import MongoClient
from bson.objectid import ObjectId
from flask import Flask, current_app, request, render_template, url_for, make_response, json
from mimetypes import MimeTypes
import urllib
from json import loads
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route('/deposit', methods=['POST'])
def deposit():
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
	response = app.response_class(
		response = json.dumps({"status": "OK"}),
		status = 200,
		mimetype = "application/json"
	)
	return response

# /retrieve { docId }
@app.route('/retrieve/<docId>', methods=['GET'])
def retrieve(docId):
	client = MongoClient("127.0.0.1", 27017)
	db = client.wolfieclass
        docs = db.docs
        document = docs.find_one({"_id": ObjectId(docId)})
        response = make_response(document["content"])
	mime = MimeTypes()
	url = urllib.pathname2url(document["filename"])
        response.headers['Content-Type'] = mime.guess_type(url)[0]
        client.close()
	return response

# retrieves all links associated with a courseId
@app.route('/links/<courseId>', methods=['GET'])
def links(courseId):
        client = MongoClient("127.0.0.1", 27017)
        db = client.wolfieclass
        docs = db.docs
	courses = db.courses
        course = courses.find_one({"courseId": courseId})
	output = {"status": "OK", "links": []}
	for docId in course["docIds"]:
		document = docs.find_one({"_id": ObjectId(docId)})
		output.get("links").append({"link": docId, "filename": document["filename"]})
	#return output
	response = app.response_class(
		response = json.dumps(output),
		status=200,
		mimetype='application/json',
	)
	client.close()
	return response

@app.route('/delete', methods=['POST'])
def delete():
	data = loads(request.data)
	courseId = data.get('courseId')
	docId = data.get('docId')
	client = MongoClient("127.0.0.1", 27017)
	db = client.wolfieclass
	docs = db.docs
	courses = db.courses
	courses.update(
		{"courseId": courseId},
		{"$pull": {"docIds": docId}}
	)
	docs.delete_one({"_id": ObjectId(docId)})
	client.close()
	return app.response_class(
		response = json.dumps({}),
		status=200,
		mimetype='application/json'
	)

if __name__ == '__main__':
    app.run(debug=True)

