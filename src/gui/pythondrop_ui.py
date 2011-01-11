#!/usr/bin/env python

# Copyright (C) 2010 Sebastian Ruml <sebastian.ruml@gmail.com>
#
# This file is part of the PythonDrop project
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 1, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.


# This is only needed for Python v2 but is harmless for Python v3.
import sip
sip.setapi('QVariant', 2)

from PyQt4 import QtCore, QtGui

import os
import subprocess
import socket

import yaml

CONFIG_FILE = "config.yml"


class PythonDropGui(QtGui.QDialog):
    def __init__(self, configFile=CONFIG_FILE):
        super(PythonDropGui, self).__init__()
        
        self._respath = os.path.join(os.path.dirname(os.path.realpath(__file__)), "res")
        
        # Load settings
        stream = file(configFile, 'r')
        self._config = yaml.load(stream)
        
        self.createLocalSettingsGroupBox()
        self.createRemoteSettingsGroupBox()
        self.createButtons()
        
        self.createActions()
        self.createTrayIcon()
        
        mainLayout = QtGui.QVBoxLayout()
        mainLayout.addWidget(self.localSettingsGroupBox)
        mainLayout.addWidget(self.remoteSettingsGroupBox)
        mainLayout.addStretch(1)
        mainLayout.addSpacing(12)
        mainLayout.addLayout(self.buttonsLayout)
        self.setLayout(mainLayout)
        
        # TODO: Apply all settings
        self.loadSettings()
        
        self.trayIcon.show()
        
        self.setWindowTitle("PythonDrop Preferences")
        self.resize(500, 300)
        self.hide()

    def createButtons(self):
        self.okButton = QtGui.QPushButton("&Ok")
        self.cancelButton = QtGui.QPushButton("&Cancel")
        
        self.okButton.clicked.connect(self.okClicked)
        self.cancelButton.clicked.connect(self.cancelClicked)
        
        self.buttonsLayout = QtGui.QHBoxLayout()
        self.buttonsLayout.addStretch(1)
        self.buttonsLayout.addWidget(self.okButton)
        self.buttonsLayout.addWidget(self.cancelButton)
    
    def createLocalSettingsGroupBox(self):
        self.localSettingsGroupBox = QtGui.QGroupBox("Local Settings")
        
        locationLabel = QtGui.QLabel("PythonDrop Location")
        
        self.locationLineEdit = QtGui.QLineEdit()
        self.changeLocationButton = QtGui.QPushButton("Change...")
        self.changeLocationButton.clicked.connect(self.changeReposPathClicked)
        
        updateIntervalLabel = QtGui.QLabel("Update Interval")
        self.updateIntervalSpinBox = QtGui.QSpinBox()
        labelUnit = QtGui.QLabel("s")
        
        updateIntervalLayout = QtGui.QHBoxLayout()
        updateIntervalLayout.addWidget(updateIntervalLabel)
        updateIntervalLayout.addWidget(self.updateIntervalSpinBox)
        updateIntervalLayout.addWidget(labelUnit)
        
        locationLayout = QtGui.QHBoxLayout()
        locationLayout.addSpacing(20)
        locationLayout.addWidget(self.locationLineEdit)
        locationLayout.addWidget(self.changeLocationButton)
        
        layout = QtGui.QVBoxLayout()
        layout.addWidget(locationLabel)
        layout.addLayout(locationLayout)
        layout.addSpacing(5)
        layout.addLayout(updateIntervalLayout)
        self.localSettingsGroupBox.setLayout(layout)
    
    def createRemoteSettingsGroupBox(self):
        self.remoteSettingsGroupBox = QtGui.QGroupBox("Remote Settings")
        
        formLayout = QtGui.QFormLayout()
        formLayout.setSpacing(10)
        
        self.remoteHostLineEdit = QtGui.QLineEdit()
        formLayout.addRow("Remote Host", self.remoteHostLineEdit)
        
        self.remoteUserLineEdit = QtGui.QLineEdit()
        formLayout.addRow("Remote User", self.remoteUserLineEdit)
        
        self.remoteReposPathLineEdit = QtGui.QLineEdit()
        formLayout.addRow("Remote Repository Path", self.remoteReposPathLineEdit)
        
        self.remoteSettingsGroupBox.setLayout(formLayout)
    
    def createActions(self):
        self.minimizeAction = QtGui.QAction("Mi&nimize", self,
                triggered=self.hide)

        self.maximizeAction = QtGui.QAction("Ma&ximize", self,
                triggered=self.showMaximized)

        self.restoreAction = QtGui.QAction("&Restore", self,
                triggered=self.showNormal)
        
        self.openPythonDropFolderAction = QtGui.QAction("&Open PythonDrop Folder...", self,
                                                  triggered=self.openPythonDropFolder)
        
        self.showPreferencesDialogAction = QtGui.QAction("&Preferences...", self,
                                                         triggered=self.showPreferencesDialog)
        
        self.pauseResumeDaemonAction = QtGui.QAction("Pause syncing", self,
                                              triggered=self.pauseResumeDaemon)
        
        self.startDaemonAction = QtGui.QAction("Start syncing", self,
                                               triggered=self.startDaemon)
        
        self.aboutAction = QtGui.QAction("&About", self,
                triggered=self.showAbout)

        self.quitAction = QtGui.QAction("&Exit", self,
                triggered=QtGui.qApp.quit)
        
    def createTrayIcon(self):
        self.trayIconMenu = QtGui.QMenu(self)
        self.trayIconMenu.addAction(self.openPythonDropFolderAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.pauseResumeDaemonAction)
        #self.trayIconMenu.addAction(self.startDaemonAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.showPreferencesDialogAction)
        self.trayIconMenu.addAction(self.aboutAction)
        self.trayIconMenu.addSeparator()
        self.trayIconMenu.addAction(self.quitAction)
        
        self.trayIcon = QtGui.QSystemTrayIcon(self)
        self.trayIcon.setIcon(QtGui.QIcon(os.path.join(self._respath, "refresh.ico")))    
        self.trayIcon.setContextMenu(self.trayIconMenu)
        
    def startDaemon(self):
        pass
    
    def pauseResumeDaemon(self):
        self.sendApiCommand("stop")
    
    def openPythonDropFolder(self):
        subprocess.Popen("explorer " + self._config["pythondrop_folder"])
        
    def showPreferencesDialog(self):
        self.showNormal()
    
    def cancelClicked(self):
        self.hide()
    
    def okClicked(self):
        self.applySettings()
        self.hide()
        
    def changeReposPathClicked(self):
        oldDir = self._config["pythondrop_folder"]
        dir = QtGui.QFileDialog.getExistingDirectory(self,
                                                     "Select Folder for Repository",
                                                     oldDir, QtGui.QFileDialog.ShowDirsOnly) 
        if dir:
            self.locationLineEdit.setText(dir)
    
    def loadSettings(self):
        self.locationLineEdit.setText(self._config["pythondrop_folder"])
        self.updateIntervalSpinBox.setValue(int(self._config["sync_interval"]))
        self.remoteHostLineEdit.setText(self._config["remote_host"])
        self.remoteUserLineEdit.setText(self._config["remote_user"])
        self.remoteReposPathLineEdit.setText(self._config["remote_repository_path"])
    
    def applySettings(self):
        if int(self._config["sync_interval"]) != self.updateIntervalSpinBox.value():
            self.sendApiCommand("update_interval", str(self.updateIntervalSpinBox.value()))
    
    def showAbout(self):
        msgBox = QtGui.QMessageBox()
        msgBox.setText("Just a little test on christmas ;)")
        msgBox.exec_()
        
    def sendApiCommand(self, command, data=None):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        sock.connect(("127.0.0.1", self._config["tcp_listen_port"]))
        
        if data == None:
            dataToSend = command + "\n"
        else:
            dataToSend = command + " " + data + "\n"
        
        sock.send(dataToSend)
        sock.close()
        


if __name__ == '__main__':
    try:
        import sys
        
        confFile = CONFIG_FILE
        if len(sys.argv) > 1:
            confFile = sys.argv[1]
        
        app = QtGui.QApplication(sys.argv)
        
        if not QtGui.QSystemTrayIcon.isSystemTrayAvailable():
            QtGui.QMessageBox.critical(None, "Systray",
                "I couldn't detect any system tray on this system.")
            sys.exit(1)

        QtGui.QApplication.setQuitOnLastWindowClosed(False)
        
        window = PythonDropGui(confFile)
        #window.show()
        sys.exit(app.exec_())
    except SystemExit:
        raise
    except: # BaseException doesn't exist in python2.4
        import traceback
        traceback.print_exc()
