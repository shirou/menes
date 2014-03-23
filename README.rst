menes
=========

Menes is an web application which generates a PDF file from Sphinx builder. After PDF generated, menes send e-mail to the user and provide PDF download.

By using Menes, you don't need to build LaTeX environment on your desktop.


setup
-------

builder setup
++++++++++++++++++++++++

1. install builder

   ::

      % pip install sphinxcontrib-menesbuilder

2. add these to conf.py

   ::

      menes_email = "your_mailaddress@example.com"

   If you want to use your own menes server, set this(last "/apply" is
   required)

   ::

      menes_url = "http://your.menes.eample.com/menes/root/apply"

   Default serverside command is "make latexpdf" but if you want to
   run "make latexpdfja", set menes_command.

   ::

      menes_command = "latexpdfja"

3. build using menesbuilder

   ::

      % sphinx-build -b menesbuilder -d _build/doctrees . _build/html

3. wait.

4. you will receive an email which includes PDF link

   notice: PDF will be deleted shortely about 1 week.

5. if build failed, the fail log will be emailed.


web and worker setup
+++++++++++++++++++++++++++++

THIS IS NOT PROVIDED YET

You need an Amazon account to use SQS and SES.

1. git clone
2. cd menes/ansible
3. write your host to inventory.ini
4. run ansible-playbook

   ::

     % ansible-playbook -i inventory.ini menes_worker.yml


Architecture
--------------

1. Web application
2. worker
3. builder

::

  builder --HTTP POST--> Web --SQS-->
    worker --HTTP POST--> Web --SES--> You

Naming
--------

http://en.wikipedia.org/wiki/Menes

License
-----------------

2-clause BSD license
