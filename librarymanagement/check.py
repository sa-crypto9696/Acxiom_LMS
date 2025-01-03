# from pymongo import MongoClient
# from flask import Flask, render_template, request, redirect, url_for, flash, session


# app = Flask(__name__)
# app.secret_key = 'your_secret_key'

# # MongoDB connection
# client = MongoClient("mongodb://localhost:27017")  # Replace with your MongoDB URI
# db = client["library_db"]  # Replace with your database name

# user = db.users.find_one({"username": "admin", "password": "admin123"})
# print(user)