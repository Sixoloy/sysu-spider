from distutils.core import setup
import py2exe

setup(
    windows=['elect_graph.py'],
    options = { 
               "py2exe":
                { 
                 "includes":[
                            "numpy.*"
                        ] 
            } 
        }  
)