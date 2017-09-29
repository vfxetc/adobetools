import argparse
import errno
import os
import subprocess


def install_via_link(path, name=None):

    csxs = os.path.join(path, 'csxs', 'manifest.xml')
    if not os.path.exists(csxs):
        raise ValueError('Panel does not contain manifest.xml', path)
    
    ext_root = os.path.expanduser('~/Library/Application Support/Adobe/CEP/extensions')
    try:
        os.makedirs(ext_root)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

    name = name or os.path.basename(path)
    link_path = os.path.join(ext_root, name)

    try:
        os.unlink(link_path)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise
    os.symlink(path, link_path)


def assert_debug_mode(verbose=False):


    # Note that Premiere 2017 is currently sitting at CSXS 6.
    for v in xrange(5, 8):
        subprocess.check_call(['defaults', 'write', 'com.adobe.CSXS.{}'.format(v), 'PlayerDebugMode', '1'])
        # See: https://github.com/Adobe-CEP/CEP-Resources/wiki/CEP-6-HTML-Extension-Cookbook-for-CC-2015#where-are-the-log-files
        # Logs go to ~/Library/Logs/CSXS
        subprocess.check_call(['defaults', 'write', 'com.adobe.CSXS.{}'.format(v), 'LogLevel', '4' if verbose else '1'])
    
    # Need to force macOS to recache.
    subprocess.check_call(['killall', '-u', os.getlogin(), 'cfprefsd'])


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-n', '--name')
    parser.add_argument('path')
    args = parser.parse_args()

    print 'Linking in CEP extension.'
    install_via_link(args.path, name=args.name)

    print 'Asserting debug mode.'
    assert_debug_mode(args.debug)


if __name__ == '__main__':
    main()
