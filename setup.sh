echo "      Welcome to Torrentor.v2 installer      "
echo "---------------------------------------------"
echo "       Trying to install prerequisites       "
sudo ./install_prereq.sh
echo "  Finished. Now setting up config files...   "
touch ~/.rtorrent.rc
python config.py
echo "        Finished. Running services...        "
echo "Finished. If you haven't done already, update"
./runapps.sh
echo "   your server settings for fcgi handling.   "
echo ""
echo "---------------------------------------------"
echo "   For more info: gitub.com/hgeg/torrentor   "
