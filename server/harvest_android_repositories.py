from __future__ import print_function
from past.builtins import xrange

from urlparse import urlparse
from Queue import Queue, Empty
from os import makedirs, getcwd
from multiprocessing import cpu_count
from urllib2 import urlopen, HTTPError
from threading import Thread, current_thread
import xml.etree.ElementTree as element_tree
from os.path import dirname, join, realpath, exists, basename

script_directory = dirname(realpath(__file__))

__root_repo__ = "http://dl.google.com/android/repository/"
__sub_repos__ = [
"repository2-1.xml",
"sys-img/android/sys-img2-1.xml",
"sys-img/android-tv/sys-img2-1.xml",
"sys-img/android-wear/sys-img2-1.xml",
"glass/addon2-1.xml",
"sys-img/google_apis/sys-img2-1.xml",
"addon.xml"
"addon2-1.xml",
"extras/intel/addons2-1.xml",
]

def download_resource(url):
    uri = urlparse(url)
    print("\t{0}: Downloading: {1}".format(current_thread().name, uri.path))

    target_directory = realpath(getcwd()) + dirname(uri.path)
    if not exists(target_directory):
        try:
            makedirs(target_directory)
        except:
            pass

    try:
        response = urlopen(url)
        resource_contents = response.read()

        resource_file = open(join(target_directory, basename(uri.path)), "wb")
        resource_file.write(resource_contents)
        resource_file.close()
    except HTTPError, e:
        if e.getcode() != 404:
            raise
        else:
            print("\t\t{0}: {1} is no longer available".format(current_thread().name, url))

def download_daemon(queue):
    while True:
        try:
            url = queue.get_nowait()
            download_resource(url)
        except Empty:
            # Nothing left to process exit thread
            return
        else:
            queue.task_done()

if __name__ == "__main__":
    download_queue = Queue()

    for sub_repo_uri in __sub_repos__:
        repo_uri = join(__root_repo__, sub_repo_uri)
        print("Parsing {0}".format(repo_uri))

        try:
            response = urlopen(repo_uri)
            repo_xml = response.read()

            root = element_tree.fromstring(repo_xml)

            for url in root.iter("url"):
                download_queue.put(join(dirname(repo_uri), url.text.strip()))

            for url in root.iter("sdk:url"):
                download_queue.put(url.text.strip())

        except HTTPError, e:
            if e.getcode() != 404:
                raise
            else:
                print("\t{0} is no longer available".format(repo_uri))
        except:
            from traceback import format_exc
            print(format_exc())


    print("{0} has {1} packages available".format(__root_repo__, download_queue.qsize()))

    # Start the works
    workers = [ Thread(target=download_daemon, args=(download_queue,)) for count in xrange(cpu_count()) ]

    print("Worker threads starting")
    map(lambda x:x.start(), workers)

    map(lambda x:x.join(), workers)
    print("Worker threads exited")
