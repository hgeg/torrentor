#!/bin/bash
echo "creating directiories"
#media conversion dirs
#will add later
#mkdir <DATA_DIR>/converting
# spawn-fcgimkdir <DATA_DIR>/finished

echo "creating media folders"
if [ -d "<DATA_DIR>/downloads" ]
then
  echo "downloads directory exists."
else
  mkdir <DATA_DIR>/downloads
fi

if [ -d "<DATA_DIR>/media" ]
then
  echo "media directory exists."
else
  mkdir <DATA_DIR>/media
fi

echo "creating temp folders"
mkdir <SITE_DIR>/session
mkdir <SITE_DIR>/torrents

echo "linking media folder"
ln -s <DATA_DIR>/media static/media

sudo service torrentor-stack stop
sudo service torrentor-stack start

echo "running nginx" 
if [ -f torrentor.conf ]
then                                                                                                                                                                             
  echo "setting up fcgi upstream"
  sudo rm /etc/nginx/sites-enabled/default
  sudo mv torrentor.conf /etc/nginx/sites-enabled/torrentor.conf
  sudo service nginx restart
fi

echo "initialize data"
scripts/action.py --init 

echo "setting up welcome screen"
echo "on 0" | cec-client -s
xset -display :0 s reset
DISPLAY=:0 feh -F -X --hide-pointer -x -q --draw-tinted --info "python <SITE_DIR>/ip.py" -C /usr/share/fonts/truetype/ttf-dejavu/ -e DejaVuSans/36 -Z -D 5 -B black <SITE_DIR>/screen.png &

