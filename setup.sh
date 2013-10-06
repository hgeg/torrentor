echo "      Welcome to Torrentor.v2 installer      "
echo "---------------------------------------------"
echo "Trying to install prerequisites       "
echo ""
sudo ./install_prereq.sh
echo "Finished. Now setting up config files...   "
echo ""
cp rtorrent.rc ~/.rtorrent.rc
python config.py "$1"
echo "Finished. Running services...        "
echo "Finished. If you haven't done already,"
echo "update your server settings for fcgi handling."
echo ""
./runapps.sh
echo ""
echo "---------------------------------------------"
echo "For more info: gitub.com/hgeg/torrentor   "
