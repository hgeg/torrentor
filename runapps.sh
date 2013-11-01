echo "creating directiories"
mkdir <DATA_DIR>/downloads
#media conversion dirs
#will add later
#mkdir <DATA_DIR>/converting
#mkdir <DATA_DIR>/finished
mkdir <DATA_DIR>/media
mkdir <SITE_DIR>/session
mkdir <SITE_DIR>/torrents
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
if [ -f torrentor.conf]
then                                                                                                                                                                             
  echo "setting up scgi upstream"
  sudo mv torretor.conf /etc/nginx/sites-enabled/torrentor.conf
  sudo service nginx restart
fi
echo "initialize data"
scripts/action.py --init 
