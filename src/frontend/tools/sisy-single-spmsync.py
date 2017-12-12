#!/usr/bin/python3

from libsisyphus import *

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

def sisyphus_pkg_spmsync():
    sync_sisyphus_single_spm_csv()

if "__main__" == __name__:
    if "spmsync" in sys.argv[1:]:
        sync_sisyphus_single_spm_csv()