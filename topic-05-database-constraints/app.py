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

@app.route("/owners", methods=["GET"])
def get_owners_list():
    owners = database.get_owners()
    return render_template("owner_list.html", owners=owners)


@app.route("/owner/create", methods=["GET"])
def get_owner_create():
    return render_template("owner_create.html")


@app.route("/owner/create", methods=["POST"])
def post_owner_create():
    data = dict(request.form)
    database.create_owner(data)
    return redirect(url_for("get_owners_list"))


@app.route("/owner/delete/<id>", methods=["GET"])
def get_owner_delete(id):
    try:
        database.delete_owner(id)
        return redirect(url_for("get_owners_list"))
    except sqlite3.IntegrityError:
        owners = database.get_owners()
        error = "Error: Cannot delete this owner because they have pets. Please delete their pets first."
        return render_template("owner_list.html", owners=owners, error=error)

@app.route("/owner/update/<id>", methods=["GET"])
def get_owner_update(id):
    data = database.get_owner(id)
    return render_template("owner_update.html", data=data)


@app.route("/owner/update/<id>", methods=["POST"])
def post_owner_update(id):
    data = dict(request.form)
    database.update_owner(id, data)
    return redirect(url_for("get_owners_list"))
