sudo killall rtorrent
sudo killall core.py
echo "creating directiories"
mkdir <DATA_DIR>/downloads
#mkdir <DATA_DIR>/finished
mkdir <DATA_DIR>/media
mkdir <SITE_DIR>/session
mkdir <SITE_DIR>/torrents
echo "kill previous processes"
sudo kill `pgrep -f rtorrent` 
sudo kill `pgrep -f core.py` 
echo "running rtorrent"
screen -S rtorrent  -d -m rtorrent
echo "running web layer"
sudo screen -S torrentor  -d -m ./core.py 
