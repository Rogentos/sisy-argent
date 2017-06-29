#!/usr/bin/python3
import sys, subprocess, sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets, uic

class System(QtWidgets.QMainWindow):
    def __init__(self):
        super(System, self).__init__()
        uic.loadUi('ui/system.ui', self)
        self.centerOnScreen()
        self.show()
        self.load_packages()
    
        self.package_install.clicked.connect(self.install_package)
        self.package_uninstall.clicked.connect(self.uninstall_package)
        self.orphans_remove.clicked.connect(self.remove_orphans)
        self.category_exit.clicked.connect(self.exit_category)
    
    def centerOnScreen(self):
        resolution = QtWidgets.QDesktopWidget().screenGeometry()
        self.move((resolution.width() / 2) - (self.frameSize().width() / 2),
                    (resolution.height() / 2) - (self.frameSize().height() / 2))

    def install_package(self):
        pkgname = self.table_system.item(self.table_system.currentRow(), 1).text()
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-install'] + pkgname.split())
    
    def uninstall_package(self):
        pkgname = self.table_system.item(self.table_system.currentRow(), 1).text()
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'auto-uninstall'] + pkgname.split())

    def remove_orphans(self):
        subprocess.Popen(['xterm', '-e', 'sisyphus', 'remove-orphans'])

    def exit_category(self):
        self.close()
 
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
                            WHERE  a.name IN
                                ('hddtemp',
                                'testdisk',
                                'system-config-printer',
                                'clamav',
                                'clamtk',
                                'kcdemu',
                                'aqemu',
                                'docker',
                                'libvirt',
                                'q4wine',
                                'qemu',
                                'spice',
                                'spice-protocol',
                                'virtualbox',
                                'virtualbox-extpack-oracle',
                                'virtualbox-guest-additions',
                                'virtualbox-modules',
                                'wine',
                                'winetricks',
                                'chkrootkit',
                                'rkhunter',
                                'laptop-mode-tools',
                                'gsmartcontrol',
                                'hdparm',
                                'lm_sensors',
                                'microcode-ctl',
                                'smartmontools',
                                'usb_modeswitch',
                                'ms-sys',
                                'isowriter',
                                'unetbootin-static',
                                'b43-firmware',
                                'b43legacy-firmware',
                                'intel-microcode',
                                'ovmf',
                                'btrfs-progs',
                                'cryptsetup',
                                'dosfstools',
                                'e2fsprogs',
                                'ncdu',
                                'ntfs3g',
                                'spl',
                                'squashfs-tools',
                                'xfsprogs',
                                'zfs',
                                'vhba',
                                'bumblebee',
                                'xhost',
                                'xrandr',
                                'radeontop',
                                'nvidia-drivers',
                                'xf86-input-evdev',
                                'xf86-input-joystick',
                                'xf86-input-keyboard',
                                'xf86-input-mouse',
                                'xf86-input-synaptics',
                                'xf86-input-wacom',
                                'xf86-video-amdgpu',
                                'xf86-video-ati',
                                'xf86-video-intel',
                                'xf86-video-nouveau',
                                'xf86-video-qxl',
                                'xf86-video-vesa',
                                'xf86-video-virtualbox',
                                'xf86-video-vmware',
                                'arandr',
                                'ccsm',
                                'compton',
                                'grsync',
                                'primus',
                                'simple-ccsm',
                                'slock',
                                'vdpauinfo',
                                'xscreensaver',
                                'qterminal',
                                'st',
                                'xterm',
                                'compiz-fusion',
                                'emerald',
                                'openbox')
                        ''')
            rows = cursor.fetchall()
            
            for row in rows:
                inx = rows.index(row)
                self.table_system.insertRow(inx)
                self.table_system.setItem(inx, 0, QtWidgets.QTableWidgetItem(row[0]))
                self.table_system.setItem(inx, 1, QtWidgets.QTableWidgetItem(row[1]))
                self.table_system.setItem(inx, 2, QtWidgets.QTableWidgetItem(row[2]))
                self.table_system.setItem(inx, 3, QtWidgets.QTableWidgetItem(row[3]))
                self.table_system.setItem(inx, 4, QtWidgets.QTableWidgetItem(row[4]))
