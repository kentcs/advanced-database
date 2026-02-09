from flask import Flask, render_template, request, redirect, url_for

import database

# remember to $ pip install flask

database.initialize("pets.db")

app = Flask(__name__)

@app.route("/", methods=["GET"]) 
@app.route("/list", methods=["GET"])
def get_list():
    pets = database.get_pets()
    return render_template("list.html", pets=pets)     

@app.route("/create", methods=["GET"])
def get_create():
    return render_template("create.html")     

@app.route("/create", methods=["POST"])
def post_create():
    data = dict(request.form)
    database.create_pet(data)
    return redirect(url_for("get_list"))  

@app.route("/delete/<id>", methods=["GET"])
def get_delete(id):
    database.delete_pet(id)
    return redirect(url_for("get_list"))  

@app.route("/update/<id>", methods=["GET"])
def get_update(id):
    data = database.get_pet(id)
    return render_template("update.html",data=data)

@app.route("/update/<id>", methods=["POST"])
def post_update(id):
    data = dict(request.form)
    database.update_pet(id, data)
    return redirect(url_for("get_list"))  
