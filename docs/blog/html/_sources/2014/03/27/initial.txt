Menes PDF
============================

menes is a web application which generates a PDF from your Sphinx
project.

You never need to install a tex environment!

How to Use
----------------

At first, install the sphinx extension via pip,

::

  % pip install sphinxcontrib-menesbuilder

And add two lines to your conf.py.

.. code-block:: python

   extensions = ['sphinxcontrib.menesbuilder']
   menes_email = "your_mailaddress@example.com"

Then, type this!

::

  % cd <path to top of your sphinx project>
  % sphinx-build -b menesbuilder source .

After while, you receive e-mail which includes PDF download URL.

Very easty to generate Sphinx beautiful PDF.


.. author:: default
.. categories:: none
.. tags:: none
.. comments::
