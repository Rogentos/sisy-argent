#!/usr/bin/python3

from libsisyphus import *

sisyphus_singlepkg_spm_csv_path = '/var/lib/sisyphus/csv/portage_singlepkg_spmsync.csv'

def sync_sisyphus_single_spm_csv():
    sisyphusdb = sqlite3.connect(sisyphus_database_path)
    with open(sisyphus_spm_csv_path) as sisyphus_spm_csv:
        for row in csv.reader(sisyphus_spm_csv):
            sisyphusdb.cursor().execute(
                '''DELETE FROM local_packages 
                WHERE category=? AND name=? AND version=?''',
                (row[0], row[1], row[2]))
        sisyphusdb.commit()
        sisyphusdb.close()
    os.remove(sisyphus_spm_csv_path)

def generate_sisyphus_spm_csv():
    subprocess.check_call(['/usr/share/sisyphus/helpers/make_singlepkg_spmsync_csv'])

def sync_sisyphus_single_pkg_spm_csv():
    sisyphusdb = sqlite3.connect(sisyphus_database_path)
    with open(sisyphus_singlepkg_spm_csv_path) as sisyphus_spm_csv:
        for row in csv.reader(sisyphus_spm_csv):
            sisyphusdb.cursor().execute("insert into local_packages (category, name, version, slot, timestamp, description) values (?, ?, ?, ?, ?, ?);", row)
        sisyphusdb.commit()
        sisyphusdb.close()
    os.remove(sisyphus_singlepkg_spm_csv_path)

def sisyphus_pkg_spmsync():
    generate_sisyphus_spm_csv()
    sync_sisyphus_single_spm_csv()

PKGLIST = sys.argv[2:]

if "__main__" == __name__:
    if "spmsync" in sys.argv[1:]:
        print("changing values")
        sync_sisyphus_single_spm_csv()
    elif "spmsync-pkg" in sys.argv[1] and len(sys.argv) >=3:
        print(sys.argv[0])
        print(sys.argv[1])
        print(sys.argv[2:])
    elif not len(sys.argv) >3:
        print("blah")