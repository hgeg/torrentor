#!/bin/bash
echo ""
echo "      Welcome to Torrentor.v2 installer      "
echo "---------------------------------------------"
echo "Current version: 2.0.2b"
echo "Released on 13.12.2013"
echo ""

echo ""
echo "Installing dependencies..."
echo "rtorrent, pip, screen, redis, omxplayer, nginx, spawn, flup, feh...:"
sudo apt-get install rtorrent python-pip screen omxplayer redis-server nginx feh spawn-fcgi python-flup
echo "python/web.py:"
sudo pip install web.py
echo "python/redis:"
sudo pip install redis
echo "python/requests:"
sudo pip install requests
echo "python/xmlrpclib:"
sudo pip install xmlrpclib
echo "python/periscope:"
sudo pip install periscope
echo "python/bs4"
sudo pip install BeautifulSoup

echo ""
echo "Finished. Now setting up config files..."
python config.py $1 $2 $3
mv .rtorrent.rc $HOME/.rtorrent.rc

echo ""
echo "Finished. Setting autostart on boot"
chmod +x torrentor-stack
sudo mv torrentor-stack /etc/init.d/torrentor-stack
sudo update-rc.d torrentor-stack defaults 100

echo ""
echo "Finished. Running services..."
./runapps.sh

#echo ""
#echo "cleaning up..."
#rm runapps.sh
#rm config.py
#rm README.md
#rm -- "$0"

echo ""
echo "---------------------------------------------"
echo "Installation finished."
echo "For more info: hgeg.io/app/torrentor"
