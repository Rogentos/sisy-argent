#!/usr/bin/env bash

# import gentoo functions
source /lib/gentoo/functions.sh

checkroot () {
	if [[ "$(whoami)" != root ]] ; then
		eerror "You're not root?...No cookies for you, go away !!!"
		exit 1
	fi
}

checksystemmode() {
	if [[ "$(readlink -f "/etc/portage/make.conf")" = /opt/redcore-build/conf/intel/portage/make.conf.amd64-srcmode ]] ; then
		eerror "The system is set to srcmode (full Gentoo mode), cowardly refusing to run!"
		exit 1
	fi
}

checkportageconfig () {
	pushd /opt/redcore-build > /dev/null 2>&1
	git remote update > /dev/null 2>&1
	export local confhash=$(git rev-parse @)
	export local rconfhash=$(git rev-parse @{u})
	if [ $confhash != $rconfhash ] ; then
		eerror "Portage config is out-of-date, run "sisyphus update" first"
		exit 1
	fi
	popd > /dev/null 2>&1
}

checkportagetree () {
	pushd /usr/portage > /dev/null 2>&1
	git remote update > /dev/null 2>&1
	export local treehash=$(git rev-parse @)
	export local rtreehash=$(git rev-parse @{u})
	if [ $treehash != $rtreehash ] ; then
		eerror "Portage tree is out-of-date, run "sisyphus update" first"
		exit 1
	fi
	popd > /dev/null 2>&1
}

checkredcoreoverlay () {
	pushd /var/lib/layman/redcore-desktop > /dev/null 2>&1
	git remote update > /dev/null 2>&1
	export local overlayhash=$(git rev-parse @)
	export local roverlayhash=$(git rev-parse @{u})
	if [  $overlayhash != $roverlayhash ] ; then
		eerror "Redcore Desktop overlay is out-of-date, run "sisyphus update" first"
		exit 1
	fi
}

remotedbcsvget () {
	if [[ ! -f /var/lib/sisyphus/csv/remote_preinst.csv ]] ; then
		pushd /var/lib/sisyphus/csv > /dev/null 2>&1
		touch remote_preinst.csv
		wget -c http://mirror.math.princeton.edu/pub/redcorelinux/csv/remote_preinst.csv -O remote_postinst.csv > /dev/null 2>&1
		popd > /dev/null 2>&1
	elif [[ -f /var/lib/sisyphus/csv/remote_preinst.csv ]] ; then
		pushd /var/lib/sisyphus/csv > /dev/null 2>&1
		wget -c http://mirror.math.princeton.edu/pub/redcorelinux/csv/remote_preinst.csv -O remote_postinst.csv > /dev/null 2>&1
		popd > /dev/null 2>&1
	fi
}

remotedbcsvcheck () {
	if ! cmp /var/lib/sisyphus/csv/remote_preinst.csv /var/lib/sisyphus/csv/remote_postinst.csv > /dev/null 2>&1 ; then
		eerror "SisyphusDB : "remote_packages" table is out-of-date, run "sisyphus update" first"
		rm -rf /var/lib/sisyphus/csv/remote_postinst.csv
		exit 1
	elif cmp /var/lib/sisyphus/csv/remote_preinst.csv /var/lib/sisyphus/csv/remote_postinst.csv > /dev/null 2>&1 ; then
		rm -rf /var/lib/sisyphus/csv/remote_postinst.csv
	fi
}

checkremotedb () {
	remotedbcsvget
	remotedbcsvcheck
}

checksync () {
	checkroot
	checkportagetree
	checkredcoreoverlay
	checkportageconfig
	checkremotedb
}

syncrepos () {
	emerge --sync
}

syncportageconfig () {
	pushd /opt/redcore-build > /dev/null 2>&1
	echo ">>> Syncing 'portage config' into '/etc/portage'..."
	echo "/usr/bin/git pull"
	git pull
	echo "=== Sync completed for 'portage config'"
	popd > /dev/null 2>&1
}

remotedbcsvsync () {
	if ! cmp /var/lib/sisyphus/csv/remote_preinst.csv /var/lib/sisyphus/csv/remote_postinst.csv > /dev/null 2>&1 ; then
		echo ">>> Syncing 'SisyphusDB remote_packages' into '/var/lib/sisyphus/db/sisyphus.db'"
		echo "/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db"
		pushd /var/lib/sisyphus/db > /dev/null 2>&1
		sqlite3 -echo sisyphus.db<<-EXIT_HERE
		drop table if exists remote_packages;
		create table remote_packages (category TEXT,name TEXT,version TEXT,slot TEXT,description TEXT);
		.mode csv
		.import /var/lib/sisyphus/csv/remote_postinst.csv remote_packages
		EXIT_HERE
		popd > /dev/null 2>&1
		echo "=== Sync completed for 'SisyphusDB remote_packages'"
	elif cmp /var/lib/sisyphus/csv/remote_preinst.csv /var/lib/sisyphus/csv/remote_postinst.csv > /dev/null 2>&1 ; then
		echo ">>> Syncing 'SisyphusDB remote_packages' into '/var/lib/sisyphus/db/sisyphus.db'"
		echo "/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db"
		echo "Already up-to-date."
		echo "=== Sync completed for 'SisyphusDB remote_packages'"
	fi
	mv /var/lib/sisyphus/csv/remote_postinst.csv /var/lib/sisyphus/csv/remote_preinst.csv
}

syncremotedb() {
	remotedbcsvget
	remotedbcsvsync
}

redcoresync () {
	checkroot
	syncrepos
	syncportageconfig
	syncremotedb
}

localdbcsvpre () {
	if [[ ! -f /var/lib/sisyphus/csv/local_preinst.csv ]] ; then
		for i in $(qlist -ICv); do
			pushd /var/db/pkg/$i > /dev/null 2>&1
			echo "$(<CATEGORY),$(sed -re "s/-([0-9])/,\1/" <PF),$(<SLOT),$(sed -e "s/\"//g" -e "s/\'//g" -e "s/\,//g" <DESCRIPTION)" >> /var/lib/sisyphus/csv/local_preinst.csv
			popd > /dev/null 2>&1
		done
	fi
}

localdbcsvpost () {
	for i in $(qlist -ICv); do
		pushd /var/db/pkg/$i > /dev/null 2>&1
		echo "$(<CATEGORY),$(sed -re "s/-([0-9])/,\1/" <PF),$(<SLOT),$(sed -e "s/\"//g" -e "s/\'//g" -e "s/\,//g" <DESCRIPTION)" >> /var/lib/sisyphus/csv/local_postinst.csv
		popd > /dev/null 2>&1
	done
}

localdbcsvsync () {
	if cmp /var/lib/sisyphus/csv/local_preinst.csv /var/lib/sisyphus/csv/local_postinst.csv > /dev/null 2>&1 ; then
		einfo "'PortageDB' && 'SisyphusDB local_packages' are in sync, nothing to do..."
	else
		einfo "'PortageDB' && 'SisyphusDB local_packages' are out of sync, syncing now..."
		echo "/usr/bin/sqlite3 /var/lib/sisyphus/db/sisyphus.db"
		pushd /var/lib/sisyphus/db > /dev/null 2>&1
		sqlite3 -echo sisyphus.db<<-EXIT_HERE
		drop table if exists local_packages;
		create table local_packages (category TEXT,name TEXT,version TEXT,slot TEXT,description TEXT);
		.mode csv
		.import /var/lib/sisyphus/csv/local_postinst.csv local_packages
		EXIT_HERE
		popd > /dev/null 2>&1
		einfo "'PortageDB' && 'SisyphusDB local_packages' resync complete..."
	fi
	mv /var/lib/sisyphus/csv/local_postinst.csv /var/lib/sisyphus/csv/local_preinst.csv
}

updatelocaldb () {
	checkroot
	localdbcsvpost
	localdbcsvsync
}
