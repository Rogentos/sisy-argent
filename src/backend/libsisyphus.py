#!/usr/bin/python3

import csv
import filecmp
import os
import shutil
import sqlite3
import sys
import urllib3
import subprocess

redcore_portage_tree_path = '/usr/portage'
redcore_desktop_overlay_path = '/var/lib/layman/redcore-desktop'
redcore_portage_config_path = '/opt/redcore-build'

sisyphus_remote_csv_url = 'http://mirror.math.princeton.edu/pub/redcorelinux/csv/remote_preinst.csv'
sisyphus_remote_csv_path_pre = '/var/lib/sisyphus/csv/remote_preinst.csv'
sisyphus_remote_csv_path_post = '/var/lib/sisyphus/csv/remote_postinst.csv'
sisyphus_local_csv_path_pre = '/var/lib/sisyphus/csv/local_preinst.csv'
sisyphus_local_csv_path_post = '/var/lib/sisyphus/csv/local_postinst.csv'
sisyphus_database_path = '/var/lib/sisyphus/db/sisyphus.db'

def check_if_root():
    if not os.getuid() == 0:
        sys.exit("\nyou need root permissions to do this. exiting!\n")

def check_if_srcmode():
    portage_srcmode_make_conf = '/opt/redcore-build/conf/intel/portage/make.conf.amd64-srcmode'
    portage_make_conf_symlink = '/etc/portage/make.conf'

    if os.path.islink(portage_make_conf_symlink) and os.path.realpath(portage_make_conf_symlink) == portage_srcmode_make_conf:
        print("\nthe system is set to srcmode (full gentoo), refusing to run!\n")
        sys.exit(1)

def check_redcore_portage_tree():
    os.chdir(redcore_portage_tree_path)
    subprocess.call(['git', 'remote', 'update'])
    redcore_portage_tree_local_hash = subprocess.check_output(['git', 'rev-parse', '@'])
    redcore_portage_tree_remote_hash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    if not redcore_portage_tree_local_hash == redcore_portage_tree_remote_hash:
        print("\nredcore desktop portage tree is out-of-date. run 'sisyphus update' first!\n")
        sys.exit(1)

def check_redcore_desktop_overlay():
    os.chdir(redcore_desktop_overlay_path)
    subprocess.call(['git', 'remote', 'update'])
    redcore_desktop_overlay_local_hash = subprocess.check_output(['git', 'rev-parse', '@'])
    redcore_desktop_overlay_remote_hash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    if not redcore_desktop_overlay_local_hash == redcore_desktop_overlay_remote_hash:
        print("\nredcore desktop overlay is out-of-date. run 'sisyphus update' first!\n")
        sys.exit(1)

def check_redcore_portage_config():
    os.chdir(redcore_portage_config_path)
    subprocess.call(['git', 'remote', 'update'])
    redcore_portage_config_local_hash = subprocess.check_output(['git', 'rev-parse', '@'])
    redcore_portage_config_remote_hash = subprocess.check_output(['git', 'rev-parse', '@{u}'])

    if not redcore_portage_config_local_hash == redcore_portage_config_remote_hash:
        print("\nredcore desktop portage config is out-of-date. run 'sisyphus update' first!\n")
        sys.exit(1)

def fetch_sisyphus_remote_packages_table_csv():
    http = urllib3.PoolManager()
    
    if not os.path.isfile(sisyphus_remote_csv_path_pre):
        os.mknod(sisyphus_remote_csv_path_pre)
        with http.request('GET', sisyphus_remote_csv_url, preload_content=False) as tmp_buffer, open(sisyphus_remote_csv_path_post, 'wb') as output_file:       
            shutil.copyfileobj(tmp_buffer, output_file)
    else:
        with http.request('GET', sisyphus_remote_csv_url, preload_content=False) as tmp_buffer, open(sisyphus_remote_csv_path_post, 'wb') as output_file:
            shutil.copyfileobj(tmp_buffer, output_file)

def check_sisyphus_remote_packages_table_csv():
    if not filecmp.cmp(sisyphus_remote_csv_path_pre, sisyphus_remote_csv_path_post):
        print("\nsisyphus database remote_packages table is out-of-date. run 'sisyphus update' first!\n")
        os.remove(sisyphus_remote_csv_path_post)
        sys.exit(1)
    else:
        os.remove(sisyphus_remote_csv_path_post)

def check_sisyphus_remote_packages_table():
    fetch_sisyphus_remote_packages_table_csv()
    check_sisyphus_remote_packages_table_csv()

def check_sync():
    check_if_root()
    check_redcore_portage_tree()
    check_redcore_desktop_overlay()
    check_redcore_portage_config()
    check_sisyphus_remote_packages_table()

def sync_redcore_portage_tree_and_desktop_overlay():
    subprocess.call(['emerge', '--sync'])

def sync_redcore_portage_config():
    os.chdir(redcore_portage_config_path)
    print(">>> Syncing 'portage config' into '/etc/portage'...")
    print("/usr/bin/git pull")
    subprocess.call(['git', 'pull'])
    print("=== Sync completed for 'portage config'")

def sync_sisyphus_remote_packages_table_csv():
    if not filecmp.cmp(sisyphus_remote_csv_path_pre, sisyphus_remote_csv_path_post):
        print(">>> Syncing 'sisyphus database remote_packages table' into '/var/lib/sisyphus/db/sisyphus.db'")
        print("/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db")
        sisyphusdb = sqlite3.connect(sisyphus_database_path)
        sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
        sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT,description TEXT)''')
        with open(sisyphus_remote_csv_path_post) as sisyphus_remote_csv:
            for row in csv.reader(sisyphus_remote_csv):
                sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot, description) values (?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
        print("=== Sync completed for 'sisyphus database remote_packages table'")
    else:
        print(">>> Syncing 'sisyphus database remote_packages table' into '/var/lib/sisyphus/db/sisyphus.db'")
        print("/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db")
        print("Already up-to-date.")
        print("=== Sync completed for 'sisyphus database remote_packages table'")
    shutil.move(sisyphus_remote_csv_path_post, sisyphus_remote_csv_path_pre)
        
def sync_sisyphus_database_remote_packages_table():
    fetch_sisyphus_remote_packages_table_csv()
    sync_sisyphus_remote_packages_table_csv()

def redcore_sync():
    check_if_root()
    sync_redcore_portage_tree_and_desktop_overlay()
    sync_redcore_portage_config()
    sync_sisyphus_database_remote_packages_table()

def generate_sisyphus_local_packages_table_csv_pre():
    subprocess.call(['/usr/share/sisyphus/helpers/make_local_csv_pre']) # this is really hard to do in python, so we cheat with a bash helper script

def generate_sisyphus_local_packages_table_csv_post():
    subprocess.call(['/usr/share/sisyphus/helpers/make_local_csv_post']) # this is really hard to do in python, so we cheat with a bash helper script

def sync_sisyphus_local_packages_table_csv():
    if filecmp.cmp(sisyphus_local_csv_path_pre, sisyphus_local_csv_path_post):
        print(">>> Syncing 'sisyphus database local_packages table' into '/var/lib/sisyphus/db/sisyphus.db'")
        print("/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db")
        print("Already up-to-date.")
        print("=== Sync completed for 'sisyphus database local_packages table'")
    else:
        print(">>> Syncing 'sisyphus database local_packages table' into '/var/lib/sisyphus/db/sisyphus.db'")
        print("/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db")
        sisyphusdb = sqlite3.connect(sisyphus_database_path)
        sisyphusdb.cursor().execute('''drop table if exists local_packages''')
        sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT,description TEXT)''')
        with open(sisyphus_local_csv_path_post) as sisyphus_local_csv:
            for row in csv.reader(sisyphus_local_csv):
                sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot, description) values (?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
        print("=== Sync completed for 'sisyphus database local_packages table'")
    shutil.move(sisyphus_local_csv_path_post, sisyphus_local_csv_path_pre)

def sisyphus_pkg_install():
    check_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '-a'] + sys.argv[2:])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_uninstall():
    check_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '--depclean', '-a'] + sys.argv[2:])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_force_uninstall():
    check_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '--unmerge', '-a'] + sys.argv[2:])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_remove_orphans():
    check_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '--depclean', '-a'])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_system_upgrade():
    check_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '-uDaN', '--with-bdeps=y', '@world'])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_install():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge'] + sys.argv[2:])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_uninstall():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '--depclean'] + sys.argv[2:])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_force_uninstall():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '--unmerge'] + sys.argv[2:])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_remove_orphans():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '--depclean', '-q'])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_system_upgrade():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    subprocess.call(['emerge', '-uDN', '--with-bdeps=y', '@world'])
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_search():
    subprocess.call(['emerge', '--search'] + sys.argv[2:])

def sisyphus_pkg_system_update():
    redcore_sync()

def sisyphus_pkg_belongs():
    subprocess.call(['equery', 'belongs'] + sys.argv[2:])

def sisyphus_pkg_depends():
    subprocess.call(['equery', 'depends'] + sys.argv[:2])

def sisyphus_pkg_files():
    subprocess.call(['equery', 'files'] + sys.argv[:2])

def sisyphus_pkg_sysingo():
    subprocess.call(['emerge', '--info'])

def sisyphus_pkg_help():
    print("\nUsage : sisyphus command [package(s)] || [file(s)]\n")
    print("Sisyphus is a simple python wrapper around portage, gentoolkit, and portage-utils that provides")
    print("an apt-get/yum-alike interface to these commands, to assist newcomer people transitioning from")
    print("Debian/RedHat-based systems to Gentoo.\n")
    print("Commands :\n")
    print("install - Install new packages")
    print("uninstall - Uninstall packages *safely* (INFO : If reverse deps are found, package(s) will NOT be uninstalled)")
    print("force-uninstall - Uninstall packages *unsafely* (WARNING : This option will ignore reverse deps, which may break your system)")
    print("remove-orphans - Uninstall packages that are no longer needed")
    print("upgrade -  Upgrade the system")
    print("auto-install - Install new packages - no confirmation")
    print("auto-uninstall - Uninstall packages *safely* - no confirmation (INFO : If reverse deps are found, package(s) will NOT be uninstalled)")
    print("auto-force-uninstall - Uninstall packages *unsafely* - no confirmation (WARNING : This option will ignore reverse deps, which may break your system)")
    print("auto-remove-orphans - Uninstall packages that are no longer needed - no confirmation")
    print("auto-upgrade - Upgrade the system - no confirmation")
    print("search - Search for packages")
    print("update - Update the Portage tree, Overlay(s), Portage config files && Sisyphus database remote_packages table")
    print("belongs - List what package FILE(s) belong to (e.g.: sisyphus belongs /usr/bin/wine -> app-emulation/wine : aka the /usr/bin/wine file belongs to the app-emulation/wine package)")
    print("depends - List all packages directly depending on given package (e.g.: sisyphus depends wine -> app-emulation/winetricks : aka app-emulation/winetricks package depends on wine)")
    print("files - List all files installed by package (e.g.: sisyphus files wine : will display all files installed by app-emulation/wine package)")
    print("sysinfo - Display information about installed core packages and portage configuration")