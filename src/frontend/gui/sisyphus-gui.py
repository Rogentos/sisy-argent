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
            ('Search by name', 'pn'),
            ('Search by category', 'cat'),
            ('Search by description', 'descr')
            ])
        self.selectfield.addItems(self.SEARCHFIELDS.keys())
        self.selectfield.setCurrentText('Search by name')
        Sisyphus.SEARCHFIELD = self.SEARCHFIELDS['Search by name']
        self.selectfield.currentIndexChanged.connect(self.setSearchField)
        
        self.SEARCHFILTERS = OrderedDict ([
            ('All packages', 'all'),
            ('Installed packages', 'instaled'),
            ('Installable packages', 'installable'),
            ('Safe removable packages', 'removable'),
            ('Upgradable/Rebuilt packages', 'upgradable')
            ])
        Sisyphus.SEARCHFILTER = self.SEARCHFILTERS['All packages']        
        self.selectfilter.addItems(self.SEARCHFILTERS.keys())
        self.selectfilter.setCurrentText('All packages')
        self.selectfilter.currentIndexChanged.connect(self.setSearchFilter)
        
        Sisyphus.SEARCHTERM = "'%%'"

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
        Sisyphus.SELECT = self.selectfilter.currentText()
        self.loadDatabase()

    def loadDatabase(self):
        self.SELECTS = OrderedDict ([
            ('all','''SELECT
                i.category AS cat,
                i.name as pn,
                IFNULL(a.version, 'None') AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i LEFT OUTER JOIN remote_packages as a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                WHERE %s LIKE %s
                UNION
                SELECT
                a.category AS cat,
                a.name as pn,
                a.version AS av,
                IFNULL(i.version, 'None') AS iv,
                a.description AS descr
                FROM remote_packages AS a LEFT OUTER JOIN local_packages AS i
                ON a.category = i.category
                AND a.name = i.name
                AND a.slot = i.slot
                WHERE %s LIKE %s
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM, Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM)),
            ('instaled','''SELECT
                i.category AS cat,
                i.name AS pn,
                a.version AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                WHERE %s LIKE %s
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM)),
            ('installable','''SELECT
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
                WHERE %s LIKE %s
                AND iv IS NULL
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM)),
            ('removable','''SELECT
                i.category AS cat,
                i.name AS pn,
                a.version AS av,
                i.version AS iv,
                i.description AS descr,
                CASE WHEN rm.name ISNULL THEN 'no' ELSE 'yes' END AS rmv
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                LEFT JOIN removable_packages as rm
                ON i.category = rm.category
                AND i.name = rm.name
                AND i.slot = rm.slot
                WHERE %s LIKE %s
                AND rmv = "yes"
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM)),
            ('upgradable','''SELECT
                i.category AS cat,
                i.name AS pn,
                a.version AS av,
                i.version AS iv,
                i.description AS descr
                FROM local_packages AS i
                LEFT JOIN remote_packages AS a
                ON i.category = a.category
                AND i.name = a.name
                AND i.slot = a.slot
                WHERE %s LIKE %s
                AND a.timestamp > i.timestamp
            ''' % (Sisyphus.SEARCHFIELD, Sisyphus.SEARCHTERM)),
            ])
        with sqlite3.connect(sisyphus_database_path) as db:
            cursor=db.cursor()
            FILTEROUT = "AND cat NOT LIKE 'virtual'"
            cursor.execute('%s %s' % (self.SELECTS[Sisyphus.SEARCHFILTER], FILTEROUT))
            rows = cursor.fetchall()
            Sisyphus.PKGCOUNT = len(rows)
            Sisyphus.PKGSELECTED = 0
            model = QtGui.QStandardItemModel(len(rows), 5)
            model.setHorizontalHeaderLabels(['Category', 'Name', 'Available Version', 'Installed Version', 'Description'])
            for row in rows:
                indx = rows.index(row)
                for column in range(0, 5):
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
        self.statusBar().showMessage("I am syncing myself, hope to finish soon ...")
        self.updateThread.start()

    def packageInstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.statusBar().showMessage("I am installing %d package(s) for you ..." %len(Sisyphus.PKGLIST))
            self.installThread.start()

    def packageUninstall(self):
        indexes = self.database.selectionModel().selectedRows(1)
        if len(indexes) == 0:
            self.statusBar().showMessage("No package selected, please pick at least one!")
        else:
            Sisyphus.PKGLIST = []
            for index in sorted(indexes):
                Sisyphus.PKGLIST.append(index.data())
            self.statusBar().showMessage("I am removing %d package(s) as requested ..." %len(Sisyphus.PKGLIST))
            self.uninstallThread.start()

    def systemUpgrade(self):
        self.statusBar().showMessage("I am upgrading the system, please be patient ...")
        self.upgradeThread.start()

    def orphansRemove(self):
        self.statusBar().showMessage("I am busy with some cleaning, please don't rush me ...")
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
