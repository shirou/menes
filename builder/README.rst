Menes builder
==================

menesubuilder is an sphinx extension which can use menes PDF generates web service.

Hob to install
--------------------

::

  % pip install sphinxcontrib-menesbuilder

How to Use
--------------

1. add these to conf.py

   ::

      menes_email = "your_mailaddress@example.com"

   If you want to use your own menes server, set like this.

   ::

      menes_url = "http://your.menes.eample.com/menes/root"

   Default serverside command is "make latexpdf" but if you want to
   run "make latexpdfja", set menes_command.

   ::

      menes_command = "latexpdfja"

2. build using menesbuilder

   ::

      % sphinx-build -b menesbuilder -d _build/doctrees . .

      or if you separete source dire,

      % sphinx-build -b menesbuilder source .

   where first "." is source dir and last "." specify where is the
   root directory.

3. wait.

4. you will receive an email which includes PDF link

   notice: PDF will be deleted shortely about 1 week.

5. if build failed, the fail log will be emailed.


License
----------

New BSD

