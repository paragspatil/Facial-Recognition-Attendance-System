import os
import sys
from datetime import datetime
from shutil import copyfile

import face_recognition
from threading import *

from mysql import connector
import xlsxwriter
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QDialog, QGroupBox, QHBoxLayout, \
    QVBoxLayout, \
    QLabel, QTableWidgetItem, QTableWidget, QHeaderView, QComboBox, QLineEdit, QFileDialog, QMenuBar

from ui_main_window import *

from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.models import load_model
import numpy as np

import imutils
import pickle

import cv2

try:
    db = connector.connect(
        host="localhost",
        user="root",
        passwd="dbms",
        database= "te division a"
    )

    # it will print a connection object if everything is fine
    cursor = db.cursor()

    """
    print('Connected to MySQL database')
    cursor.execute("SELECT * FROM " + "23_11_202014_09_25")
    # fetch all of the rows from the query
    data = cursor.fetchall()
    print("here")
    # print the rows
    for row in data:
        print("Id = ", row[0], )
        print("Name = ", row[1], "\n")
        print("attendance status = ", row[2], )
        print("time recorded ", row[3], "\n")

"""

    db = connector.connect(
        host="localhost",
        user="root",
        passwd="dbms"
    )

    # it will print a connection object if everything is fine
    print(db)
    cursor = db.cursor()
    c1 = "TE Division A"
    c2 = "TE Division B"
    cursor.execute("CREATE DATABASE `TE Division A`")
    cursor.execute("CREATE DATABASE `TE Division B`")

    ## creating a databse called 'datacamp'
    ## 'execute()' method is used to compile a 'SQL' statement
    ## below statement is used to create tha 'datacamp' database

    databases = cursor.fetchall()  ## it returns a list of all databases present

    ## printing the list of databases
    print(databases)

except Exception as e:
    print(e)
