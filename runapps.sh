echo "running rtorrent"
screen -S rtorrent  -d -m rtorrent
echo "running web layer"
spawn-fcgi -d <BASE_DIR> -f <BASE_DIR>/core.py -a 127.0.0.1 -p 9595
