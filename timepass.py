import os
import sys
from datetime import datetime
from email.utils import formatdate
from os.path import isfile, join
from shutil import copyfile
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import face_recognition
from threading import *
import winsound
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


# for git push

db2 = connector.connect(
                    host="localhost",
                    user="ashwini",
                    passwd="dbms",

                )
cursor2 = db2.cursor()

databases = cursor2.fetchall()  ## it returns a list of all databases present

                ## printing the list of databases
print(databases)
