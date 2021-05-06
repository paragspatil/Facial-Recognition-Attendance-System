import os
import sys
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
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
import pymysql
import imutils
import pickle
import cv2


class Window(QDialog):
    def __init__(self):
        super().__init__()
        file = open("logindetail.txt", "r+")
        lines = file.readlines()
        self.username = lines[0]
        self.password = lines[1]
        self.username = self.username[0:len(self.username) - 1]
        self.password = self.password[0:len(self.password)]
        file.close()
        # print(self.username)
        # print(self.password)

        self.modelPath = os.path.sep.join(["my-liveness-detection", "face_detector",
                                           "res10_300x300_ssd_iter_140000.caffemodel"])
        self.protoPath = os.path.sep.join(["my-liveness-detection", "face_detector", "deploy.prototxt"])
        self.mainBackground = QImage("resorces/mainbac2.png")
        self.isAttendance = False
        self.title = "Face recognition Layout"
        self.left = 700
        self.top = 700
        self.width = 1000
        self.height = 1000
        self.IconName = "resorces/face-recognition.png"
        self.initWindow()
        os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

        # setting background image of main window
        simage = self.mainBackground.scaled(QSize(self.width, self.height))
        pallate = QtGui.QPalette()
        pallate.setBrush(QtGui.QPalette.Window, QtGui.QBrush(simage))
        self.setPalette(pallate)

    def initWindow(self):
        self.setWindowIcon(QtGui.QIcon(self.IconName))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.SelectClassLayout()
        self.UtilityactionsWindow()
        self.createTable()
        vbox = QVBoxLayout()
        vbox.addWidget(self.groupbox)
        vbox.addWidget(self.groupbox2)
        vbox.addWidget(self.tableWidget)
        self.cameraGroupBox = QGroupBox()
        self.cameraGroupBox.setMinimumHeight(600)
        self.initCameraBox()
        vbox.addWidget(self.cameraGroupBox)
        self.setLayout(vbox)
        self.setStyleSheet("background-color :#89ABE3FF")

        self.show()

    def SelectClassLayout(self):
        self.groupbox = QGroupBox()
        hboxlayout = QHBoxLayout()

        label = QPushButton("access attendance archives")
        label.setStyleSheet("background-color :#FCF6F5FF")
        label.setMinimumHeight(40)
        label.clicked.connect(self.accessrecordedAttendance)
        hboxlayout.addWidget(label)

        self.comboBox = QComboBox(self)
        self.comboBox.setToolTip("select class")
        classes = os.listdir("classes")
        numOfClasses = len(classes)
        for c in classes:
            self.comboBox.addItem(c)
        self.comboBox.setStyleSheet("background-color :#FCF6F5FF")
        self.comboBox.setMinimumHeight(40)

        hboxlayout.addWidget(self.comboBox)
        self.groupbox.setLayout(hboxlayout)

    def UtilityactionsWindow(self):
        self.groupbox2 = QGroupBox("utility actions")
        hboxlayout = QHBoxLayout()

        addstudentButton = QPushButton("add new student")
        addstudentButton.setToolTip("click here to add new student to selected class")
        addstudentButton.setMinimumHeight(40)
        addstudentButton.setStyleSheet("background-color :#FCF6F5FF")
        addstudentButton.clicked.connect(self.addnewStudent)
        hboxlayout.addWidget(addstudentButton)

        addnewclassbutton = QPushButton("add new class")
        addnewclassbutton.setToolTip("click here to add a new class")
        addnewclassbutton.setMaximumHeight(40)
        addnewclassbutton.setStyleSheet("background-color :#FCF6F5FF")
        addnewclassbutton.clicked.connect(self.addnewClass)
        hboxlayout.addWidget(addnewclassbutton)

        self.startattendenceButton = QPushButton("Start Attendance session")
        self.startattendenceButton.setToolTip("Start Attendance session for selected class")
        self.startattendenceButton.setMinimumHeight(40)
        self.startattendenceButton.setStyleSheet("background-color :#FCF6F5FF")
        self.startattendenceButton.clicked.connect(self.StartAttendenceSession)
        hboxlayout.addWidget(self.startattendenceButton)

        self.groupbox2.setLayout(hboxlayout)

    def createTable(self):
        self.tableWidget = QTableWidget()

        # Row count
        self.tableWidget.setRowCount(80)

        # Column count
        self.tableWidget.setColumnCount(4)

        self.tableWidget.setHorizontalHeaderLabels(["Roll No", "Name", "Attendance Status", "Time Recorded"])

        # Table will fit the screen horizontally
        self.tableWidget.horizontalHeader().setStretchLastSection(True)
        self.tableWidget.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch)
        self.tableWidget.setStyleSheet("background-color :#FCF6F5FF")

    def initCameraBox(self):
        camerabuttonLayout = QHBoxLayout()
        camreraButtonBox = QGroupBox()

        camerahboxlayout = QVBoxLayout()
        self.exportToExcelButton = QPushButton("Export to excel")
        self.exportToExcelButton.setMinimumHeight(40)
        self.exportToExcelButton.clicked.connect(self.Exporttoexcel)
        self.exportToExcelButton.setIcon(QtGui.QIcon("resorces/excel.png"))
        self.exportToExcelButton.setStyleSheet("background-color :#FCF6F5FF")
        camerabuttonLayout.addWidget(self.exportToExcelButton)

        self.exportToDataBaseButton = QPushButton("Export to DataBase")
        self.exportToDataBaseButton.setMinimumHeight(40)
        self.exportToDataBaseButton.setIcon(QtGui.QIcon("resorces/database.png"))
        camerabuttonLayout.addWidget(self.exportToDataBaseButton)
        self.exportToDataBaseButton.clicked.connect(self.exportToMysql)
        self.exportToDataBaseButton.setStyleSheet("background-color :#FCF6F5FF")
        camreraButtonBox.setMaximumHeight(50)
        camreraButtonBox.setLayout(camerabuttonLayout)
        camerahboxlayout.addWidget(camreraButtonBox)

        self.cameraoutput = QLabel()
        self.cameraoutput.setMinimumHeight(180)
        camerahboxlayout.addWidget(self.cameraoutput)

        self.eventlogsbox = QLineEdit()
        self.eventlogsbox.setMaximumHeight(20)
        self.eventlogsbox.setText("Welcome, this is where you will see event logs")
        self.eventlogsbox.setStyleSheet("background-color :#FCF6F5FF")
        camerahboxlayout.addWidget(self.eventlogsbox)

        self.cameraGroupBox.setLayout(camerahboxlayout)

    def StartAttendenceSession(self):
         try:
            if not self.isAttendance:
                self.isAttendance = True
                self.cap = cv2.VideoCapture(0)
                model = load_model("my-liveness-detection/liveness.model")
                self.listofstudentRollnos = []
                fakeCount = 0
                self.startattendenceButton.setStyleSheet("background-color : red")
                self.startattendenceButton.setText("stop Attendance session")
                studentImages = []
                studentImagesEncodings = []
                self.attendanceStatus = []
                self.timeRecorded = []
                path = "classes/" + self.comboBox.currentText() + "/Students Data/"
                self.listOfstudents = os.listdir(path)
                i = 0
                for student in self.listOfstudents:
                    currentImage = cv2.imread(path + student + "/" + student + ".jpg")
                    studentImages.append(currentImage)
                    currentImage = cv2.cvtColor(currentImage, cv2.COLOR_BGR2RGB)
                    encode = face_recognition.face_encodings(currentImage)[0]
                    studentImagesEncodings.append(encode)

                    self.tableWidget.setItem(i, 1, QTableWidgetItem(student))
                    self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i)))
                    self.tableWidget.setItem(i, 2, QTableWidgetItem("Absent"))
                    self.listofstudentRollnos.append(i + 1)
                    self.attendanceStatus.append("Absent")
                    self.timeRecorded.append("not recorded")
                    i = i + 1

                # code for fake and real person detection
                net = cv2.dnn.readNetFromCaffe(self.protoPath, self.modelPath)

                # load the liveness detector model and label encoder from disk
                try:
                    self.eventlogsbox.setText("[INFO] loading liveness detector...")
                    le = pickle.loads(open("my-liveness-detection/le.pickle", "rb").read())

                except Exception as e:
                    print(e)
                while self.isAttendance:
                    success, img = self.cap.read()
                    frame = img
                    imgs = cv2.resize(img, (0, 0), None, 0.25, 0.25)
                    imgs = cv2.cvtColor(imgs, cv2.COLOR_BGR2RGB)

                    facecurrentframe = face_recognition.face_locations(imgs)
                    encodecurrentframe = face_recognition.face_encodings(imgs, facecurrentframe)
                    try:

                        cv2.rectangle(img, (facecurrentframe[0][3] * 4, facecurrentframe[0][0] * 4),
                                      (facecurrentframe[0][1] * 4, facecurrentframe[0][2] * 4), (255, 0, 255),
                                      2)
                    except Exception as e:
                    # processing frame for liveness detection
                        pass

                    self.displayImage(img, 1)
                    cv2.waitKey()
                    frame = imutils.resize(frame, width=600)

                    # grab the frame dimensions and convert it to a blob
                    (h, w) = frame.shape[:2]
                    blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0,
                                                 (300, 300), (104.0, 177.0, 123.0))
                    # pass the blob through the network and obtain the detections and
                    # predictions
                    net.setInput(blob)
                    detections = net.forward()

                    # loop over the detections
                    for i in range(0, detections.shape[2]):
                        # extract the confidence (i.e., probability) associated with the
                        # prediction
                        confidence = detections[0, 0, i, 2]
                        # filter out weak detections
                        if confidence > 0.5:
                            # compute the (x, y)-coordinates of the bounding box for
                            # the face and extract the face ROI
                            box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                            (startX, startY, endX, endY) = box.astype("int")
                            # ensure the detected bounding box does fall outside the
                            # dimensions of the frame
                            startX = max(0, startX)
                            startY = max(0, startY)
                            endX = min(w, endX)
                            endY = min(h, endY)
                            # extract the face ROI and then preproces it in the exact
                            # same manner as our training data
                            face = frame[startY:endY, startX:endX]
                            face = cv2.resize(face, (32, 32))
                            face = face.astype("float") / 255.0
                            face = img_to_array(face)
                            face = np.expand_dims(face, axis=0)
                            # pass the face ROI through the trained liveness detector
                            # model to determine if the face is "real" or "fake"
                            preds = model.predict(face)[0]
                            j = np.argmax(preds)
                            label = le.classes_[j]
                            # print(label)

                            if label == "fake":

                                fakeCount += 1
                                if fakeCount > 9:
                                    frequency = 2500  # Set Frequency To 2500 Hertz
                                    duration = 2000  # Set Duration To 1000 ms == 1 second
                                    winsound.Beep(frequency, duration)
                                    self.eventlogsbox.setText("don't cheat attendance; serious action will be taken")

                            elif label == "real":
                                fakeCount = 0
                                for encodeface, faceLoc in zip(encodecurrentframe, facecurrentframe):
                                    matches = face_recognition.compare_faces(studentImagesEncodings, encodeface)
                                    faceDis = face_recognition.face_distance(studentImagesEncodings, encodeface)
                                    matchIndex = np.argmin(faceDis)

                                    if matches[matchIndex]:
                                        # print(self.listOfstudents[matchIndex])

                                        self.tableWidget.setItem(matchIndex, 2, QTableWidgetItem("Present"))
                                        now = datetime.now()
                                        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                                        self.tableWidget.setItem(matchIndex, 3, QTableWidgetItem(dt_string))
                                        self.attendanceStatus[matchIndex] = "Present"
                                        self.timeRecorded[matchIndex] = dt_string
                                        self.eventlogsbox.setText(self.listOfstudents[matchIndex]
                                                                  + " your attendance has been recorded successfully")

            else:
                self.isAttendance = False
                self.cap.release()
                self.cameraoutput.clear()
                self.startattendenceButton.setText("Start Attendance session")
                self.startattendenceButton.setStyleSheet("background-color :#FCF6F5FF")
         except Exception as e:
            print(e)

    def Exporttoexcel(self):
        i = 0
        if len(self.listofstudentRollnos) > 0:
            now = datetime.now()
            dt_string = now.strftime("%d-%m-%Y %H-%M-%S")
            # print(dt_string)
            print(os.path.isdir("classes/" + self.comboBox.currentText() + "/attendence recods"))
            # writing to excel
            workbook = xlsxwriter.Workbook(
                "classes/" + self.comboBox.currentText() + "/attendence recods/" + dt_string + '.xlsx')

            # By default worksheet names in the spreadsheet will be
            # Sheet1, Sheet2 etc., but we can also specify a name.
            worksheet = workbook.add_worksheet("My sheet")

            # Some data we want to write to the worksheet.

            # Start from the first cell. Rows and
            # columns are zero indexed.
            worksheet.write(0, 0, "Roll No")
            worksheet.write(0, 1, "Names")
            worksheet.write(0, 2, "Attendance Status")
            worksheet.write(0, 3, "Time Recorded")
            row = 1
            col = 0

            # Iterate over the data and write it out row by row.
            i = 0
            while i < len(self.listOfstudents):
                worksheet.write(i + 1, 0, self.listofstudentRollnos[i])
                worksheet.write(i + 1, 1, self.listOfstudents[i])
                worksheet.write(i + 1, 2, self.attendanceStatus[i])
                worksheet.write(i + 1, 3, self.timeRecorded[i])
                i += 1

            self.eventlogsbox.setText("your attendce has been save in " + "classes/" + self.comboBox.currentText()
                                      + "/attendence recods/" + dt_string + '.xlsx')

            workbook.close()

    def exportToMysql(self):
        if True:
            try:
                db = connector.connect(
                    host="localhost",
                    user=self.username,
                    passwd=self.password,
                    database=self.comboBox.currentText()
                )

                # it will print a connection object if everything is fine
                cursor = db.cursor()
                now = datetime.now()
                dt_string = now.strftime("%d_%m_%Y%H_%M_%S")

                cursor.execute(
                    "CREATE TABLE " + dt_string + "(Roll_no INT(11) PRIMARY KEY,name VARCHAR(255), attendance_status "
                                                  "VARCHAR(255),Time_Recorded VARCHAR(255))")
                cursor.execute("SHOW TABLES")

                tables = cursor.fetchall()  ## it returns list of tables present in the database

                for i in range(0, len(self.listofstudentRollnos)):
                    query = "INSERT INTO " + dt_string + "(Roll_no, name,attendance_status,Time_Recorded) VALUES (%s, " \
                                                         "%s, %s, %s) "
                    ## storing values in a variable
                    values = (self.listofstudentRollnos[i], self.listOfstudents[i], self.attendanceStatus[i],
                              self.timeRecorded[i])

                    ## executing the query with values
                    cursor.execute(query, values)

                    ## to make final output we have to run the 'commit()' method of the database object
                    db.commit()

                self.eventlogsbox.setText("attendance session saved successfully in SQL")





            except Exception as e:
                print(e)

            # here goes the fuction to save stuff to mysql database

    def addnewStudent(self):
        self.isnameentered = False
        self.isimageselected = False
        self.dialog = QDialog()
        self.dialog.setWindowIcon(QtGui.QIcon(self.IconName))
        self.dialog.setModal(True)
        self.dialog.setWindowTitle("add a new Student")
        self.dialog.setGeometry(350, 350, 500, 500)
        self.dialog.setStyleSheet("background-color :#89ABE3FF")

        addnewstudnetBackground = QImage("resorces/add_student_background.jpg")
        simage = addnewstudnetBackground.scaled(QSize(self.dialog.width(), self.dialog.height()))
        pallate = QtGui.QPalette()
        pallate.setBrush(QtGui.QPalette.Window, QtGui.QBrush(simage))
        self.dialog.setPalette(pallate)

        self.selectClass = QComboBox(self.dialog)
        self.selectClass.setToolTip("select class")
        classes = os.listdir("classes")
        numOfClasses = len(classes)
        for c in classes:
            self.selectClass.addItem(c)
        self.selectClass.setMinimumHeight(40)
        self.selectClass.setMinimumWidth(60)
        self.selectClass.move(200, 50)
        self.selectClass.setStyleSheet("background-color :#FCF6F5FF")

        namelable = QLabel("Enter Student Name below", self.dialog)
        namelable.setMinimumWidth(100)
        namelable.setMinimumHeight(40)
        namelable.move(175, 125)
        namelable.setStyleSheet("background-color :#FCF6F5FF")

        self.nametextbox = QLineEdit(self.dialog)
        self.nametextbox.setMinimumWidth(200)
        self.nametextbox.move(150, 175)
        self.nametextbox.setStyleSheet("background-color :#FCF6F5FF")

        chooseStudentImageLable = QLabel("select student Image", self.dialog)
        chooseStudentImageLable.setMinimumHeight(40)
        chooseStudentImageLable.move(200, 200)
        chooseStudentImageLable.setStyleSheet("background-color :#FCF6F5FF")

        chooseImageButton = QPushButton("Choose Image", self.dialog)
        chooseImageButton.setMinimumHeight(40)
        chooseImageButton.move(200, 250)
        chooseImageButton.clicked.connect(self.chooseImage)
        chooseImageButton.setStyleSheet("background-color :#FCF6F5FF")

        self.imageNameLable = QLabel("no Image selected", self.dialog)
        self.imageNameLable.setMinimumHeight(40)
        self.imageNameLable.setMinimumWidth(300)
        self.imageNameLable.move(100, 300)
        self.imageNameLable.setStyleSheet("background-color :#FCF6F5FF")

        saveStudentButton = QPushButton("Save Student", self.dialog)
        saveStudentButton.setMinimumHeight(40)
        saveStudentButton.move(200, 400)
        saveStudentButton.clicked.connect(self.savenewstudent)
        saveStudentButton.setStyleSheet("background-color :#FCF6F5FF")

        self.dialog.exec_()

    def addnewClass(self):
        self.classdialog = QDialog()
        self.classdialog.setWindowIcon(QtGui.QIcon(self.IconName))
        self.classdialog.setModal(True)
        self.classdialog.setWindowTitle("add a new class")
        self.classdialog.setGeometry(350, 350, 500, 300)
        self.classdialog.setStyleSheet("background-color :#89ABE3FF")

        self.classnametextbox = QLineEdit(self.classdialog)
        self.classnametextbox.setMinimumWidth(300)
        self.classnametextbox.move(100, 75)
        self.classnametextbox.setStyleSheet("background-color :#FCF6F5FF")

        addclassbutton = QPushButton("add new class", self.classdialog)
        addclassbutton.setMinimumWidth(100)
        addclassbutton.clicked.connect(self.createnewclass)
        addclassbutton.move(200, 150)
        addclassbutton.setStyleSheet("background-color :#FCF6F5FF")

        self.classdialog.exec_()

    def createnewclass(self):
        if self.classnametextbox.text() != "":
            path = "classes/" + self.classnametextbox.text()
            os.mkdir(path)
            os.mkdir(path + "/" + "Students Data")
            os.mkdir(path + "/" + "attendence recods")
            self.eventlogsbox.setText("new class with name " + self.classnametextbox.text() + " has been added "
                                                                                              "successfully restart app to access new class")
            self.classdialog.close()
            try:
                db = connector.connect(
                    host="localhost",
                    user=self.username,
                    passwd=self.password
                )

                # it will print a connection object if everything is fine
                print(db)
                cursor = db.cursor()
                classname = self.classnametextbox.text();
                cursor.execute("CREATE DATABASE " + "`" + classname + "`")


            except Exception as e:
                print(e)

        else:
            self.eventlogsbox.setText("enter name of class first")

    def chooseImage(self):
        fname = QFileDialog.getOpenFileName(self.dialog, 'Open File', 'C\\', 'Image files (*.jpg *.png)')
        self.ImagePath = fname[0]
        self.imageNameLable.setText(self.ImagePath)
        self.isimageselected = True

    def savenewstudent(self):
        self.isnameentered = self.nametextbox.text() != ""
        if (self.isimageselected and self.isnameentered):
            path = "classes/" + self.selectClass.currentText() + "/Students Data"
            try:
                os.mkdir(path + "/" + self.nametextbox.text())
                copyfile(self.ImagePath,
                         path + "/" + self.nametextbox.text() + "/" + self.nametextbox.text() + self.ImagePath[len(
                             self.ImagePath) - 4:len(self.ImagePath)])
            except Exception as e:
                print(e.msg)

            self.eventlogsbox.setText(
                "new student named " + self.nametextbox.text() + " has been added successfully to " +
                self.selectClass.currentText())

            self.dialog.close()



        else:
            self.imageNameLable.setText("select Image and enter name first")

    def accessrecordedAttendance(self):
        self.chooserecordDialog = QDialog()
        self.chooserecordDialog.setWindowIcon(QtGui.QIcon(self.IconName))
        self.chooserecordDialog.setModal(True)
        self.chooserecordDialog.setWindowTitle("select record type")
        self.chooserecordDialog.setGeometry(350, 350, 500, 300)
        self.chooserecordDialog.setStyleSheet("background-color :#89ABE3FF")

        chooseexcelButton = QPushButton("access attendance recorded in excel", self.chooserecordDialog)
        chooseexcelButton.setMinimumWidth(300)
        chooseexcelButton.move(100, 75)
        chooseexcelButton.setStyleSheet("background-color :#FCF6F5FF")
        chooseexcelButton.clicked.connect(self.accessExcelRecords)

        choosemysqlButton = QPushButton("access attendance recorded in MySQL", self.chooserecordDialog)
        choosemysqlButton.setMinimumWidth(300)
        choosemysqlButton.clicked.connect(self.accessMysqlRecords)
        choosemysqlButton.move(100, 150)
        choosemysqlButton.setStyleSheet("background-color :#FCF6F5FF")

        self.chooserecordDialog.exec_()

    def accessExcelRecords(self):
        self.chooserecordDialog.close()
        self.excelRecordDialog = QDialog()
        self.excelRecordDialog.setWindowIcon(QtGui.QIcon(self.IconName))
        self.excelRecordDialog.setModal(True)
        self.excelRecordDialog.setWindowTitle("select attendance record")
        self.excelRecordDialog.setGeometry(500, 500, 500, 300)
        self.excelRecordDialog.setStyleSheet("background-color :#89ABE3FF")

        path = "classes/" + self.comboBox.currentText() + "/attendence recods/"
        onlyfiles = [f for f in os.listdir(path) if isfile(join(path, f))]

        self.excelcombo = QComboBox(self.excelRecordDialog)
        self.excelcombo.setToolTip("select Record")
        self.excelcombo.setMinimumWidth(300)
        self.excelcombo.move(100, 50)
        self.excelcombo.setStyleSheet("background-color :#FCF6F5FF")

        for f in onlyfiles:
            self.excelcombo.addItem(f)

        self.emailIDtextBox = QLineEdit(self.excelRecordDialog)
        self.emailIDtextBox.setMinimumWidth(300)
        self.emailIDtextBox.setToolTip("enter your email ID here")
        self.emailIDtextBox.move(100, 100)
        self.emailIDtextBox.setStyleSheet("background-color :#FCF6F5FF")

        sendEmailButton = QPushButton("send me an email", self.excelRecordDialog)
        sendEmailButton.setMinimumWidth(300)
        sendEmailButton.move(100, 150)
        sendEmailButton.setStyleSheet("background-color :#FCF6F5FF")
        sendEmailButton.clicked.connect(self.sendexcelEmail)

        self.excelRecordDialog.exec_()

    def accessMysqlRecords(self):
        self.chooserecordDialog.close()
        try:
            self.mySQLRecordDialog = QDialog()
            self.mySQLRecordDialog.setWindowIcon(QtGui.QIcon(self.IconName))
            self.mySQLRecordDialog.setModal(True)
            self.mySQLRecordDialog.setWindowTitle("select attendance record")
            self.mySQLRecordDialog.setGeometry(500, 500, 500, 300)
            self.mySQLRecordDialog.setStyleSheet("background-color :#89ABE3FF")

            path = "classes/" + self.comboBox.currentText() + "/attendence recods/"

            self.mySQLcombo = QComboBox(self.mySQLRecordDialog)
            self.mySQLcombo.setToolTip("select Record")
            self.mySQLcombo.setMinimumWidth(300)
            self.mySQLcombo.move(100, 50)
            self.mySQLcombo.setStyleSheet("background-color :#FCF6F5FF")

            db = connector.connect(
                host="localhost",
                user=self.username,
                passwd=self.password,
                database=self.comboBox.currentText()
            )

            # it will print a connection object if everything is fine
            cursor = db.cursor()
            cursor.execute("SHOW TABLES")
            for (table_name,) in cursor:
                self.mySQLcombo.addItem(table_name)

            showintableButton = QPushButton("view in Table", self.mySQLRecordDialog)
            showintableButton.setMinimumWidth(300)
            showintableButton.move(100, 100)
            showintableButton.setStyleSheet("background-color :#FCF6F5FF")
            showintableButton.clicked.connect(self.showSQLinTable)

            self.emailIDtextBox = QLineEdit(self.mySQLRecordDialog)
            self.emailIDtextBox.setMinimumWidth(300)
            self.emailIDtextBox.setToolTip("enter your email ID here")
            self.emailIDtextBox.move(100, 150)
            self.emailIDtextBox.setStyleSheet("background-color :#FCF6F5FF")

            sendEmailButton = QPushButton("send me an email", self.mySQLRecordDialog)
            sendEmailButton.setMinimumWidth(300)
            sendEmailButton.move(100, 200)
            sendEmailButton.setStyleSheet("background-color :#FCF6F5FF")
            sendEmailButton.clicked.connect(self.sendMySQLEmail)

            self.mySQLRecordDialog.exec_()
        except Exception as e:
            print(e)

    def sendMySQLEmail(self):
        try:
            if not os.path.isfile(
                    "classes/" + self.comboBox.currentText() + "/attendence recods/" + self.mySQLcombo.currentText() + '.xlsx'):
                db = connector.connect(
                    host="localhost",
                    user=self.username,
                    passwd=self.password,
                    database=self.comboBox.currentText()
                )
                cur = db.cursor()
                cur.execute(
                    "SELECT Roll_no, name, attendance_status, Time_Recorded  FROM " + self.mySQLcombo.currentText())
                result_set = cur.fetchall()
                workbook = xlsxwriter.Workbook(
                    "classes/" + self.comboBox.currentText() + "/attendence recods/" + self.mySQLcombo.currentText() + '.xlsx')

                # By default worksheet names in the spreadsheet will be
                # Sheet1, Sheet2 etc., but we can also specify a name.
                worksheet = workbook.add_worksheet("My sheet")

                # Some data we want to write to the worksheet.

                # Start from the first cell. Rows and
                # columns are zero indexed.
                worksheet.write(0, 0, "Roll No")
                worksheet.write(0, 1, "Names")
                worksheet.write(0, 2, "Attendance Status")
                worksheet.write(0, 3, "Time Recorded")
                row = 1
                col = 0

                # Iterate over the data and write it out row by row.
                i = 0
                for row in result_set:
                    worksheet.write(i + 1, 0, i + 1)
                    worksheet.write(i + 1, 1, row[1])
                    worksheet.write(i + 1, 2, row[2])
                    worksheet.write(i + 1, 3, row[3])
                    i = i + 1

                workbook.close()

            if len(self.emailIDtextBox.text()) > 0:

                mail_content = '''Hello,
                            this is the attendance you requested in excel format this is
                            an automated message from facial-recognition-attendance-system
                            app 
                            '''
                # Setup the MIME
                msg = MIMEMultipart()
                msg['From'] = "facialrecognitionsytem@gmail.com"
                msg['To'] = self.emailIDtextBox.text()
                msg['Date'] = formatdate(localtime=True)
                msg['Subject'] = "requested attendance"
                msg.attach(MIMEText(mail_content))

                part = MIMEBase('application', "octet-stream")
                part.set_payload(
                    open(
                        "classes/" + self.comboBox.currentText() + "/attendence recods/" + self.mySQLcombo.currentText() + ".xlsx",
                        "rb").read())
                encoders.encode_base64(part)
                part.add_header('Content-Disposition',
                                'attachment; filename=" ' + self.mySQLcombo.currentText() + ".xlsx")
                msg.attach(part)

                smtp = smtplib.SMTP('smtp.gmail.com', 587)
                smtp.starttls()
                smtp.login("facialrecognitionsytem@gmail.com", "Parag@1999")
                smtp.sendmail("facialrecognitionsytem@gmail.com", self.emailIDtextBox.text(), msg.as_string())
                self.eventlogsbox.setText(
                    "sql record saved as " + self.mySQLcombo.currentText() + ".xlsx" + "and sent to" +
                    self.emailIDtextBox.text())
                smtp.quit()

            else:
                self.eventlogsbox.setText("enter email ID first")







        except Exception as e:
            print(e)

    def showSQLinTable(self):
        self.mySQLRecordDialog.close()
        try:
            db = connector.connect(
                host="localhost",
                user=self.username,
                passwd=self.password,
                database=self.comboBox.currentText()
            )
            cur = db.cursor()
            cur.execute("SELECT Roll_no, name, attendance_status, Time_Recorded  FROM " + self.mySQLcombo.currentText())
            result_set = cur.fetchall()
            i = 0
            for row in result_set:
                self.tableWidget.setItem(i, 0, QTableWidgetItem(str(i + 1)))
                self.tableWidget.setItem(i, 1, QTableWidgetItem(row[1]))
                self.tableWidget.setItem(i, 2, QTableWidgetItem(row[2]))
                self.tableWidget.setItem(i, 3, QTableWidgetItem(row[3]))
                i += 1






        except Exception as e:
            print(e)

    def sendexcelEmail(self):
        try:
            mail_content = '''Hello,
            this is the attendance you requested in excel format this is
            an automated message from facial-recognition-attendance-system
            app 
            '''
            # Setup the MIME
            msg = MIMEMultipart()
            msg['From'] = "facialrecognitionsytem@gmail.com"
            msg['To'] = self.emailIDtextBox.text()
            msg['Date'] = formatdate(localtime=True)
            msg['Subject'] = "requested attendance"
            msg.attach(MIMEText(mail_content))

            part = MIMEBase('application', "octet-stream")
            part.set_payload(
                open("classes/" + self.comboBox.currentText() + "/attendence recods/" + self.excelcombo.currentText(),
                     "rb").read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment; filename=" ' + self.excelcombo.currentText())
            msg.attach(part)

            smtp = smtplib.SMTP('smtp.gmail.com', 587)
            smtp.starttls()
            smtp.login("facialrecognitionsytem@gmail.com", "Parag@1999")
            smtp.sendmail("facialrecognitionsytem@gmail.com", self.emailIDtextBox.text(), msg.as_string())
            self.eventlogsbox.setText("email sent to " + self.emailIDtextBox.text())
            smtp.quit()

        except Exception as e:
            print(e)

    def displayImage(self, img, window=1):
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qformat = QImage.Format_RGBA8888

            else:
                qformat = QImage.Format_RGB888

        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()
        self.cameraoutput.setPixmap(QPixmap.fromImage(img))
        self.cameraoutput.setAlignment(QtCore.Qt.AlignCenter | QtCore.Qt.AlignVCenter)


class loginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.left = 500
        self.top = 500
        self.width = 500
        self.height = 500
        self.initWindow()

    def initWindow(self):
        self.setWindowTitle("login")
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.initUI()
        self.show()

    def initUI(self):
        self.usernamebox = QLineEdit(self)
        self.usernamebox.setMaximumHeight(40)
        self.usernamebox.setText("Welcome, enter your username here")
        self.usernamebox.setMinimumWidth(300)
        self.usernamebox.move(100, 50)
        self.usernamebox.setStyleSheet("background-color :#FCF6F5FF")

        self.passwordbox = QLineEdit(self)
        self.passwordbox.setMaximumHeight(40)
        self.passwordbox.setText("enter your password here")
        self.passwordbox.setMinimumWidth(300)
        self.passwordbox.move(100, 100)
        self.passwordbox.setStyleSheet("background-color :#FCF6F5FF")

        loginbutton = QPushButton("Login", self)
        loginbutton.setMaximumHeight(40)
        loginbutton.setMinimumWidth(100)
        loginbutton.move(200, 150)
        loginbutton.setStyleSheet("background-color :#FCF6F5FF")
        loginbutton.clicked.connect(self.loginfunc)

        accountlable = QLabel(self)
        accountlable.setText("Don't have a account?, register below")
        accountlable.setMinimumWidth(300)
        accountlable.setMaximumHeight(40)
        accountlable.move(100, 200)

        createAccountButton = QPushButton("create new account", self)
        createAccountButton.setMaximumHeight(40)
        createAccountButton.setMinimumWidth(200)
        createAccountButton.move(150, 250)
        createAccountButton.setStyleSheet("background-color :#FCF6F5FF")
        createAccountButton.clicked.connect(self.createnewaccout)

        self.debugLable = QLabel(self)
        self.debugLable.setMinimumHeight(200)
        self.debugLable.setMinimumWidth(400)
        self.debugLable.move(50, 300)

    def loginfunc(self):
        try:
            username = self.usernamebox.text()
            password = self.passwordbox.text()
            db = connector.connect(
                host="localhost",
                user=username,
                passwd=password,

            )
            open('logindetail.txt', 'w').close()
            file = open("logindetail.txt", "r+")
            file.writelines([username + "\n", password])
            file.close()
            self.hide()
            self.window = Window()
            self.window.show()
        except Exception as e:
            self.debugLable.setText("something is wrong try again with correct username and password or"

                                    " create a new account")

    def createnewaccout(self):
        self.isadminloggedin = False
        self.createaccdialog = QDialog()
        self.createaccdialog.setGeometry(500, 500, 500, 500)

        self.adminusernamebox = QLineEdit(self.createaccdialog)
        self.adminusernamebox.setMaximumHeight(40)
        self.adminusernamebox.setText("Welcome, enter admins username here")
        self.adminusernamebox.setMinimumWidth(300)
        self.adminusernamebox.move(100, 50)
        self.adminusernamebox.setStyleSheet("background-color :#FCF6F5FF")

        self.adminpasswordbox = QLineEdit(self.createaccdialog)
        self.adminpasswordbox.setMaximumHeight(40)
        self.adminpasswordbox.setText("enter admins password here")
        self.adminpasswordbox.setMinimumWidth(300)
        self.adminpasswordbox.move(100, 100)
        self.adminpasswordbox.setStyleSheet("background-color :#FCF6F5FF")

        loginbutton = QPushButton("Login", self.createaccdialog)
        loginbutton.setMaximumHeight(40)
        loginbutton.setMinimumWidth(100)
        loginbutton.move(200, 150)
        loginbutton.setStyleSheet("background-color :#FCF6F5FF")
        loginbutton.clicked.connect(self.adminlogin)

        self.accountlable = QLabel(self.createaccdialog)
        self.accountlable.setText("first log in to admins account to create a new one")
        self.accountlable.setMinimumWidth(300)
        self.accountlable.setMaximumHeight(40)
        self.accountlable.move(100, 200)

        self.usernamebox = QLineEdit(self.createaccdialog)
        self.usernamebox.setMaximumHeight(40)
        self.usernamebox.setText("Welcome, enter your username here")
        self.usernamebox.setMinimumWidth(300)
        self.usernamebox.move(100, 300)
        self.usernamebox.setStyleSheet("background-color :#FCF6F5FF")

        self.passwordbox = QLineEdit(self.createaccdialog)
        self.passwordbox.setMaximumHeight(40)
        self.passwordbox.setText("enter your password here")
        self.passwordbox.setMinimumWidth(300)
        self.passwordbox.move(100, 350)
        self.passwordbox.setStyleSheet("background-color :#FCF6F5FF")

        createAccountButton = QPushButton("create new account", self.createaccdialog)
        createAccountButton.setMaximumHeight(40)
        createAccountButton.setMinimumWidth(200)
        createAccountButton.move(150, 400)
        createAccountButton.setStyleSheet("background-color :#FCF6F5FF")
        createAccountButton.clicked.connect(self.createacc)

        self.debugLable = QLabel(self.createaccdialog)
        self.debugLable.setMinimumHeight(50)
        self.debugLable.setMinimumWidth(400)
        self.debugLable.move(50, 450)

        self.createaccdialog.exec_()
        self.hide()

    def adminlogin(self):
        try:
            username = self.adminusernamebox.text()
            password = self.adminpasswordbox.text()
            db = connector.connect(
                host="localhost",
                user=username,
                passwd=password,

            )
            self.accountlable.setText("success! create a new acoount below")
            self.isadminloggedin = True





        except Exception as e:
            self.accountlable.setText("use correct details and try again")

    def createacc(self):
        if self.isadminloggedin:
            try:
                if self.usernamebox.text() != "Welcome, enter your username here" and self.passwordbox.text() != "enter your password here":
                    db = pymysql.connect(
                        host="127.0.0.1",
                        user="root",
                        password="dbms",
                        charset="utf8mb4",
                        cursorclass=pymysql.cursors.DictCursor
                    )
                    cursor = db.cursor()
                    username = self.usernamebox.text()
                    password = self.passwordbox.text()

                    sqlCreateUser = "CREATE USER '%s'@'localhost' IDENTIFIED BY '%s';" % (username, password)
                    cursor.execute(sqlCreateUser)
                    cursor.execute("GRANT ALL PRIVILEGES ON * . * TO '" + username + "'@'localhost'")

                    db.close()

            except Exception as e:

                self.debugLable.setText("something is wrong try again with different details")
            try:
                username = self.usernamebox.text()
                password = self.passwordbox.text()
                db = connector.connect(
                    host="localhost",
                    user=username,
                    passwd=password,

                )
                file = open("logindetail.txt", "r+")
                file.writelines([username + "\n", password])
                file.close()
                self.createaccdialog.close()
                self.window = Window()
                self.window.show()
            except Exception as e:
                self.debugLable.setText("something is wrong try again with correct username and password or"

                                        " create a new account")

        else:
            self.debugLable.setText("log in to admins account first")


if True:
    App1 = QApplication(sys.argv)
    window1 = loginWindow()
    sys.exit(App1.exec_())

# keep it halal
# for git push
