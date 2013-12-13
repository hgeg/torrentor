echo ""
echo "      Welcome to Torrentor.v2 installer      "
echo "---------------------------------------------"
echo "Current version: 2.0.2b"
echo "Released on 11.12.13"
echo ""

echo ""
echo "Installing dependencies..."
./install_prereq.sh

echo ""
echo "Finished. Now setting up config files..."
python config.py $1 $2 
mv .rtorrent.rc $HOME/.rtorrent.rc

echo ""
echo "Finished. Setting autostart on boot"
chmod +x torrentor-service
sudo cp run.sh /etc/init.d/torrentor-service
update-rc.d torrentor-service defaults 100


echo ""
echo "Finished. Running services..."
./runapps.sh

echo ""
echo "cleaning up..."
rm install_prereq.sh 
rm runapps.sh
rm config.py
rm README.md
rm -- "$0"

echo ""
echo "---------------------------------------------"
echo "Installation finished."
echo "For more info: hgeg.io/app/torrentor"
