#!/usr/bin/env bash

# chmod +x launcher.sh
# ./launcher HOST_IP

wget ""

sudo apt-get update
sudo apt-get install python-pip
sudo pip install pymango
sudo pip install gitpython
sudo pip install flask
sudo pip install flask_restful
sudo pip install python-magic
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 0C49F3730359A14518585931BC711F9BA15703C6
sudo echo "deb [ arch=amd64 ] http://repo.mongodb.org/apt/ubuntu trusty/mongodb-org/3.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-3.4.list
sudo apt-get update
sudo apt-get install -y mongodb-org
service mongod status
mongo --host 127.0.0.1 --port 27017 < "use wolfieclass"
mongo --host 127.0.0.1 --port 27017 < "show dbs"



#cqlsh < "CREATE TABLE docs(courseId text, contents blob, filename text, docId bigint, mimetype text, PRIMARY KEY(docId, courseId));"
#export FLASK_APP=app.py
#sudo flask run --host=0.0.0.0 --port=80

