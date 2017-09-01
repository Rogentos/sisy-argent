#!/usr/bin/python3
import sys, subprocess, sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from libsisyphus import *

PKGLIST = self.database.item(self.database.currentRow(), 1).text()

class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus-gui.ui', self)
        self.refresh_database()
        self.centerOnScreen()
        self.show()
        self.load_packages()

        self.input.returnPressed.connect(self.filter_database)
    
        self.install.clicked.connect(self.install_package)
        self.uninstall.clicked.connect(self.uninstall_package)
        self.orphans.clicked.connect(self.remove_orphans)
        self.upgrade.clicked.connect(self.upgrade_system)
        self.abort.clicked.connect(self.exit_sisyphus)
    
    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))
    
    def install_package(self):
        sisyphus_pkg_auto_install(PKGLIST.split())

    def uninstall_package(self):
        sisyphus_pkg_auto_uninstall(PKGLIST.split())

    def remove_orphans(self):
        sisyphus_pkg_auto_remove_orphans()

    def upgrade_system(self):
        sisyphus_pkg_auto_system_upgrade()

    def refresh_database(self):
        sisyphus_pkg_system_update()

    def exit_sisyphus(self):
        self.close()

    def filter_database(self):
        items = self.database.findItems(self.input.text(), QtCore.Qt.MatchExactly)
        if items:
            for item in items:
                results = ''.join('%d' % (item.row() + 0)).split()
                coordinates = map(int, results)
                for coordinate in coordinates:
                    self.database.setCurrentCell(coordinate, 0)
        else:
            self.input.setText("There are no packages with that name...")
 
    def load_packages(self):
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

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Sisyphus()
    sys.exit(app.exec_())
