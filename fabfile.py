import urllib
import BeautifulSoup
from contextlib import nested
from fabric.api import *
from unipath import FSPath as Path

API_LANDING_PAGE = 'http://www.evernote.com/about/developer/api/'
API_LINK_TITLE = 'Evernote API'
BASE_PATH = Path(__file__).absolute().parent

def prep_sdist():
    """
    Build a sdist from the latest Evernote Python API wrappers.
    """
    landing_page = BeautifulSoup.BeautifulSoup(urllib.urlopen(API_LANDING_PAGE))
    api_link = landing_page.find('a', text=API_LINK_TITLE).parent['href']
    api_zip_name = Path(api_link).name
    api_zip_dest = BASE_PATH.child(api_zip_name)

    if not api_zip_dest.exists():
        local('curl -O "%s"' % api_link)
        
    unziped_dir = BASE_PATH.child(api_zip_name.stem)
    if not unziped_dir.exists():
        local('unzip %s' % api_zip_name)
    
    local('cp -r -f %s/lib/python src' % unziped_dir)
    
    with nested(open('setup.py.in'), open('setup.py', 'w')) as (fin, fout):
        fout.write(fin.read() % {'version': api_zip_name.stem.split('-')[-1]})
            
def clean():
    """
    Clean up any leftovers.
    """
    local('rm -rf dist src evernote* setup.py')
    
def upload():
    """
    Push a tarball to PyPI.
    """
    prep_sdist()
    local('python setup.py register sdist upload')