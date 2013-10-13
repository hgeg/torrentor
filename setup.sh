echo "      Welcome to Torrentor.v2 installer      "
echo "---------------------------------------------"
echo "Trying to install prerequisites"
echo ""

./install_prereq.sh
echo "Finished. Now setting up config files..."
echo ""
python config.py $1 $2 
mv .rtorrent.rc $HOME/.rtorrent.rc
echo "Finished. Running services..."
echo ""
./runapps.sh
echo ""
echo "---------------------------------------------"
echo "For more info: gitub.com/hgeg/torrentor"
