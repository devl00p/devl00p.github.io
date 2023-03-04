#!/bin/bash
# devloop.lyua.org
# saveconfig.sh december 2005

function makebackup
{
  cd "$dirname"
  tar c * > /tmp/$(uname -n)-$(date +%F).tar 2> /dev/null
  rm -f "/tmp/$(uname -n)-$(date +%F).tar.bz2"
  bzip2 /tmp/$(uname -n)-$(date +%F).tar
  echo "Deleting temporary files..."
  rm -rf "$dirname"
  rm -f "$tmpfile"
  echo
  echo "Configuration saved to /tmp/$(uname -n)-$(date +%F).tar.bz2"
}

echo "SaveConfig v1.0 by devloop"
echo "devloop.lyua.org   12/2005"
echo
dirname=$(tempfile)
rm -f $dirname
mkdir $dirname
echo "Using temporary directory $dirname"
scriptname=$0
nblines=$(wc -l $scriptname|cut -d' ' -f1)
tmpfile=$(tempfile)
echo "Using temporary file $tmpfile"
grep -A$nblines "# \"File List\"" $scriptname | grep -v "# \"File List\"" > $tmpfile
cd $dirname
grep -v _USER_ $tmpfile | while read fichier;
do
  if [ -r "$fichier" ];
  then
    mkdir -p "./$(dirname $fichier)" 2> /dev/null
    cp -r "$fichier" "./$fichier" 2> /dev/null
  fi
done
if [ $UID != 0 ]; then
  echo ' !! You must be root to save the configuration of the users on the system !!'
  makebackup
  exit 2
fi
awk -F: '{if ($3 >= 500) print $6}' /etc/passwd | while read homedir;
do
  grep _USER_ $tmpfile | while read fichier;
  do
    realpath=$(echo $fichier | sed "s#/_USER_#$homedir#g")
    if [ -r "$realpath" ];
    then
      mkdir -p "./$(dirname $realpath)" 2> /dev/null
      cp -r "$realpath" "./$realpath" 2> /dev/null
    fi
  done
done
makebackup
exit
# "File List"
/etc/apache
/etc/apache2
/etc/crontab
/etc/DIR_COLORS
/etc/esd.conf
/etc/exports
/etc/fonts/fonts.conf
/etc/fstab
/etc/ftpusers
/etc/group
/etc/HOSTNAME
/etc/inputrc
/etc/lilo.conf
/etc/modules.conf
/etc/my.cnf
/etc/networks
/etc/network
/etc/ppp
/etc/profile
/etc/profile.d
/etc/rc.d
/etc/resolv.conf
/etc/ssh
/etc/sudoers
/etc/swaret.conf
/etc/syslog.conf
/etv/vim/vimrc
/etc/X11/XF86Config
/etc/X11/xinit/xinitrc
/etc/X11/xorg.conf
/usr/share/vim/vimrc
/_USER_/.bashrc
/_USER_/.bash_profile
/_USER_/.blackbox
/_USER_/.bmp
/_USER_/.config
/_USER_/.fluxbox
/_USER_/.gaim
/_USER_/.gnupg
/_USER_/.liferea/feedlist.opml
/_USER_/.opera/bookmarks.adr
/_USER_/.opera/contacts.adr
/_USER_/.opera/filter.ini
/_USER_/.opera/opera6.ini
/_USER_/.opera/search.ini
/_USER_/.profile
/_USER_/.ssh
/_USER_/.torsmorc
/_USER_/.xmms
