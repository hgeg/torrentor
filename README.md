Torrentor.v2
============

1. Description 
--------------

Torrentor.v2 is the lightweight, easily installed, and optimized version of classic torrentor. It has a minimal and brand new interface. This version's focus is handling media files. It is designed to play movies and tv shows downloaded via torrent.

2. Installation
---------------
* Download Deployment script [from here](https://hgeg.io/misc/deploy) into the folder you want to install torrentor.

* open it with your favorite text editor, then change ```DATA_DIR``` variable to a desired path for your downloads. Normally this would be the root directory of your storage space(e.g. external harddisk).

* Make it executable by typing ``` chmod +x deploy ```

* And finally, run it: ```./deploy```. Deployment script will install all the requirements, project files and start the services. 

* After the installation finishes, you can access torrentor by typing ```http://<your_ip_address>:8092/torrentor``` in any browser.

3. How to use
-------------
When you first enter the web interface, you will see something like this:
![alt text](http://hgeg.io/misc/mainpage.png "Main Page")

You can add new torrents, search for media, and see the progress of your downloads.
####Shaded areas are:

1. Progress Toggle: It opens a panel that shows your current downloads.
2. Omnibox: This is how you control the torrentor. With, omnibox you can:
    * Add new torrents by directly pasting the link (torrent or magnet)
    * Search for media in your downloads location.
    * If above search returns no results, omnibox understands it and suggests the best matching torrent file in the internet as you type.

4. Issues
---------

Torrentor.v2 is quite new and naturally has some bugs & issues. Also file conversion is not added yet. For any bugs reports and/or suggestions please send an email to [me](mailto:alicanblbl@gmail.com).
