Photo Mover
===========

Photo Mover is a script to operate photos, that have time and date in their
Exif metadata. This script can copy or move photos from a source to a destination and sort them by date.


Using
-----

The script has the following three modes:

 - dry-run mode;
 - copy mode;
 - move mode.

The `dry-run` mode can be used to check what the script will do with photos.

The `copy` mode can be used, when the source photos shouldn't be moved from a source directory to a target directory.

The `move` mode can be used, when the source photos should be moved from a source directory to a target directory.


Examples
--------

### Dry-run mode

```
your_server:$ ./photo_move.py dry-run -s /path/to/directory/with/photos -d /path/to/destination
```

### Move photos

```
your_server:$ ./photo_move.py move -s /path/to/directory/with/photos -d /path/to/destination
```

### Copy photos

```
your_server:$ ./photo_move.py copy -s /path/to/directory/with/photos -d /path/to/destination
```


License
-------
Apache License 2.0
