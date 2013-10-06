echo "running rtorrent"
screen -dmS rtorrent  rtorrent
echo "running web layer"
screen -dmS torrentor spawn-fcgi -d <BASE_DIR> -f <BASE_DIR>/core.py -a 127.0.0.1 -p $1
