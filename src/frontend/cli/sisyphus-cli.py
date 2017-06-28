#!/usr/bin/python3

import sys
from libsisyphus import *

check_if_srcmode()

if "__main__" == __name__:
    if "install" in sys.argv[1:]:
        sisyphus_pkg_install()
    elif "uninstall" in sys.argv[1:]:
        sisyphus_pkg_uninstall()
    elif "force-uninstall" in sys.argv[1:]:
        sisyphus_pkg_force_uninstall()
    elif "remove-orphans" in sys.argv[1:]:
        sisyphus_pkg_remove_orphans()
    elif "upgrade" in sys.argv[1:]:
        sisyphus_pkg_system_upgrade()
    elif "auto-install" in sys.argv[1:]:
        sisyphus_pkg_auto_install()
    elif "auto-uninstall" in sys.argv[1:]:
        sisyphus_pkg_auto_uninstall()
    elif "auto-force-uninstall" in sys.argv[1:]:
        sisyphus_pkg_auto_force_uninstall()
    elif "auto-remove-orphans" in sys.argv[1:]:
        sisyphus_pkg_auto_remove_orphans()
    elif "auto-upgrade" in sys.argv[1:]:
        sisyphus_pkg_auto_system_upgrade()
    elif "search" in sys.argv[1:]:
        sisyphus_pkg_search()
    elif "update" in sys.argv[1:]:
        sisyphus_pkg_system_update()
    elif "sysinfo" in sys.argv[1:]:
        sisyphus_pkg_sysinfo()
    elif "help" in sys.argv[1:]:
        sisyphus_pkg_help()
    elif not sys.argv[1:]:
        sisyphus_pkg_help()
