Torrentor
=========

Torrentor is a remote torrent client operates on your browser. It also provides an HTML5 media player with subtitle support
and it can convert videos to mp4 format.

### Installation:

#####1. Prerequsites
 
  - **rTorrent**:

      ``` apt-get install rtorrent ```

  - **screen**:

      ``` apt-get install screen ```

  - **apache (mod_wsgi, mod_scgi)**:

      ``` apt-get install apache2
          apt-get install libapache2-mod-wsgi
          apt-get install libapache2-mod-scgi````

  - **django**:
      install pip if you haven't already.

      ``` apt-get install python-pip```
      
      then django,
      
      ``` pip install django```
          
  - **ffmpeg**:
    this stage is optional. ffmpeg is required for video conversion.
    [Installation guide for ffmpeg and libx264](https://ffmpeg.org/trac/ffmpeg/wiki/UbuntuCompilationGuide)

#####2. Configuring Django:
  
  in the *django* directory:
  - Create two folders called *downloads* and *convert* anywhere in your computer. 
  - Open up the *settings.py* file and change the values of **DOWNLOADS_DIR** and **CONVERT_DIR** as the path to the folders you created.
  - type: 

  ``` python manage.py syncdb``` and say no to the prompt.

#####3. Configuration Files

  in the *config* directory:
  - in *httpd.conf* and *rtorrent.rc*, change the value of **DOWNLOADS_DIR** as above.
  - copy the **rtorrent.rc** file into your home directory as **.rtorrent.rc**
  - copy the **httpd.conf** and **ports.conf** into */etc/apache2/*
  
#####4. Initialize
  
  in the terminal, type:

    ``` screen rtorrent```
    
  when rtorrent initializes, press CTRL+A and CTRL+D to detach from the screen. Then restart the apache server:
  
  ``` service apache2 restart```
  
  if everything goes well, you can access torrentor with your browser.
  
  
--------------------------------------------------------------------------------------------------

The theme [Simplex](http://bootswatch.com/simplex/) provided by [Bootswatch](http://bootswatch.com/),
which is based on [Bootstrap](http://twitter.github.com/bootstrap/).

[Video.js](http://videojs.com) is a free HTML5 video player created and open-sourced by Steve Heffernan and [Zencoder Inc.](http://zencoder.com)
  
  
