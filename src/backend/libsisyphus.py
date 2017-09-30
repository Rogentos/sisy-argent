#!/usr/bin/python3

import animation
import atexit
import csv
import filecmp
import os
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib3

redcore_portage_tree_path = '/usr/portage'
redcore_desktop_overlay_path = '/var/lib/layman/redcore-desktop'
redcore_portage_config_path = '/opt/redcore-build'

sisyphus_remote_csv_url = 'http://mirror.math.princeton.edu/pub/redcorelinux/csv/remote_packages_pre.csv'
sisyphus_remote_csv_path_pre = '/var/lib/sisyphus/csv/remote_packages_pre.csv'
sisyphus_remote_csv_path_post = '/var/lib/sisyphus/csv/remote_packages_post.csv'
sisyphus_removable_csv_url = 'http://mirror.math.princeton.edu/pub/redcorelinux/csv/removable_packages_pre.csv'
sisyphus_removable_csv_path_pre = '/var/lib/sisyphus/csv/removable_packages_pre.csv'
sisyphus_removable_csv_path_post = '/var/lib/sisyphus/csv/removable_packages_post.csv'
sisyphus_local_csv_path_pre = '/var/lib/sisyphus/csv/local_packages_pre.csv'
sisyphus_local_csv_path_post = '/var/lib/sisyphus/csv/local_packages_post.csv'
sisyphus_spm_csv_path = '/var/lib/sisyphus/csv/portage_spmsync.csv'
sisyphus_database_path = '/var/lib/sisyphus/db/sisyphus.db'

def check_if_root():
    if not os.getuid() == 0:
        sys.exit("\nYou need root permissions to do this, exiting!\n")

def check_system_mode():
    portage_binmode_make_conf = '/opt/redcore-build/conf/intel/portage/make.conf.amd64-binmode'
    portage_mixedmode_make_conf = '/opt/redcore-build/conf/intel/portage/make.conf.amd64-mixedmode'
    portage_make_conf_symlink = '/etc/portage/make.conf'

    if not os.path.islink(portage_make_conf_symlink):
        print("\nmake.conf is not a symlink, refusing to run!\n")
        sys.exit(1)
    else:
        if os.path.realpath(portage_make_conf_symlink) == portage_binmode_make_conf:
            pass
        elif os.path.realpath(portage_make_conf_symlink) == portage_mixedmode_make_conf:
            pass
        else:
            print("\nThe system is not set to binmode or mixedmode, refusing to run!\n")
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

def fetch_sisyphus_removable_packages_table_csv():
    http = urllib3.PoolManager()

    if not os.path.isfile(sisyphus_removable_csv_path_pre):
        os.mknod(sisyphus_removable_csv_path_pre)
        with http.request('GET', sisyphus_removable_csv_url, preload_content=False) as tmp_buffer, open(sisyphus_removable_csv_path_post, 'wb') as output_file:
            shutil.copyfileobj(tmp_buffer, output_file)
    else:
        with http.request('GET', sisyphus_removable_csv_url, preload_content=False) as tmp_buffer, open(sisyphus_removable_csv_path_post, 'wb') as output_file:
            shutil.copyfileobj(tmp_buffer, output_file)

def sync_redcore_portage_tree_and_desktop_overlay():
    subprocess.check_call(['emerge', '--sync', '--quiet'])

def sync_redcore_portage_config():
    os.chdir(redcore_portage_config_path)
    subprocess.call(['git', 'pull', '--quiet'])

def sync_sisyphus_remote_packages_table_csv():
    if not filecmp.cmp(sisyphus_remote_csv_path_pre, sisyphus_remote_csv_path_post):
        sisyphusdb = sqlite3.connect(sisyphus_database_path)
        sisyphusdb.cursor().execute('''drop table if exists remote_packages''')
        sisyphusdb.cursor().execute('''create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT,timestamp TEXT,description TEXT)''')
        with open(sisyphus_remote_csv_path_post) as sisyphus_remote_csv:
            for row in csv.reader(sisyphus_remote_csv):
                sisyphusdb.cursor().execute("insert into remote_packages (category, name, version, slot, timestamp, description) values (?, ?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
    shutil.move(sisyphus_remote_csv_path_post, sisyphus_remote_csv_path_pre)

def sync_sisyphus_removable_packages_table_csv():
    if not filecmp.cmp(sisyphus_removable_csv_path_pre, sisyphus_removable_csv_path_post):
        sisyphusdb = sqlite3.connect(sisyphus_database_path)
        sisyphusdb.cursor().execute('''drop table if exists removable_packages''')
        sisyphusdb.cursor().execute('''create table removable_packages (category TEXT,name TEXT,version TEXT,slot TEXT,timestamp TEXT,description TEXT)''')
        with open(sisyphus_removable_csv_path_post) as sisyphus_removable_csv:
            for row in csv.reader(sisyphus_removable_csv):
                sisyphusdb.cursor().execute("insert into removable_packages (category, name, version, slot, timestamp, description) values (?, ?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
    shutil.move(sisyphus_removable_csv_path_post, sisyphus_removable_csv_path_pre)
        
def sync_sisyphus_database_remote_packages_table():
    fetch_sisyphus_remote_packages_table_csv()
    sync_sisyphus_remote_packages_table_csv()

def sync_sisyphus_database_removable_packages_table():
    fetch_sisyphus_removable_packages_table_csv()
    sync_sisyphus_removable_packages_table_csv()

@animation.wait('syncing remote databases')
def redcore_sync():
    check_if_root()
    sync_redcore_portage_tree_and_desktop_overlay()
    sync_redcore_portage_config()
    sync_sisyphus_database_remote_packages_table()
    sync_sisyphus_database_removable_packages_table()

def generate_sisyphus_local_packages_table_csv_pre():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_local_csv_pre']) # this is really hard to do in python, so we cheat with a bash helper script

def generate_sisyphus_local_packages_table_csv_post():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_local_csv_post']) # this is really hard to do in python, so we cheat with a bash helper script

def sync_sisyphus_local_packages_table_csv():
    if not filecmp.cmp(sisyphus_local_csv_path_pre, sisyphus_local_csv_path_post):
        sisyphusdb = sqlite3.connect(sisyphus_database_path)
        sisyphusdb.cursor().execute('''drop table if exists local_packages''')
        sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT,timestamp TEXT,description TEXT)''')
        with open(sisyphus_local_csv_path_post) as sisyphus_local_csv:
            for row in csv.reader(sisyphus_local_csv):
                sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot, timestamp, description) values (?, ?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
    shutil.move(sisyphus_local_csv_path_post, sisyphus_local_csv_path_pre)

def generate_sisyphus_spm_csv():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_spmsync_csv']) # this is really hard to do in python, so we cheat using a bash helper script

def sync_sisyphus_spm_csv():
    sisyphusdb = sqlite3.connect(sisyphus_database_path)
    sisyphusdb.cursor().execute('''drop table if exists local_packages''')
    sisyphusdb.cursor().execute('''create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT,timestamp TEXT,description TEXT)''')
    with open(sisyphus_spm_csv_path) as sisyphus_spm_csv:
        for row in csv.reader(sisyphus_spm_csv):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot, timestamp, description) values (?, ?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
    os.remove(sisyphus_spm_csv_path)

@animation.wait('syncing local databases')
def sisyphus_pkg_spmsync():
    generate_sisyphus_spm_csv()
    sync_sisyphus_spm_csv()

def sisyphus_pkg_install(PKGLIST):
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '-avq'] + PKGLIST)
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_install(PKGLIST):
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '-vq'] + PKGLIST)
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_uninstall(PKGLIST):
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '--depclean', '-avq'] + PKGLIST)
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_uninstall(PKGLIST):
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '--depclean', '-vq'] + PKGLIST)
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_force_uninstall(PKGLIST):
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '--unmerge', '-avq'] + PKGLIST)
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_force_uninstall(PKGLIST):
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '--unmerge', '-vq'] + PKGLIST)
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_remove_orphans():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '--depclean', '-avq'])
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_remove_orphans():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '--depclean', '-vq'])
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_system_upgrade():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '-uDavNq', '--with-bdeps=y', '@world'])
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_auto_system_upgrade():
    redcore_sync()
    generate_sisyphus_local_packages_table_csv_pre()
    portage_call = subprocess.Popen(['emerge', '-uDvNq', '--with-bdeps=y', '@world'])
    atexit.register(kill_bg_portage, portage_call)
    portage_call.communicate()
    generate_sisyphus_local_packages_table_csv_post()
    sync_sisyphus_local_packages_table_csv()

def sisyphus_pkg_search(PKGLIST):
    subprocess.check_call(['emerge', '--search'] + PKGLIST)

def sisyphus_pkg_system_update():
    redcore_sync()

def sisyphus_pkg_sysinfo():
    subprocess.check_call(['emerge', '--info'])

def sisyphus_db_rescue():
    if os.path.exists(sisyphus_remote_csv_path_pre):
        os.remove(sisyphus_remote_csv_path_pre)
    if os.path.exists(sisyphus_removable_csv_path_pre):
        os.remove(sisyphus_removable_csv_path_pre)
    if os.path.exists(sisyphus_local_csv_path_pre):
        os.remove(sisyphus_local_csv_path_pre)
    if os.path.exists(sisyphus_database_path):
        os.remove(sisyphus_database_path)
    sisyphus_pkg_system_update()
    sisyphus_pkg_spmsync()

def kill_bg_portage(bg_portage):
        bg_portage.terminate()

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
    print("update - Update the Portage tree, Overlay(s), Portage config files && Sisyphus database remote_packages table")
    print("upgrade -  Upgrade the system")
    print("search - Search for packages")
    print("spmsync - Sync Sisyphus database with Portage database (if you install something with Portage, not Sisyphus)")
    print("rescue - Rescue Sisyphus database if lost or corrupted")
    print("sysinfo - Display information about installed core packages and portage configuration")
