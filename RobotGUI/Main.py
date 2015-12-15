#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
ZetCode PyQt4 tutorial 

In this example, we position two push
buttons in the bottom-right corner 
of the window. 

author: Jan Bodnar
website: zetcode.com 
last edited: October 2011
"""

import sys
import cv2
import Robot
import Video
import Commands
from PyQt4 import QtGui, QtCore

########## WIDGETS ##########
class CameraWidget(QtGui.QWidget):
    def __init__(self, getFrameFunction):
        """
        :param cameraID:
        :param getFrameFunction: A function that when called will return a frame
                that can be put in a QLabel. In this case the frame will come from
                a VideoStream object's getFrame function.
        :return:
        """
        super(CameraWidget, self).__init__()

        #Set up globals
        self.getFrame = getFrameFunction
        self.fps      = 24
        self.paused   = True   #Keeps track of the video's state
        self.timer    = None

        #Initialize the UI
        self.video_frame = QtGui.QLabel("ERROR: Could not open camera.")  #Temp label for the frame
        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.video_frame)
        self.setLayout(self.vbox)

        #Get one frame and display it, and wait for play to be pressed
        self.nextFrameSlot()


    def play(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.nextFrameSlot)
        self.timer.start(1000./self.fps)

        self.paused = False

    def pause(self):
        self.timer.stop()
        self.paused = True

    def nextFrameSlot(self):

        pixFrame = self.getFrame()

        #If a frame was returned correctly
        if pixFrame is None:
            return

        self.video_frame.setPixmap(pixFrame)


########## VIEWS ##########
class ScanView(QtGui.QWidget):

    def __init__(self):
        super(ScanView, self).__init__()
        #When Apply is clicked, these settings are sent to the main app TODO: Have these settings filled out by a settings file
        self.settings  = {"robotID": None, "cameraID": None}

        #Init UI Globals
        self.cameraButtonGroup = None
        self.robotButtonGroup  = None
        self.robVBox   = QtGui.QVBoxLayout()
        self.camVBox   = QtGui.QVBoxLayout()
        self.applyBtn  = QtGui.QPushButton("Apply")  #Gets connected from the MainWindow method
        self.cancelBtn = QtGui.QPushButton("Cancel")

        self.initUI()


    def initUI(self):
        #Create Text
        selectRobotTxt  = QtGui.QLabel('Please select the robot you will be using:')
        selectCameraTxt = QtGui.QLabel('Please select the camera you will be using:')

        #CREATE BUTTONS
        robotScanBtn  = QtGui.QPushButton("Scan for Robots")
        cameraScanBtn = QtGui.QPushButton("Scan for Cameras")
            #Set max widths of buttons
        maxWidth = 100
        robotScanBtn.setMaximumWidth(maxWidth)
        cameraScanBtn.setMaximumWidth(maxWidth)
        self.applyBtn.setMaximumWidth(maxWidth)
        self.cancelBtn.setMaximumWidth(maxWidth)


        #CREATE GRID
        grid = QtGui.QGridLayout()
        grid.setSpacing(20)
            #Add Widgets
        grid.addWidget(selectRobotTxt,  0, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(robotScanBtn,    0, 1, QtCore.Qt.AlignRight)
        grid.addLayout(self.robVBox,    1, 0, QtCore.Qt.AlignTop)


        grid.addWidget(selectCameraTxt, 2, 0, QtCore.Qt.AlignLeft)
        grid.addWidget(cameraScanBtn,   2, 1, QtCore.Qt.AlignRight)
        grid.addLayout(self.camVBox,    3, 0, QtCore.Qt.AlignTop)

        grid.addWidget(self.cancelBtn,  4, 0, QtCore.Qt.AlignBottom)
        grid.addWidget(self.applyBtn,   4, 1, QtCore.Qt.AlignBottom)

        self.setLayout(grid)

        #Connect Buttons
        robotScanBtn.clicked.connect(self.scanForRobotsClicked)
        cameraScanBtn.clicked.connect(self.scanForCamerasClicked)

    def scanForRobotsClicked(self):
        connectedDevices = Robot.getConnectedRobots()
        print connectedDevices
        self.robotButtonGroup = QtGui.QButtonGroup()

        #Update the list of found devices
        self.clearLayout(self.robVBox)  #  Clear robot list
        for i, port in enumerate(connectedDevices):
            newButton = QtGui.QRadioButton(port[0])
            self.robVBox.addWidget(newButton)                        # Add the button to the button layout
            self.robotButtonGroup.addButton(newButton, i)            # Add the button to a group, with an ID of i
            newButton.clicked.connect(self.robButtonClicked) # Connect each radio button to a method


        if len(connectedDevices) == 0:
            notFoundTxt = QtGui.QLabel('No devices were found.')
            self.robVBox.addWidget(notFoundTxt)

    def scanForCamerasClicked(self):

        #  Get all of the cameras connected to the computer and list them
        connectedCameras = Video.getConnectedCameras()

        self.cameraButtonGroup = QtGui.QButtonGroup()

        #Update the list of found cameras
        self.clearLayout(self.camVBox)  #  Clear camera list
        for i in xrange(len(connectedCameras)):
            newButton = QtGui.QRadioButton("Camera " + str(i))
            self.camVBox.addWidget(newButton)                  # Add the button to the button layout
            self.cameraButtonGroup.addButton(newButton, i)     # Add the button to a group, with an ID of i
            newButton.clicked.connect(self.camButtonClicked)   # Connect each radio button to a method



        if len(connectedCameras) == 0:
            notFoundTxt = QtGui.QLabel('No cameras were found.')
            self.camVBox.addWidget(notFoundTxt)

    def camButtonClicked(self):
        self.settings["cameraID"] = self.cameraButtonGroup.checkedId()

    def robButtonClicked(self):
        self.settings["robotID"] = str(self.robotButtonGroup.checkedButton().text())

    def clearLayout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            child.widget().deleteLater()

    def getSettings(self):
        return self.settings

class DashboardView(QtGui.QWidget):
    def __init__(self, getFrameFunction):
        super(DashboardView, self).__init__()



        #UI Globals setup
        self.commandList    = Commands.CommandList()
        self.addCommandBtn  = QtGui.QPushButton("Add Command")
        self.cameraWidget   = CameraWidget(getFrameFunction)

        self.initUI()

        # for index, name, icon in [
        #     ('No.1', 'Meyoko',  'icon.png'),
        #     ('No.2', 'Nyaruko', 'icon.png'),
        #     ('No.3', 'Louise',  'icon.png')]:
        #
        #     self.commandList.addCommand(index, name)

    def initUI(self):

        #Create main layout
        mainHLayout = QtGui.QHBoxLayout()
        mainVLayout = QtGui.QVBoxLayout()
        mainVLayout.addLayout(mainHLayout)


        #Create command list (LEFT)
        listVLayout = QtGui.QVBoxLayout()
        listVLayout.addWidget(self.addCommandBtn)
        listVLayout.addWidget(self.commandList)
        mainHLayout.addLayout(listVLayout)


        #Put a space between control list and camera view
        mainHLayout.addStretch(1)


        #Create Camera view (RIGHT)
        mainHLayout.addWidget(self.cameraWidget)

        self.setLayout(mainVLayout)
        self.addCommandBtn.clicked.connect(self.addCommand)

    def addCommand(self):
        #For controlling the commandList
        #Eventually, this will open a Menu window that will offer various types of commands that can be created
        self.commandList.addCommand(Commands.MoveRSHCommand)



########## MAIN WINDOW ##########
class MainWindow(QtGui.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        #Set Global variables
        self.settings = {"robotID": None, "cameraID": 0}
        self.vStream  = Video.VideoStream(self.settings["cameraID"])
        self.robot    = Robot.Robot()

        #Set Global UI Variables
        self.centralWidget   = QtGui.QStackedWidget()
        self.dashboardView   = DashboardView(self.vStream.getPixFrame)
        self.settingsView    = ScanView()
        self.scriptToggleBtn = QtGui.QAction(QtGui.QIcon('Images/run_script.png'), 'Run/Pause the command script (Ctrl+R)',   self)
        self.videoToggleBtn  = QtGui.QAction(QtGui.QIcon('Images/play_video.png'), 'Play/Pause the video stream (Ctrl+P)',    self)
        self.settingsBtn     = QtGui.QAction(QtGui.QIcon('Images/settings.png'),   'Open Camera and Robot settings (Ctrl+T)', self)


        #self.scanView = ScanView()
        #Set up other views
        self.settingsView.applyBtn.clicked.connect(lambda: self.closeSettingsView("Apply"))
        self.settingsView.cancelBtn.clicked.connect(lambda: self.closeSettingsView("Cancel"))

        self.initUI()

        self.videoToggle()  #Play video

    def initUI(self):
        #Create toolbar
        toolbar = self.addToolBar("MainToolbar")
            #Run/Pause script button
        self.scriptToggleBtn.setShortcut('Ctrl+R')
        self.scriptToggleBtn.triggered.connect(self.scriptToggle)
        toolbar.addAction(self.scriptToggleBtn)
            #Play/Pause video button
        self.videoToggleBtn.setShortcut('Ctrl+P')
        self.videoToggleBtn.triggered.connect(self.videoToggle)
        toolbar.addAction(self.videoToggleBtn)
            #Settings button
        self.settingsBtn.setShortcut('Ctrl+S')
        self.settingsBtn.triggered.connect(lambda: self.centralWidget.setCurrentWidget(self.settingsView))
        toolbar.addAction(self.settingsBtn)

        #Create the main layout
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.addWidget(self.dashboardView)
        self.centralWidget.addWidget(self.settingsView)


        self.setWindowTitle('uArm Creator Dashboard')
        self.show()

    def videoToggle(self):
        #Play pause video stream on dashBoardView
        print "MainWindow.videoToggle(): Toggling video!"
        if self.settings["cameraID"] is None: return  #Don't change anything if no camera ID has been added yet

        if self.vStream.paused:
            self.dashboardView.cameraWidget.play()
            self.vStream.setPaused(False)
            self.videoToggleBtn.setIcon(QtGui.QIcon("Images/pause_video.png"))
        else:
            self.dashboardView.cameraWidget.pause()
            self.vStream.setPaused(True)
            self.videoToggleBtn.setIcon(QtGui.QIcon("Images/play_video.png"))
    def scriptToggle(self):
        #Run/pause the main script
        print "MainWindow.scriptToggle(): Toggling script!"
        self.robot.moveTo(height=150)

    def closeSettingsView(self, buttonClicked):
        print "MainWindow.closeSettingsView(): Closing settings from button: ", buttonClicked
        if buttonClicked == "Apply":
            #Apply settings
            newSettings = self.settingsView.getSettings()

            if newSettings["cameraID"] is not None and not newSettings["cameraID"] == self.settings["cameraID"]:
                print "Main.closeSettingsView()\t Changing cameraID from ", \
                      self.settings["cameraID"], "to", newSettings["cameraID"]
                self.settings["cameraID"] = newSettings["cameraID"]
                self.vStream.setNewCamera(self.settings["cameraID"])


            if newSettings["robotID"] is not None:
                self.settings["robotID"] = newSettings["robotID"]
                self.robot.setSerial(self.settings["robotID"])

        if buttonClicked == "Cancel":
            #Don't apply settings
            pass
        self.centralWidget.setCurrentWidget(self.dashboardView)

    def closeEvent(self, event):
        self.vStream.endThread()



if __name__ == '__main__':
    app = QtGui.QApplication(sys.argv)
    mainWindow = MainWindow()
    mainWindow.show()

    sys.exit(app.exec_())

