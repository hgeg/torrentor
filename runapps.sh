echo "creating directiories"
mkdir <DATA_DIR>/downloads
#media conversion dirs
#will add later
#mkdir <DATA_DIR>/converting
#mkdir <DATA_DIR>/finished
mkdir <DATA_DIR>/media
mkdir <SITE_DIR>/session
mkdir <SITE_DIR>/torrents
echo "kill previous processes"
ps ax | grep rtorrent | cut -c 1-5 | sudo xargs kill
ps ax | grep core.py | cut -c 1-5 | sudo xargs kill
echo "running rtorrent"
screen -S rtorrent  -d -m rtorrent
echo "running web layer"
sudo screen -S torrentor  -d -m ./core.py 
