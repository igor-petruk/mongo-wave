from distutils.core import setup
setup(name='mongowave',
    version='1.0',
    url="https://github.com/igor-petruk/mongo-wave",
    author='Igor Petruk',
    author_email='igor.petrouk@gmail.com',
    packages=['mongowave'],
    package_dir={'':'src'},
    package_data={'mongowave': ['data/*.glade']},
    scripts=['src/mongow']
)
