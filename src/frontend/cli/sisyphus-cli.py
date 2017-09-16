#!/usr/bin/python3

import sys
from libsisyphus import *

check_system_mode()

PKGLIST = sys.argv[2:]

if "__main__" == __name__:
    if "install" in sys.argv[1:]:
        sisyphus_pkg_install(PKGLIST)
    elif "auto-install" in sys.argv[1:]:
        sisyphus_pkg_auto_install(PKGLIST)
    elif "uninstall" in sys.argv[1:]:
        sisyphus_pkg_uninstall(PKGLIST)
    elif "auto-uninstall" in sys.argv[1:]:
        sisyphus_pkg_auto_uninstall(PKGLIST)
    elif "force-uninstall" in sys.argv[1:]:
        sisyphus_pkg_force_uninstall(PKGLIST)
    elif "auto-force-uninstall" in sys.argv[1:]:
        sisyphus_pkg_auto_force_uninstall(PKGLIST)
    elif "remove-orphans" in sys.argv[1:]:
        sisyphus_pkg_remove_orphans()
    elif "auto-remove-orphans" in sys.argv[1:]:
        sisyphus_pkg_auto_remove_orphans()
    elif "upgrade" in sys.argv[1:]:
        sisyphus_pkg_system_upgrade()
    elif "auto-upgrade" in sys.argv[1:]:
        sisyphus_pkg_auto_system_upgrade()
    elif "search" in sys.argv[1:]:
        sisyphus_pkg_search(PKGLIST)
    elif "update" in sys.argv[1:]:
        sisyphus_pkg_system_update()
    elif "spmsync" in sys.argv[1:]:
        sisyphus_pkg_spmsync()
    elif "sysinfo" in sys.argv[1:]:
        sisyphus_pkg_sysinfo()
    elif "help" in sys.argv[1:]:
        sisyphus_pkg_help()
    elif not sys.argv[1:]:
        sisyphus_pkg_help()
