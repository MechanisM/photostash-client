Photostash CLI Client
=====================

Command line interface to the http://photostash.herokuapp.com/ api.

**WARNING** this only works with Python 2.7 currently.


Installation::

  $ pip install photostash-client


Usage
-----

Creating a new album::

  $ stash create myalbum

  myalbum has been created.


Add a photo to a album::

  $ stash add myalbum ~/path.to.image.jpg

  1 has been added to myalbum.


Add a existing photo to a album::

  $ stash create myotheralbum
  $ stash add myotheralbum 1

  1 has been added to myotheralbum.


Listing photos in a album::

  $ stash list myalbum

  Photos: 12


Deleting a photo from a album::

  $ stash delete myalbum 1

  12 has been removed from myalbum.


Showing all albums and photos::

  $ stash stats

  -----------------------------------
  | Album     | Photos              |                                                                                                                                                                   
  -----------------------------------
  | myalbum       |                 |                                                                                                                                                                   
  | myotheralbum  | 1               |                                                                                                                                                                                                                                                                                                                                     
  -----------------------------------


Opening a photo::

  $ stash open 1

  Opening 1...
