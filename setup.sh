echo "      Welcome to Torrentor.v2 installer      "
echo "---------------------------------------------"
echo ""
echo "Installing dependencies..."
echo ""

./install_prereq.sh

echo "Finished. Now setting up config files..."
python config.py $1 $2 
mv .rtorrent.rc $HOME/.rtorrent.rc

echo ""
echo "Finished. Running services..."
./runapps.sh

echo ""
echo "cleaning up..."
rm install_prereq.sh 
rm runapps.sh
rm config.py
rm -- "$0"

echo ""
echo "---------------------------------------------"
echo "Installation finished."
echo "For more info: hgeg.io/app/torrentor"
