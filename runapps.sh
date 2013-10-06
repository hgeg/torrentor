sudo killall rtorrent
sudo killall core.py`
echo "running rtorrent"
screen -S rtorrent  -d -m rtorrent
echo "running web layer"
screen -S torrentor  -d -m ./core.py 
