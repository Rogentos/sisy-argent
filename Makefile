SUBDIRS =
DESTDIR = 
UBINDIR ?= /usr/bin
DESKTOPDIR ?= /usr/share/applications
PIXMAPDIR ?= /usr/share/pixmaps
SISYPHUSDATADIR ?= /usr/share/sisyphus
POLKITDIR ?= /usr/share/polkit-1/actions

all:
	for d in $(SUBDIRS); do $(MAKE) -C $$d; done

clean:
	for d in $(SUBDIRS); do $(MAKE) -C $$d clean; done

install:
	for d in $(SUBDIRS); do $(MAKE) -C $$d install; done

	install -d $(DESTDIR)$(UBINDIR)
	install -m 0755 sisyphus-gui $(DESTDIR)$(UBINDIR)/
	install -m 0755 sisyphus-gui-pkexec $(DESTDIR)$(UBINDIR)/
	install -d $(DESTDIR)$(SISYPHUSDATADIR)
	install -d $(DESTDIR)$(SISYPHUSDATADIR)/helpers
	install -d $(DESTDIR)$(SISYPHUSDATADIR)/icon
	install -d $(DESTDIR)$(SISYPHUSDATADIR)/ui
	install -m 0755 src/helpers/* $(DESTDIR)$(SISYPHUSDATADIR)/helpers/
	install -m 0755 src/frontend/cli/*.py $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 src/frontend/gui/*.py $(DESTDIR)$(SISYPHUSDATADIR)/
	install -m 0755 src/frontend/gui/icon/* $(DESTDIR)$(SISYPHUSDATADIR)/icon/
	install -m 0755 src/frontend/gui/ui/* $(DESTDIR)$(SISYPHUSDATADIR)/ui/
	install -d $(DESTDIR)$(DESKTOPDIR)
	install -m 0755 sisyphus-gui.desktop $(DESTDIR)$(DESKTOPDIR)/
	install -d $(DESTDIR)$(PIXMAPDIR)
	install -m 0644 sisyphus-gui.png $(DESTDIR)$(PIXMAPDIR)
	install -d $(DESTDIR)$(POLKITDIR)
	install -m 0644 org.redcorelinux.sisyphus-gui.policy $(DESTDIR)$(POLKITDIR)/

uninstall:
	rm -rf $(DESTDIR)$(UBINDIR)/sisyphus-gui
	rm -rf $(DESTDIR)$(UBINDIR)/sisyphus-gui-pkexec
	rm -rf $(DESTDIR)$(DESKTOPDIR)/sisyphus-gui.desktop
	rm -rf $(DESTDIR)$(PIXMAPDIR)/sisyphus-gui.png
	rm -rf $(DESTDIR)$(POLKITDIR)/org.redcorelinux.sisyphus-gui.policy
	rm -rf $(DESTDIR)$(SISYPHUSDATADIR)
