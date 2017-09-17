#!/usr/bin/python3
import sys, subprocess, sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import *

class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus-gui.ui', self)
        self.updateSystem()
        self.centerOnScreen()
        self.show()
        self.progress.hide()
        self.loadDatabase()

        self.input.returnPressed.connect(self.filterDatabase)

        self.installThread = InstallThread()
        self.install.clicked.connect(self.packageInstall)
        self.installThread.installFinished.connect(self.finishedInstall)

        self.uninstallThread = UninstallThread()
        self.uninstall.clicked.connect(self.packageUninstall)
        self.uninstallThread.uninstallFinished.connect(self.finishedUninstall)

        self.upgradeThread = UpgradeThread()
        self.upgrade.clicked.connect(self.systemUpgrade)
        self.upgradeThread.upgradeFinished.connect(self.finishedUpgrade)

        self.orphansThread = OrphansThread()
        self.orphans.clicked.connect(self.orphansRemove)
        self.orphansThread.orphansFinished.connect(self.finishedOrphans)

        self.abort.clicked.connect(self.sisyphusExit)

    def updateSystem(self):
        sisyphus_pkg_system_update()

    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

    def loadDatabase(self):
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
                        ''')
            rows = cursor.fetchall()

            for row in rows:
                inx = rows.index(row)
                self.database.insertRow(inx)
                self.database.setItem(inx, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.database.setItem(inx, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.database.setItem(inx, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.database.setItem(inx, 3, QtWidgets.QTableWidgetItem(row[3]))
                self.database.setItem(inx, 4, QtWidgets.QTableWidgetItem(row[4]))

    def filterDatabase(self):
        items = self.database.findItems(self.input.text(), QtCore.Qt.MatchExactly)
        if items:
            for item in items:
                results = ''.join('%d' % (item.row() + 0)).split()
                coordinates = map(int, results)
                for coordinate in coordinates:
                    self.database.setCurrentCell(coordinate, 0)
        else:
            self.input.setText("There are no packages with that name...")
    
    def packageInstall(self):
        self.showProgressBar()
        Sisyphus.PKGLIST = self.database.item(self.database.currentRow(), 1).text()
        self.installThread.start()

    def finishedInstall(self):
        self.hideProgressBar()

    def packageUninstall(self):
        self.showProgressBar()
        Sisyphus.PKGLIST = self.database.item(self.database.currentRow(), 1).text()
        self.uninstallThread.start()

    def finishedUninstall(self):
        self.hideProgressBar()

    def systemUpgrade(self):
        self.showProgressBar()
        self.upgradeThread.start()

    def finishedUpgrade(self):
        self.hideProgressBar()

    def orphansRemove(self):
        self.showProgressBar()
        self.orphansThread.start()

    def finishedOrphans(self):
        self.hideProgressBar()

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

class InstallThread(QtCore.QThread):
    installFinished = QtCore.pyqtSignal()
    def run(self):
        PKGLIST = Sisyphus.PKGLIST
        sisyphus_pkg_auto_install(PKGLIST.split())
        self.installFinished.emit()

class UninstallThread(QtCore.QThread):
    uninstallFinished = QtCore.pyqtSignal()
    def run(self):
        PKGLIST = Sisyphus.PKGLIST
        sisyphus_pkg_auto_uninstall(PKGLIST.split())
        self.uninstallFinished.emit()

class UpgradeThread(QtCore.QThread):
    upgradeFinished = QtCore.pyqtSignal()
    def run(self):
        sisyphus_pkg_auto_system_upgrade()
        self.upgradeFinished.emit()

class OrphansThread(QtCore.QThread):
    orphansFinished = QtCore.pyqtSignal()
    def run(self):
        sisyphus_pkg_auto_remove_orphans()
        self.orphansFinished.emit()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Sisyphus()
    sys.exit(app.exec_())
