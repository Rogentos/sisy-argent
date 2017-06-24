#!/usr/bin/python3
import sys, subprocess
from PyQt5 import QtCore, QtGui, QtWidgets, uic

from accesories import Accesories
from development import Development
from games import Games
from graphics import Graphics
from internet import Internet
from multimedia import Multimedia
from office import Office
from system import System
from local import Local
from everything import Everything

class Sisyphus(QtWidgets.QMainWindow):
    def __init__(self):
        super(Sisyphus, self).__init__()
        uic.loadUi('ui/sisyphus-gui.ui', self)
        self.centerOnScreen()
        self.show()

        self.package_search.clicked.connect(self.search_package)
        self.package_install.clicked.connect(self.install_package)
        self.package_uninstall.clicked.connect(self.uninstall_package)
        self.system_upgrade.clicked.connect(self.upgrade_system)
        self.orphans_remove.clicked.connect(self.remove_orphans)

        self.category_accesories.clicked.connect(self.accesories_category)
        self.category_development.clicked.connect(self.development_category)
        self.category_games.clicked.connect(self.games_category)
        self.category_graphics.clicked.connect(self.graphics_category)
        self.category_internet.clicked.connect(self.internet_category)
        self.category_multimedia.clicked.connect(self.multimedia_category)
        self.category_office.clicked.connect(self.office_category)
        self.category_system.clicked.connect(self.system_category)
        self.category_local.clicked.connect(self.local_category)
        self.category_everything.clicked.connect(self.everything_category)

    def centerOnScreen (self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

    def search_package(self):
        pkgname = self.input.text()
        subprocess.Popen(['xterm', '-hold', '-e', 'sisyphus', 'search'] + pkgname.split())

    def install_package(self):
        pkgname = self.input.text()
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-install'] + pkgname.split())

    def uninstall_package(self):
        pkgname = self.input.text()
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-uninstall'] + pkgname.split())

    def upgrade_system(self):
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'autoupgrade'])

    def remove_orphans(self):
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'remove-orphans'])

    def accesories_category(self):
        self.window = Accesories()
        self.window.show()

    def development_category(self):
        self.window = Development()
        self.window.show()

    def games_category(self):
        self.window = Games()
        self.window.show()

    def graphics_category(self):
        self.window = Graphics()
        self.window.show()

    def internet_category(self):
        self.window = Internet()
        self.window.show()

    def multimedia_category(self):
        self.window = Multimedia()
        self.window.show()

    def office_category(self):
        self.window = Office()
        self.window.show()

    def system_category(self):
        self.window = System()
        self.window.show()

    def local_category(self):
        self.window = Local()
        self.window.show()

    def everything_category(self):
        self.window = Everything()
        self.window.show()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Sisyphus()
    sys.exit(app.exec_())
