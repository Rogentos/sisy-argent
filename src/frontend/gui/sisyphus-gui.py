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
        
# set globals

        self.SEARCHFIELDS = OrderedDict ([
            ('Category', 'cat'),
            ('Name', 'pn'),
            ('Description', 'descr')
            ])
        self.selectfield.addItems(self.SEARCHFIELDS.keys())
        self.selectfield.setCurrentIndex(1)
        self.selectfield.currentIndexChanged.connect(self.setSearchField)
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS['Name']
             
        self.SEARCHFILTERS = OrderedDict ([
            ('All', ''),
            ('Available', 'AND iv IS NULL'),
            ('Installed', 'AND iv IS NOT NULL'),
            ('Upgradable', 'AND iv <> av'),
            ('Removable', 'AND rmv = "yes"')
            ])
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS['All']
        
        Sisyphus.SEARCHTERM = "'%%'"

# connect signals

        self.selectfilter.addItems(self.SEARCHFILTERS.keys())
        self.selectfilter.setCurrentIndex(0)
        self.selectfilter.currentIndexChanged.connect(self.setSearchFilter)
        
        self.database.clicked.connect(self.rowClicked)
        
        self.input.textEdited.connect(self.filterDatabase)

        self.updateThread = UpdateThread()
        self.updateThread.started.connect(self.showProgressBar)
        self.updateThread.finished.connect(self.jobDone)

        self.installThread = InstallThread()
        self.install.clicked.connect(self.packageInstall)
        self.installThread.started.connect(self.showProgressBar)
        self.installThread.finished.connect(self.jobDone)

        self.uninstallThread = UninstallThread()
        self.uninstall.clicked.connect(self.packageUninstall)
        self.uninstallThread.started.connect(self.showProgressBar)
        self.uninstallThread.finished.connect(self.jobDone)

        self.upgradeThread = UpgradeThread()
        self.upgrade.clicked.connect(self.systemUpgrade)
        self.upgradeThread.started.connect(self.showProgressBar)
        self.upgradeThread.finished.connect(self.jobDone)

        self.orphansThread = OrphansThread()
        self.orphans.clicked.connect(self.orphansRemove)
        self.orphansThread.started.connect(self.showProgressBar)
        self.orphansThread.finished.connect(self.jobDone)

        self.updateSystem()
        self.progress.hide()

        self.abort.clicked.connect(self.sisyphusExit)
        
        #hide removable column
        self.database.horizontalHeader().hideSection(5)
        
    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))
        
    def rowClicked(self):
        Sisyphus.PKGSELECTED = len(self.database.selectionModel().selectedRows())
        self.showPackageCount()

    def showPackageCount(self):
        self.statusBar().showMessage("Found: %d, Selected: %d packages" %(Sisyphus.PKGCOUNT, Sisyphus.PKGSELECTED))

    def setSearchField(self):
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS[self.selectfield.currentText()]
        self.loadDatabase()
        
    def setSearchFilter(self):
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS[self.selectfilter.currentText()]
        self.loadDatabase()

    def loadDatabase(self):
        with sqlite3.connect(sisyphus_database_path) as db:
            cursor=db.cursor()
            FILTEROUT = "AND cat NOT LIKE 'virtual'"
            cursor.execute('''SELECT
                            a.category AS cat,
                            a.name AS pn,
                            a.version AS av,
                            i.version AS iv,
                            a.description AS descr,
                            CASE WHEN rm.name ISNULL THEN 'no' ELSE 'yes' END AS rmv
                            FROM remote_packages AS a
                            LEFT JOIN local_packages AS i
                            ON a.category = i.category
                            AND a.name = i.name
                            AND a.slot = i.slot
                            LEFT JOIN removeable_packages as rm
                            ON i.category = rm.category
                            AND i.name = rm.name
                            AND i.slot = rm.slot
                            WHERE %s LIKE %s %s %s
                        ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, Sisyphus.SEARCHFILTER, FILTEROUT))
            rows = cursor.fetchall()
            Sisyphus.PKGCOUNT = len(rows)
            Sisyphus.PKGSELECTED = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(['Category', 'Name', 'Available Version', 'Installed Version', 'Description', 'Rmv'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 6):
                    item = QtGui.QStandardItem("%s"%(row[column]))
                    model.setItem(indx, column, item)
            self.database.setModel(model)
            self.showPackageCount()

    def filterDatabase(self):
        search = self.input.text()
        Sisyphus.SEARCHTERM = "'%" + search + "%'"
        self.loadDatabase()

    def updateSystem(self):
        self.loadDatabase()
        self.updateThread.start()

    def packageInstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!", 3000)
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.installThread.start()

    def packageUninstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!", 3000)
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.uninstallThread.start()

    def systemUpgrade(self):
        self.upgradeThread.start()

    def orphansRemove(self):
        self.orphansThread.start()

    def jobDone(self):
        self.hideProgressBar()
        self.loadDatabase()

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
