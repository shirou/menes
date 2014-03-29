what's this?
==================

I want to make PDF using Sphinx at many time, but TeXLive environment
is so huge and complicated to install, especially Windows.

Menes is PDF generator from your sphinx project. By using menes, you
never need to install TeX environment.


Privacy concern
----------------------------

Menes code is open at `github <http:///github.com/shirou/menes>`_ and
I guarantee not to see your files.

The stored information are only

- your ipaddress
- email

But you may not believe. You can create your own menes server. set
your conf.py about

.. code-block:: python

   menes_url = "http://menes.example.com/your_menes_path/"
