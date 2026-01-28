from flask import Flask, render_template, request, redirect, url_for

# remember to $ pip install flask

app = Flask(__name__)

@app.route("/", methods=["GET"])
@app.route("/hello/<name>", methods=["GET"])
def get_hello(name="world"):
    # return f"<html><h1>Hello, {name}!<html>"
    return render_template("hello.html", name=name)

@app.route("/bye", methods=["GET"])
def get_bye():
    return "Bye!"

@app.route("/list", methods=["GET"])
def get_list():
    list = ["alpha","beta","gamma"]
    return render_template("list.html", list=list)
