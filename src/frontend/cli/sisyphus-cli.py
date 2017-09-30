#!/usr/bin/python3

import sys
from libsisyphus import *

check_system_mode()

PKGLIST = sys.argv[2:]

if "__main__" == __name__:
    if "install" in sys.argv[1:]:
        sisyphus_pkg_install(PKGLIST)
    elif "uninstall" in sys.argv[1:]:
        sisyphus_pkg_uninstall(PKGLIST)
    elif "force-uninstall" in sys.argv[1:]:
        sisyphus_pkg_force_uninstall(PKGLIST)
    elif "remove-orphans" in sys.argv[1:]:
        sisyphus_pkg_remove_orphans()
    elif "update" in sys.argv[1:]:
        sisyphus_pkg_system_update
    elif "upgrade" in sys.argv[1:]:
        sisyphus_pkg_system_upgrade()
    elif "search" in sys.argv[1:]:
        sisyphus_pkg_search(PKGLIST)
    elif "spmsync" in sys.argv[1:]:
        sisyphus_pkg_spmsync()
    elif "rescue" in sys.argv[1:]:
        sisyphus_db_rescue()
    elif "sysinfo" in sys.argv[1:]:
        sisyphus_pkg_sysinfo()
    elif "help" in sys.argv[1:]:
        sisyphus_pkg_help()
    elif not sys.argv[1:]:
        sisyphus_pkg_help()
