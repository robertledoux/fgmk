# -*- coding: utf-8 -*-
import json
from PyQt5 import QtCore, QtWidgets, QtGui
from fgmk import action_dialog, getdata

class actionItem(QtWidgets.QListWidgetItem):
    def __init__(self, actionAndParameter):
        #super().__init__(str(actionAndParameter))
        QtWidgets.QListWidgetItem.__init__(self, '')
        self.setText('["'+actionAndParameter[0]+'","'+actionAndParameter[1]+'"]')
        self.setData(QtCore.Qt.UserRole, actionAndParameter)
        self.setIcon(QtGui.QIcon(getdata.path('actions/'+actionAndParameter[0]+'.png')))

    def getAction(self):
        actionAndParameterReturn = self.data(QtCore.Qt.UserRole)
        action = str(actionAndParameterReturn[0])
        parameter = str(actionAndParameterReturn[1])
        return [action, parameter]

class DragAndDropList(QtWidgets.QListWidget):
    itemMoved = QtCore.pyqtSignal(int, int) # Oldindex, newindex

    def __init__(self, parent=None, **args):
        QtWidgets.QListWidget.__init__(self, parent, **args)

        self.setAcceptDrops(True)
        self.setDragEnabled(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
        self.drag_item = None
        self.drag_row = None

    def dropEvent(self, event):
        QtWidgets.QListWidget.dropEvent(self, event)
        self.itemMoved.emit(self.drag_row, self.row(self.drag_item))
        self.drag_item = None

    def startDrag(self, supportedActions):
        self.drag_item = self.currentItem()
        self.drag_row = self.row(self.drag_item)
        QtWidgets.QListWidget.startDrag(self, supportedActions)

class ActionsWidget(QtWidgets.QDialog):
    def __init__(self, psSettings, parent=None, ischaras=False, **kwargs):
        #super().__init__(parent, **kwargs)
        QtWidgets.QDialog.__init__(self, parent, **kwargs)

        self.psSettings = psSettings
        self.ischaras = ischaras

        self.mainVBox = QtWidgets.QVBoxLayout(self)
        self.mainVBox.setAlignment(QtCore.Qt.AlignTop)

        self.scrollArea = QtWidgets.QScrollArea()
        self.scrollArea.setWidgetResizable(True)
        self.mainVBox.addWidget(self.scrollArea)

        self.insideScrollArea = QtWidgets.QWidget(self.scrollArea)
        self.scrollArea.setWidget(self.insideScrollArea)

        self.VBox = QtWidgets.QVBoxLayout(self.insideScrollArea)
        self.VBox.setAlignment(QtCore.Qt.AlignTop)
        self.insideScrollArea.setLayout(self.VBox)

        filepath = getdata.path('actionsList.json')
        f = open(filepath, "r")
        e = json.load(f)
        f.close()

        self.parent = parent
        self.actionButton = []

        for action in e["actionOrder"]:
            icon = QtGui.QIcon(getdata.path('actions/'+action+'.png'))
            self.actionButton.append(QtWidgets.QPushButton(icon, action, self))
            self.actionButton[-1].setMaximumWidth(330)
            self.actionButton[-1].setMinimumWidth(80)
            self.actionButton[-1].setMinimumHeight(24)
            self.VBox.addWidget(self.actionButton[-1])
            self.actionButton[-1].clicked.connect(self.getAction)

        self.setGeometry(300, 40, 350, 650)
        self.setLayout(self.mainVBox)
        self.setWindowTitle('Select Action to add...')

        self.show()

    def getAction(self):

        buttonThatSent = self.sender()
        self.returnValue = buttonThatSent.text()

        if(self.returnValue == "END" or self.returnValue == "ELSE"):
            self.returnValue = [str(self.returnValue), ""]
            self.accept()
        else:
            newDialogFromName = getattr(action_dialog, str(self.returnValue))
            if(self.ischaras is False):
                self.myActionsDialog = newDialogFromName(
                    gamefolder=self.psSettings["gamefolder"],
                    parent=self)
            else:
                self.myActionsDialog = newDialogFromName(
                    gamefolder=self.psSettings["gamefolder"],
                    parent=self,
                    nothis=True)

            if self.myActionsDialog.exec_() == QtWidgets.QDialog.Accepted:
                returnActDlg = str(self.myActionsDialog.getValue())

                self.returnValue = [str(self.returnValue), str(returnActDlg)]
                self.accept()

    def getValue(self):
        return self.returnValue


class tinyActionsWdgt(QtWidgets.QWidget):
    somethingChanged = QtCore.pyqtSignal(object,object,'QString','QString')
    # the dragDrop option is temporary until I can connect itemMoved for everyone
    def __init__(self, parent=None, ssettings={}, nothis=True, ischara=False, isitem=False, dragDrop=False, **kwargs):
        #super().__init__(parent, **kwargs)
        QtWidgets.QWidget.__init__(self, parent, **kwargs)

        self.ssettings = ssettings
        self.parent = parent
        self.ischara = ischara
        self.isitem = isitem
        self.nothis = nothis

        self.HBox = QtWidgets.QHBoxLayout(self)
        self.HBox.setAlignment(QtCore.Qt.AlignTop)

        self.labelActionList = QtWidgets.QLabel("List of Actions:")
        if(dragDrop):
            self.ActionList = DragAndDropList(self)
            self.ActionList.itemMoved.connect(self.actionListItemMoved)
        else:
            self.ActionList = QtWidgets.QListWidget(self)

        VBoxActionList = QtWidgets.QVBoxLayout()
        VBoxButtons = QtWidgets.QVBoxLayout()

        self.addActionButton = QtWidgets.QPushButton("Add Action", self)
        self.editActionButton = QtWidgets.QPushButton("Edit Action", self)
        self.removeActionButton = QtWidgets.QPushButton("Remove Action", self)
        self.deselectActionButton = QtWidgets.QPushButton("Deselect Actions", self)

        if(not self.isitem):
            self.checkboxes = []
            self.checkboxes.append(QtWidgets.QCheckBox("on click", self))
            self.checkboxes.append(QtWidgets.QCheckBox("on over", self))
            self.checkboxes[0].setCheckState(QtCore.Qt.Checked)
            self.checkboxes[1].setCheckState(QtCore.Qt.Unchecked)
            self.checkboxes[0].clicked.connect(self.checkboxTypeChanged0)
            self.checkboxes[1].clicked.connect(self.checkboxTypeChanged1)

        self.addActionButton.clicked.connect(self.addAction)
        self.editActionButton.clicked.connect(self.editAction)
        self.removeActionButton.clicked.connect(self.removeAction)
        self.deselectActionButton.clicked.connect(self.deselectAction)

        self.HBox.addLayout(VBoxActionList)
        self.HBox.addLayout(VBoxButtons)

        VBoxActionList.addWidget(self.labelActionList)
        VBoxActionList.addWidget(self.ActionList)

        VBoxButtons.addWidget(self.addActionButton)
        VBoxButtons.addWidget(self.editActionButton)
        VBoxButtons.addWidget(self.removeActionButton)
        VBoxButtons.addWidget(self.deselectActionButton)

        if(not self.isitem):
            for checkbox in self.checkboxes:
                VBoxButtons.addWidget(checkbox)

        self.ActionList.itemSelectionChanged.connect(self.enableButtonsBecauseActionList)

        ActionListModel = self.ActionList.model()
        ActionListModel.layoutChanged.connect(self.updateActionFromWidget)

    def setList(self,actionToSet):
        # I am reusing this widget for when we have a list of actions and a type
        # selections (charas, events place in the map) and when we are adding
        # events to things that always have a definite trigger (items which you
        # hit use, maps when you get teleported, scripts,...)
        if(not self.isitem):
            # the actionToSet has two parts, a type (onover or click for example)
            # and also a list, which has all the actions, the most interesting part
            atype = actionToSet['type']
            for i in range(len(atype)):
                if(atype[i]):
                    self.checkboxes[i].setCheckState(QtCore.Qt.Checked)
                else:
                    self.checkboxes[i].setCheckState(QtCore.Qt.Unchecked)

            listToSet = actionToSet['list']
        else:
            # this else deals when actionToSet is just a list of actions
            listToSet = actionToSet

        #Whatever we had, delete and fill with all the new actions
        self.ActionList.clear()
        for action in listToSet:
            self.ActionList.addItem(actionItem(action))

    def clear(self):
        self.ActionList.clear()

    def setAllState(self, state):
        self.addActionButton.setEnabled(state)
        self.removeActionButton.setEnabled(state)
        self.ActionList.setEnabled(state)
        self.labelActionList.setEnabled(state)
        self.deselectActionButton.setEnabled(state)
        self.editActionButton.setEnabled(state)
        self.enableButtonsBecauseActionList()

        if(not self.isitem):
            for checkbox in self.checkboxes:
                checkbox.setEnabled(state)

    def updateActionFromWidget(self):
        i = 0
        while i < self.ActionList.count():
            item = self.ActionList.item(i)
            actionToAdd = item.getAction()
            i += 1

    def editAction(self):
        if(self.ssettings == {} ):
            return

        indexOfAction = self.ActionList.row(self.ActionList.selectedItems()[0])
        selecteditem = self.ActionList.selectedItems()[0]
        actionParamToEdit = selecteditem.getAction()

        actionToEdit = actionParamToEdit[0]
        paramOfEdit = actionParamToEdit[1]

        paramArrayOfEdit = paramOfEdit.split(';')

        newDialogFromName = getattr(action_dialog, str(actionToEdit))

        self.myActionsDialog = newDialogFromName(
            gamefolder=self.ssettings["gamefolder"],
            parent=self,
            edit=paramArrayOfEdit,
            nothis=self.nothis)

        if self.myActionsDialog.exec_() == QtWidgets.QDialog.Accepted:
            returnActDlg = str(self.myActionsDialog.getValue())

            actionToAdd = [actionToEdit,str(returnActDlg)]

            previous_actions = self.getValue()

            #Where action is actually edited
            self.ActionList.takeItem(indexOfAction)
            self.ActionList.insertItem(indexOfAction,actionItem(actionToAdd))

            current_actions = self.getValue()
            self.somethingChanged.emit(previous_actions,current_actions,'edit','edit action')

    def deselectAction(self):
        for i in range(self.ActionList.count()):
            item = self.ActionList.item(i)
            self.ActionList.setItemSelected(item, False)

    def actionListItemMoved(self, old_i, new_i):
        previous_actions = self.getValue()
        moved_item = previous_actions['list'][new_i]
        previous_actions['list'].pop(new_i)
        previous_actions['list'].insert(old_i, moved_item)
        current_actions = self.getValue()
        self.somethingChanged.emit(previous_actions,current_actions,'actionmoved','moved action')

    def addAction(self):
        if(self.ssettings == {} ):
            return

        self.myActionsWidget = ActionsWidget(self.ssettings,self,self.ischara)
        if self.myActionsWidget.exec_() == QtWidgets.QDialog.Accepted:
            actionToAdd = self.myActionsWidget.getValue()

            previous_actions = self.getValue()

            if not self.ActionList.selectedItems():
                self.ActionList.addItem(actionItem(actionToAdd))
            else:
                indexOfAction = self.ActionList.row(self.ActionList.selectedItems()[0])
                self.ActionList.insertItem(indexOfAction,actionItem(actionToAdd))

            current_actions = self.getValue()
            self.somethingChanged.emit(previous_actions,current_actions,'add','add action')

    def removeAction(self):
        if(self.ssettings == {} ):
            return

        if(len(self.ActionList.selectedItems())<1):
            return

        previous_actions = self.getValue()

        for item in self.ActionList.selectedItems():
            itemIndex = self.ActionList.row(item)
            self.ActionList.takeItem(itemIndex)

        current_actions = self.getValue()
        self.somethingChanged.emit(previous_actions,current_actions,'remove','remove action')

    def enableButtonsBecauseActionList(self):
        enable = True
        if (self.ActionList.currentItem() is None):
            enable = False
        else:
            if (self.ActionList.currentItem().isSelected() == False):
                enable = False

        if (enable):
            self.removeActionButton.setEnabled(True)
            self.deselectActionButton.setEnabled(True)
            self.editActionButton.setEnabled(True)
        else:
            self.removeActionButton.setEnabled(False)
            self.editActionButton.setEnabled(False)
            self.deselectActionButton.setEnabled(False)

    def checkboxTypeChanged0(self, int):
        previous_actions = self.getValue()
        previous_actions['type'][0] = not previous_actions['type'][0]
        current_actions = self.getValue()
        self.somethingChanged.emit(previous_actions,current_actions,'typeChanged','changed on click')

    def checkboxTypeChanged1(self, int):
        previous_actions = self.getValue()
        previous_actions['type'][1] = not previous_actions['type'][1]
        current_actions = self.getValue()
        self.somethingChanged.emit(previous_actions,current_actions,'typeChanged','changed on over')

    def getValue(self):
        allactions = []
        for itemIndex in range(self.ActionList.count()):
            allactions.append(self.ActionList.item(itemIndex).getAction())

        if(not self.isitem):
            onclick = self.checkboxes[0].isChecked()
            onover = self.checkboxes[1].isChecked()
            actiontype = [onclick,onover]
            returnvalue = {'list':allactions, 'type':actiontype }

        else:
            returnvalue = allactions

        return returnvalue
