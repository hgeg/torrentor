sudo killall rtorrent
sudo killall core.py
echo "creating directiories"
mkdir <BASE_DIR>/downloadas
mkdir <BASE_DIR>/session
mkdir <BASE_DIR>/torrents
mkdir <BASE_DIR>/finished
echo "running rtorrent"
screen -S rtorrent  -d -m rtorrent
echo "running web layer"
sudo screen -S torrentor  -d -m ./core.py 
