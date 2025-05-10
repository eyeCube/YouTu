from distutils.core import setup
import py2exe

setup(
    console=[{'script': 'YouTu.py', 
              'icon_resources': [(1, 'ytdl.ico')]}],
    )
