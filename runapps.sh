echo "creating directiories"
mkdir <DATA_DIR>/downloads
#media conversion dirs
#will add later
#mkdir <DATA_DIR>/converting
#mkdir <DATA_DIR>/finished

if [ -d "<DATA_DIR>/media" ]
then
  echo "media directory exists."
else
  mkdir <DATA_DIR>/media
fi

if [ -d "<DATA_DIR>/session" ]
then
  echo "session directory exists."
else
  mkdir <SITE_DIR>/session
fi

if [ -d "<DATA_DIR>/torrents" ]
then
  echo "torrents directory exists."
else
  mkdir <SITE_DIR>/torrents
fi

if [ ! -d static/media ]
then                                                                                                                                                                             
  echo "linking media folder"
  ln -s <DATA_DIR>/media static/media
fi

echo "kill previous processes"
ps ax | grep redis-server | cut -c 1-5 | sudo xargs kill
ps ax | grep rtorrent | cut -c 1-5 | sudo xargs kill
ps ax | grep core.py | cut -c 1-5 | sudo xargs kill

echo "running redis"
screen -S redis  -d -m redis-server
echo "running rtorrent"
screen -S rtorrent  -d -m rtorrent
echo "running web layer"
sudo screen -S torrentor  -d -m ./core.py 
echo "running nginx" 
if [ -f torrentor.conf ]
then                                                                                                                                                                             
  echo "setting up scgi upstream"
  sudo rm /etc/nginx/sites-enabled/default
  sudo mv torrentor.conf /etc/nginx/sites-enabled/torrentor.conf
  sudo service nginx restart
fi

echo "initialize data"
scripts/action.py --init 
