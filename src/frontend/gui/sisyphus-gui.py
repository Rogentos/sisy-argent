#!/usr/bin/python3
import sys, subprocess, sqlite3
from collections import OrderedDict
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import *

class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus-gui.ui', self)
        self.centerOnScreen()
        self.show()
        
        self.SEARCHFIELDS = OrderedDict ([
            ('Category', 'cat'),
            ('Name', 'pn'),
            ('Description', 'descr')
            ])
        self.selectfield.addItems(self.SEARCHFIELDS.keys())
        self.selectfield.setCurrentIndex(1)
        self.selectfield.currentIndexChanged.connect(self.setSearchField)
        
        self.SEARCHFILTERS = OrderedDict ([
            ('All', ''),
            ('Available', 'AND iv IS NULL'),
            ('Installed', 'AND iv IS NOT NULL'),
            ('Upgradable', 'AND iv < av'),
            ('Downgradable', 'AND iv > av')
            ])
        self.selectfilter.addItems(self.SEARCHFILTERS.keys())
        self.selectfilter.setCurrentIndex(0)
        self.selectfilter.currentIndexChanged.connect(self.setSearchFilter)
                
        Sisyphus.SEARCHTERM = "'%%'"
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS['Name']
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS['All']

        self.input.textEdited.connect(self.filterDatabase)

        self.updateThread = UpdateThread()
        self.updateThread.started.connect(self.showProgressBar)
        self.updateThread.finished.connect(self.finishedUpdate)

        self.installThread = InstallThread()
        self.install.clicked.connect(self.packageInstall)
        self.installThread.finished.connect(self.finishedInstall)

        self.uninstallThread = UninstallThread()
        self.uninstall.clicked.connect(self.packageUninstall)
        self.uninstallThread.finished.connect(self.finishedUninstall)

        self.upgradeThread = UpgradeThread()
        self.upgrade.clicked.connect(self.systemUpgrade)
        self.upgradeThread.finished.connect(self.finishedUpgrade)

        self.orphansThread = OrphansThread()
        self.orphans.clicked.connect(self.orphansRemove)
        self.orphansThread.finished.connect(self.finishedOrphans)

        self.updateSystem()
        self.progress.hide()

        self.abort.clicked.connect(self.sisyphusExit)
        
    def setSearchField(self):
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS[self.selectfield.currentText()]
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)
        
    def setSearchFilter(self):
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS[self.selectfilter.currentText()]
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)
        
    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

    def loadDatabase(self,searchField,searchTerm,searchFilter):
        with sqlite3.connect('/var/lib/sisyphus/db/sisyphus.db') as db:
            cursor=db.cursor()
            cursor.execute('''SELECT
                            a.category AS cat,
                            a.name AS pn,
                            a.version AS av,
                            i.version AS iv,
                            a.description AS descr
                            FROM remote_packages AS a
                            LEFT JOIN local_packages AS i
                            ON a.category = i.category
                            AND a.name = i.name
                            AND a.slot = i.slot
                            WHERE %s LIKE %s %s
                        ''' % (searchField, searchTerm, searchFilter))
            rows = cursor.fetchall()
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(['Category', 'Name', 'Available Version', 'Installed Version', 'Description'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 5):
                    item = QtGui.QStandardItem("%s"%(row[column]))
                    model.setItem(indx, column, item)
            self.database.setModel(model)

    def filterDatabase(self):
        search = self.input.text()
        Sisyphus.SEARCHTERM = "'%" + search + "%'"
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)

    def updateSystem(self):
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)
        self.updateThread.start()

    def finishedUpdate(self):
        self.hideProgressBar()
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)

    def packageInstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.input.setText("Please select at least one package!!!")
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.showProgressBar()
            self.installThread.start()

    def finishedInstall(self):
        self.hideProgressBar()
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)

    def packageUninstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.input.setText("Please select at least one package!!!")
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.showProgressBar()
            self.uninstallThread.start()

    def finishedUninstall(self):
        self.hideProgressBar()
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)

    def systemUpgrade(self):
        self.showProgressBar()
        self.upgradeThread.start()

    def finishedUpgrade(self):
        self.hideProgressBar()
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)

    def orphansRemove(self):
        self.showProgressBar()
        self.orphansThread.start()

    def finishedOrphans(self):
        self.hideProgressBar()
        self.loadDatabase(Sisyphus.SEARCHFIELD,Sisyphus.SEARCHTERM,Sisyphus.SEARCHFILTER)

    def showProgressBar(self):
        self.hideButtons()
        self.progress.setRange(0,0)
        self.progress.show()

    def hideProgressBar(self):
        self.progress.setRange(0,1)
        self.progress.setValue(1)
        self.progress.hide()
        self.showButtons()

    def hideButtons(self):
        self.install.hide()
        self.uninstall.hide()
        self.orphans.hide()
        self.upgrade.hide()
        self.abort.hide()

    def showButtons(self):
        self.install.show()
        self.uninstall.show()
        self.orphans.show()
        self.upgrade.show()
        self.abort.show()

    def sisyphusExit(self):
        self.close()

class UpdateThread(QtCore.QThread):
    def run(self):
        sisyphus_pkg_system_update()

class InstallThread(QtCore.QThread):
    def run(self):
        PKGLIST = Sisyphus.PKGLIST
        sisyphus_pkg_auto_install(PKGLIST)

class UninstallThread(QtCore.QThread):
    def run(self):
        PKGLIST = Sisyphus.PKGLIST
        sisyphus_pkg_auto_uninstall(PKGLIST)

class UpgradeThread(QtCore.QThread):
    def run(self):
        sisyphus_pkg_auto_system_upgrade()

class OrphansThread(QtCore.QThread):
    def run(self):
        sisyphus_pkg_auto_remove_orphans()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Sisyphus()
    sys.exit(app.exec_())
