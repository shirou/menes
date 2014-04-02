Sample settings
====================

oneside
--------------

If you do not want to insert empty page before chapter, specify oneside.

.. code-block:: python

   latex_elements = {
       'extraclassoptions': ',openany,oneside',
       }

blockdiag
------------

If you want to use blockdiag family, please specify correct font path.

.. code-block:: python

   blockdiag_fontpath = ["C:\Windows\Fonts\msmincho.ttc",
                         "/usr/share/fonts/truetype/mplus/mplus-2p-bold.ttf"]

Japanese
------------

.. code-block:: python

   menes_command = "latexpdfja"
   language = 'ja'
   latex_docclass = {'manual': 'jreport'}
   latex_elements = {
       'pointsize': '11pt',
       'papersize': 'a4paper',
       'transition': '',
       'extraclassoptions': ',openany,oneside',
       'babel': '\\usepackage[japanese]{babel}',
       }
