find finished -iname "*.avi" -o -iname "*.mkv" -exec mv {} /Users/can/Documents/torrentor/converting/ \;
find finished -iname "*.mp4" -exec mv {} /Users/can/Documents/torrentor/static/media/ \;
for i in /*.avi; do 
  ffmpeg -i "<BASE_DIR>/converting/$i" -vcodec libx264 -b:v 1000k -ab 96k -ar 48k -f mp4 -strict experimental "<BASE_DIR>/static/media/$i"; 
done
