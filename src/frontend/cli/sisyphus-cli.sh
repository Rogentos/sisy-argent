#!/usr/bin/env bash

source /usr/lib/sisyphus/libsisyphus.sh

checksystemmode

action=$1
shift

case "$action" in
	install)
		checksync
		localdbcsvpre
		emerge -a "$@"
		updatelocaldb
		;;
	uninstall)
		checksync
		localdbcsvpre
		emerge --depclean -a "$@"
		updatelocaldb
		;;
	force-uninstall)
		checksync
		localdbcsvpre
		emerge --unmerge -a "$@"
		updatelocaldb
		;;
	remove-orphans)
		checksync
		localdbcsvpre
		emerge --depclean -a
		updatelocaldb
		;;
	upgrade)
		checksync
		localdbcsvpre
		emerge -uDaN --with-bdeps=y @system @world "$@"
		updatelocaldb
		;;
	auto-install)
		redcoresync
		localdbcsvpre
		emerge "$@"
		updatelocaldb
		;;
	auto-uninstall)
		redcoresync
		localdbcsvpre
		emerge --depclean "$@"
		updatelocaldb
		;;
	auto-force-uninstall)
		redcoresync
		localdbcsvpre
		emerge --unmerge "$@"
		updatelocaldb
		;;
	auto-remove-orphans)
		redcoresync
		localdbcsvpre
		emerge --depclean -q
		updatelocaldb
		;;
	auto-upgrade)
		redcoresync
		localdbcsvpre
		emerge -uDN --with-bdeps=y @system @world "$@"
		updatelocaldb
		;;
	search)
		emerge -s "$@"
		;;
	update)
		redcoresync
		;;
	belongs)
		equery belongs "$@"
		;;
	depends)
		equery depends "$@"
		;;
	files)
		equery files "$@"
		;;
	sysinfo)
		emerge --info
		;;
	*)
		cat <<-"EOH"
			Usage: sisyphus command [package(s)]

			sisyphus is a simple wrapper around portage, gentoolkit, and portage-utils that provides an
			apt-get/yum-alike interface to these commands, to assist people transitioning from
			Debian/RedHat-based systems to Gentoo.

			Commands :
				install - Install new packages
				uninstall - Uninstall packages safely
				force-uninstall - *Unsafely* uninstall packages
				remove-orphans - Uninstall packages that are no longer needed
				upgrade -  Upgrade system
				auto-install - Install new packages (no confirmation)
				auto-uninstall - Uninstall packages safely (no confirmation)
				auto-force-uninstall - *Unsafely* uninstall packages (no confirmation)
				auto-remove-orphans - Uninstall packages that are no longer needed (no confirmation)
				auto-upgrade - Upgrade system (no confirmation)
				search - Search for packages
				update - Resync portage tree, portage config && redcore overlay
				belongs - List what package FILE(s) belong to
				depends - List all packages directly depending on given package
				files - List all files installed by package
				sysinfo - Display information about installed core packages and portage configuration
		EOH
		;;
esac
