#!/usr/bin/python3

from libsisyphus import *

PKGLIST = sys.argv[2:]
sisyphus_singlepkg_spm_csv_path = '/var/lib/sisyphus/csv/portage_singlepkg_spmsync.csv'


# these variables are to be used only if you know what portage is
def portage_pkg_pn():
    try:
        os.environ["PN"]
    except:
        pass
    else:
        return True


def portage_pkg_cat():
    try:
        os.environ["CATEGORY"]
    except:
        pass
    else:
        return True


def portage_pkg_pvr():
    try:
        os.environ["PVR"]
    except:
        pass
    else:
        return True


def check_portage_binpkg_vars():
    try:
        portage_pkg_pn() and portage_pkg_cat() and portage_pkg_pvr()
    except:
        pass


def sync_sisyphus_single_spm_csv():
    sisyphusdb = sqlite3.connect(sisyphus_database_path)
    if not os.path.isfile(sisyphus_singlepkg_spm_csv_path):
        print("Please populate the csv file with relevant fields (category, name, version): ", sisyphus_singlepkg_spm_csv_path)
        quit()
    with open(sisyphus_singlepkg_spm_csv_path) as sisyphus_spm_csv:
        for row in csv.reader(sisyphus_spm_csv):
            sisyphusdb.cursor().execute(
                '''DELETE FROM local_packages 
                WHERE category=? AND name=? AND version=?''',
                (row[0], row[1], row[2]))
        sisyphusdb.commit()
        sisyphusdb.close()
    os.remove(sisyphus_singlepkg_spm_csv_path)


def sync_sisyphus_singlepkg_db():
    sisyphusdb = sqlite3.connect(sisyphus_database_path)
    sisyphusdb.cursor().execute('''DELETE FROM local_packages
        WHERE category=? AND name=? AND version=?''', (os.environ["CATEGORY"], os.environ["PN"], os.environ["PVR"]))
    sisyphusdb.commit()
    sisyphusdb.close()


def generate_sisyphus_singlepkg_spm_csv():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_singlepkg_spmsync_csv'] + sys.argv[1:])


def sync_sisyphus_single_pkg_spm_csv():
    sisyphusdb = sqlite3.connect(sisyphus_database_path)
    with open(sisyphus_singlepkg_spm_csv_path) as sisyphus_spm_csv:
        for row in csv.reader(sisyphus_spm_csv):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot, timestamp, description) values (?, ?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
    os.remove(sisyphus_singlepkg_spm_csv_path)


def sisyphus_singlepkg_spmsync():
    try:
        check_portage_binpkg_vars()
    except:
        generate_sisyphus_singlepkg_spm_csv()
        sync_sisyphus_single_spm_csv()
    else:
        sync_sisyphus_singlepkg_db()
        if os.path.isfile(sisyphus_singlepkg_spm_csv_path):
            os.remove(sisyphus_singlepkg_spm_csv_path)


if "__main__" == __name__:
    if "spmsync" in sys.argv[1:]:
        sisyphus_singlepkg_spmsync()
    elif "spmsync-pkg" in sys.argv[1:] and len(sys.argv) >= 3:
        generate_sisyphus_singlepkg_spm_csv()
        sync_sisyphus_single_pkg_spm_csv()
    elif "spmsync-pkg" in sys.argv[1:] and len(sys.argv) <= 2:
        print("Please specify a package or a list of packages")
    elif len(sys.argv) < 2:
        print("You`ve got two functions: spmsync or spmsync-pkg <pkg>")