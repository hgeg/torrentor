Torrentor.v2
============


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/hgeg/torrentor/trend.png)](https://bitdeli.com/free "Bitdeli Badge")


1. Description 
--------------

Torrentor.v2 is the lightweight, easy to install, and optimized version of classic torrentor, featuring brand new minimalistic interface. This version's focus is handling media files. It is designed to play movies and tv shows downloaded via torrent.

2. Installation
---------------
* Download Deployment script [from here](https://hgeg.io/misc/deploy) into the folder you want to install torrentor.

* open it with your favorite text editor, then change ```DATA_DIR``` variable to a desired path for your downloads. Normally this would be the root directory of your storage space(e.g. external harddisk).

* Make it executable by typing ``` chmod +x deploy ```

* And finally, run it: ```./deploy```. Deployment script will install all the requirements, project files and start the services. 

* After the installation finishes, you can access torrentor by typing ```http://<your_ip_address>:8092/torrentor``` in any browser.

3. How to use
-------------
Access to torrentor via url ```http://<your pi's local ip>:8092/torrentor``` from any device, this link will be provided at the end of installation process. On the web interface, you will see something like this:

![alt text](http://hgeg.io/misc/mainpage.png "Main Page")

You can add new torrents, search for media, and see the progress of your downloads by:

1. Progress Toggle: It opens a panel that shows your current downloads and "now playing" information
2. Omnibox: This is how you control the torrentor. With, omnibox you can:
    * Add new torrents by directly pasting the link (torrent or magnet)
    * Search for media in your downloads location. Therefore, a blank search (simply pressing return key) will list your whole library.
    * If above search returns no results, omnibox understands it and suggests the best matching torrent file in the internet as you type.

4. Issues
---------

Torrentor.v2 is quite new and naturally has some bugs & issues. Here are some of the known bugs and issues:

* There are several design issues on progress panel.
* Browser playback does not work on mobile devices.
* No support for displaying files other than video. (e.g. audio, text and images)
* File conversion is not added yet. 
* Needs subtitle support.

For the bugs you fount other than those, send your reports and/or to [me](mailto:alicanblbl@gmail.com).

Just triyng sth: rape rape rape rape rape rape rape rape rape
