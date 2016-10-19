Updatify
========

Reference implementation of my auto-updater solution.

TODO
----

* Sometimes, empty folders are not removed, because they are only checked for emptyness when a FILE is removed. But sometimes a FOLDER is the last thing to be removed from them, so that check never happens when it's actually empty
* Selection of latest version using a file on the server
