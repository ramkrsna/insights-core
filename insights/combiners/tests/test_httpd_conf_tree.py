from insights.parsr.query import first, last  # noqa: F401
from insights.combiners.httpd_conf import _HttpdConf, HttpdConfTree
from insights.tests import context_wrap
from insights.parsers import SkipException
import pytest


HTTPD_CONF_MIXED = '''
JustFotTest_NoSec "/var/www/cgi"
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
ThreadsPerChild  16
JustForTest      "AB"
MaxClients       256
</IfMoDuLe>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_CONTINUATION = r'''
JustFotTest_NoSec "/var/www/cgi"
CustomLog logs/ssl_request_log \
"%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x \"%r\" %b"
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
ThreadsPerChild  16
JustForTest      "AB"
MaxClients       256
</IfModule>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_1 = '''
JustFotTest_NoSec "/var/www/cgi"
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
ThreadsPerChild  16
JustForTest      "AB"
MaxClients       256
</IfModule>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_2 = '''
JustForTest_NoSec "/var/www/cgi"
# prefork MPM
<IfModule prefork.c>
ServerLimit      1024
JustForTest      "ABC"
MaxClients       1024
</IfModule>
'''.strip()

HTTPD_CONF_3 = '''
# prefork MPM
<IfModule prefork.c>
ServerLimit      256
MaxClients       512
</IfModule>
'''.strip()

HTTPD_CONF_SHADOWTEST_1 = '''
Foo 1A
Foo 1B
Foo 1C
<IfModule prefork.c>
Foo 1xA
Foo 1xB
Foo 1xC
Bar 1A
Bar 1B
Bar 1C
</IfModule>

IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_SHADOWTEST_2 = '''
Foo 2A
Foo 2B
Foo 2C
<IfModule ASDF.prefork.c.ASDF>
Foo 2xA
Foo 2xB
Foo 2xC
Bar 2A
Bar 2B
Bar 2C
</IfModule>
'''.strip()

HTTPD_CONF_SHADOWTEST_3 = '''
Foo 3A
Foo 3B
Foo 3C
<IfModule prefork.c>
Foo 3xA
Foo 3xB
Foo 3xC
Bar 3A
Bar 3B
Bar 3C
</IfModule>
'''.strip()

HTTPD_CONF_MAIN_1 = '''
ServerRoot "/etc/httpd"
Listen 80

# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf
'''.strip()

HTTPD_CONF_MAIN_2 = '''
# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf

ServerRoot "/etc/httpd"
Listen 80
'''.strip()

HTTPD_CONF_MAIN_3 = '''
ServerRoot "/etc/httpd"

# Load config files in the "/etc/httpd/conf.d" directory, if any.
IncludeOptional conf.d/*.conf

Listen 80
'''.strip()

HTTPD_CONF_FILE_1 = '''
ServerRoot "/home/skontar/httpd"
Listen 8080
'''.strip()

HTTPD_CONF_FILE_2 = '''
ServerRoot "/home/skontar/www"
'''.strip()

HTTPD_CONF_MORE = '''
UserDir disable
UserDir enable bob
'''.strip()

HTTPD_EMPTY_LAST = '''
#
# Directives controlling the display of server-generated directory listings.
#
# Required modules: mod_authz_core, mod_authz_host,
#                   mod_autoindex, mod_alias
#
# To see the listing of a directory, the Options directive for the
# directory must include "Indexes", and the directory must not contain
# a file matching those listed in the DirectoryIndex directive.
#

#
# IndexOptions: Controls the appearance of server-generated directory
# listings.
#
IndexOptions FancyIndexing HTMLTable VersionSort

# We include the /icons/ alias for FancyIndexed directory listings.  If
# you do not use FancyIndexing, you may comment this out.
#
Alias /icons/ "/usr/share/httpd/icons/"

<Directory "/usr/share/httpd/icons">
    Options Indexes MultiViews FollowSymlinks
    AllowOverride None
    Require all granted
</Directory>

#
# AddIcon* directives tell the server which icon to show for different
# files or filename extensions.  These are only displayed for
# FancyIndexed directories.
#
AddIconByEncoding (CMP,/icons/compressed.gif) x-compress x-gzip

AddIconByType (TXT,/icons/text.gif) text/*
AddIconByType (IMG,/icons/image2.gif) image/*
AddIconByType (SND,/icons/sound2.gif) audio/*
AddIconByType (VID,/icons/movie.gif) video/*

AddIcon /icons/binary.gif .bin .exe
AddIcon /icons/binhex.gif .hqx
AddIcon /icons/tar.gif .tar
AddIcon /icons/world2.gif .wrl .wrl.gz .vrml .vrm .iv
AddIcon /icons/compressed.gif .Z .z .tgz .gz .zip
AddIcon /icons/a.gif .ps .ai .eps
AddIcon /icons/layout.gif .html .shtml .htm .pdf
AddIcon /icons/text.gif .txt
AddIcon /icons/c.gif .c
AddIcon /icons/p.gif .pl .py
AddIcon /icons/f.gif .for
AddIcon /icons/dvi.gif .dvi
AddIcon /icons/uuencoded.gif .uu
AddIcon /icons/script.gif .conf .sh .shar .csh .ksh .tcl
AddIcon /icons/tex.gif .tex
AddIcon /icons/bomb.gif core.

AddIcon /icons/back.gif ..
AddIcon /icons/hand.right.gif README
AddIcon /icons/folder.gif ^^DIRECTORY^^
AddIcon /icons/blank.gif ^^BLANKICON^^

#
# DefaultIcon is which icon to show for files which do not have an icon
# explicitly set.
#
DefaultIcon /icons/unknown.gif

#
# AddDescription allows you to place a short description after a file in
# server-generated indexes.  These are only displayed for FancyIndexed
# directories.
# Format: AddDescription "description" filename
#
#AddDescription "GZIP compressed document" .gz
#AddDescription "tar archive" .tar
#AddDescription "GZIP compressed tar archive" .tgz

#
# ReadmeName is the name of the README file the server will look for by
# default, and append to directory listings.
#
# HeaderName is the name of a file which should be prepended to
# directory indexes.
ReadmeName README.html
HeaderName HEADER.html

#
# IndexIgnore is a set of filenames which directory indexing should ignore
# and not include in the listing.  Shell-style wildcarding is permitted.
#
IndexIgnore .??* *~ *# HEADER* README* RCS CVS *,v *,t

'''.lstrip()


HTTPD_CONF_NEST_1 = """
<VirtualHost 128.39.140.28>
    <Directory /var/www/example>
        Options FollowSymLinks
        AllowOverride None
    </Directory>
    <IfModule mod_php4.c>
        php_admin_flag safe_mode Off
        php_admin_value register_globals    0
    </IfModule>
    DirectoryIndex index.php
    <IfModule mod_rewrite.c>
        RewriteEngine On
        RewriteRule .* /index.php
    </IfModule>
    <IfModule mod_rewrite.c>
        RewriteEngine Off
    </IfModule>
    <IfModule !php5_module>
        <IfModule !php4_module>
            <FilesMatch ".php[45]?$">
                Order allow,deny
                Deny from all
            </FilesMatch>
            <FilesMatch ".php[45]?$">
                Order deny,allow
            </FilesMatch>
        </IfModule>
    </IfModule>
    DocumentRoot /var/www/example
    ServerName www.example.com
    ServerAlias admin.example.com
</VirtualHost>
<IfModule !php5_module>
  <IfModule !php4_module>
    <Location />
        <FilesMatch ".php[45]">
            Order allow,deny
            Deny from all
        </FilesMatch>
    </Location>
  </IfModule>
</IfModule>
<IfModule mod_rewrite.c>
    RewriteEngine Off
</IfModule>
LogLevel warn
DocumentRoot "/var/www/html_cgi"
IncludeOptional conf.d/*.conf
EnableSendfile on
""".strip()

HTTPD_CONF_NEST_2 = """
DocumentRoot "/var/www/html"
<VirtualHost 128.39.140.30>
    <IfModule !php5_module>
        <IfModule !php4_module>
            <FilesMatch ".php[45]?$">
                Order allow,deny
                Deny from all
            </FilesMatch>
            <FilesMatch ".php[45]?$">
                Order deny,allow
            </FilesMatch>
        </IfModule>
    </IfModule>
    DocumentRoot /var/www/example1
    ServerName www.example1.com
    ServerAlias admin.example1.com
</VirtualHost>
<IfModule !php5_module>
  <IfModule !php4_module>
    <Location />
        <FilesMatch test>
            Order deny,allow
            Allow from all
        </FilesMatch>
        <FilesMatch ".php[45]">
            Order deny,allow
        </FilesMatch>
    </Location>
  </IfModule>
</IfModule>
<IfModule mod_rewrite.c>
    RewriteEngine On
</IfModule>
EnableSendfile off
""".strip()

HTTPD_CONF_NEST_3 = """
<VirtualHost 128.39.140.28>
    <IfModule !php5_module>
        Testphp php5_v3_1
        <IfModule !php4_module>
            Testphp php4_v3_1
        </IfModule>
        Testphp php5_v3_2
    </IfModule>
</VirtualHost>
<IfModule !php5_module>
  Testphp php5_3_a
  <IfModule !php4_module>
    Testphp php4_3_a
  </IfModule>
</IfModule>
""".strip()

HTTPD_CONF_NEST_4 = """
<VirtualHost 128.39.140.30>
    <IfModule !php5_module>
        Testphp php5_v4_1
        <IfModule !php4_module>
            Testphp php4_v4_1
        </IfModule>
        Testphp php5_v4_2
    </IfModule>
</VirtualHost>
<IfModule !php5_module>
  Testphp php5_4_b
  <IfModule !php4_module>
    Testphp php4_4_b
  </IfModule>
</IfModule>
""".strip()


def test_mixed_case_tags():
    httpd = _HttpdConf(context_wrap(HTTPD_CONF_MIXED, path='/etc/httpd/conf/httpd.conf'))
    assert httpd.find("ServerLimit").value == 256


def test_line_continuation():
    httpd = _HttpdConf(context_wrap(HTTPD_CONF_CONTINUATION, path='/etc/httpd/conf/httpd.conf'))
    val = httpd.find("CustomLog")[0].attrs
    assert val == [r'logs/ssl_request_log', r'%t %h %{SSL_PROTOCOL}x %{SSL_CIPHER}x "%r" %b'], val


def test_nopath():
    # no path
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2))
    try:
        result = HttpdConfTree([httpd2])
        # assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024
        exception_happened = False
    except:
        exception_happened = True
    assert exception_happened

    # no httpd.conf
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    try:
        result = HttpdConfTree([httpd2])
        # assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024
        exception_happened = False
    except:
        exception_happened = True
    assert exception_happened

    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfTree([httpd2])
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/laaalalalala/blablabla/httpd.conf'))
    result = HttpdConfTree([httpd2])
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # no include in httpd.conf
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf/httpd.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/z-z.conf'))
    result = HttpdConfTree([httpd2, httpd3])
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # no include in httpd.conf
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf/httpd.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/aaa.conf'))
    result = HttpdConfTree([httpd3, httpd2])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 1
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 1024
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # with an include
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfTree([httpd1, httpd2])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 2
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 256
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 1024

    # colliding filenames
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/00-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])
    assert len(result['IfModule', 'prefork.c']['ServerLimit']) == 3
    assert result['IfModule', 'prefork.c']['ServerLimit'][first].value == 256  # httpd1
    assert result['IfModule', 'prefork.c']['ServerLimit'][1].value == 1024     # httpd2
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 256   # httpd3
    assert len(result['IfModule', 'prefork.c']['MaxClients']) == 3
    assert result['IfModule', 'prefork.c']['MaxClients'][first].value == 256  # httpd1
    assert result['IfModule', 'prefork.c']['MaxClients'][1].value == 1024     # httpd2
    assert result['IfModule', 'prefork.c']['MaxClients'][last].value == 512   # httpd3

    # testing other ways to access the same indices
    assert result['IfModule', 'prefork.c']['MaxClients'][0].value == 256   # httpd1
    assert result['IfModule', 'prefork.c']['MaxClients'][2].value == 512   # httpd3
    assert result['IfModule', 'prefork.c']['MaxClients'][-1].value == 512  # httpd3


def test_active_httpd():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_3, path='/etc/httpd/conf.d/z-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    assert result['IfModule', 'prefork.c']['MaxClients'][last].value == 512
    assert result['IfModule', 'prefork.c']['MaxClients'][last].file_path == '/etc/httpd/conf.d/z-z.conf'
    assert result['IfModule', 'prefork.c']['ThreadsPerChild'][last].value == 16
    assert result['IfModule', 'prefork.c']['ServerLimit'][last].value == 256
    assert result['IfModule', 'prefork.c']['JustForTest'][last].file_name == '00-z.conf'
    assert result['JustForTest_NoSec'][first].line == 'JustForTest_NoSec "/var/www/cgi"'


def test_shadowing():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_2, path='/etc/httpd/conf.d/00-z.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_SHADOWTEST_3, path='/etc/httpd/conf.d/z-z.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    assert len(result["Foo"]) == 9
    assert len(result["IfModule"]) == 3
    assert len(result["IfModule"]["Foo"]) == 9
    assert len(result["IfModule"]["Bar"]) == 9
    assert len(result["IfModule", "prefork.c"]) == 2
    assert len(result["IfModule", "prefork.c"]["Foo"]) == 6
    assert len(result["IfModule", "prefork.c"]["Bar"]) == 6
    assert len(result["IfModule", "prefork.c"][0]["Foo"]) == 3
    assert len(result["IfModule", "prefork.c"][1]["Foo"]) == 3
    assert len(result["IfModule", "prefork.c"][0]["Bar"]) == 3
    assert len(result["IfModule", "prefork.c"][1]["Bar"]) == 3


def test_splits():
    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_MAIN_1, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    server_root = result['ServerRoot'][last]
    assert server_root.value == '/home/skontar/www'
    assert server_root.line == 'ServerRoot "/home/skontar/www"'
    assert server_root.file_name == '01-b.conf'
    assert server_root.file_path == '/etc/httpd/conf.d/01-b.conf'

    listen = result["Listen"][last]
    assert listen.value == 8080
    assert listen.line == 'Listen 8080'
    assert listen.file_name == '00-a.conf'
    assert listen.file_path == '/etc/httpd/conf.d/00-a.conf'

    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_MAIN_2, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    server_root = result['ServerRoot'][last]
    assert server_root.value == '/etc/httpd'
    assert server_root.line == 'ServerRoot "/etc/httpd"'
    assert server_root.file_name == 'httpd.conf'
    assert server_root.file_path == '/etc/httpd/conf/httpd.conf'

    listen = result["Listen"][last]
    assert listen.value == 80
    assert listen.line == 'Listen 80'
    assert listen.file_name == 'httpd.conf'
    assert listen.file_path == '/etc/httpd/conf/httpd.conf'

    httpd1 = _HttpdConf(context_wrap(HTTPD_CONF_MAIN_3, path='/etc/httpd/conf/httpd.conf'))
    httpd2 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_1, path='/etc/httpd/conf.d/00-a.conf'))
    httpd3 = _HttpdConf(context_wrap(HTTPD_CONF_FILE_2, path='/etc/httpd/conf.d/01-b.conf'))
    result = HttpdConfTree([httpd1, httpd2, httpd3])

    server_root = result['ServerRoot'][last]
    assert server_root.value == '/home/skontar/www'
    assert server_root.line == 'ServerRoot "/home/skontar/www"'
    assert server_root.file_name == '01-b.conf'
    assert server_root.file_path == '/etc/httpd/conf.d/01-b.conf'
    assert listen.value == 80
    assert listen.line == 'Listen 80'
    assert listen.file_name == 'httpd.conf'
    assert listen.file_path == '/etc/httpd/conf/httpd.conf'


def test_httpd_one_file_overwrites():
    httpd = _HttpdConf(context_wrap(HTTPD_CONF_MORE, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfTree([httpd])

    active_setting = result['UserDir'][last]
    assert active_setting.value == 'enable bob'
    assert active_setting.file_path == '/etc/httpd/conf/httpd.conf'
    assert active_setting.file_name == 'httpd.conf'
    assert active_setting.line == 'UserDir enable bob', active_setting.line

    setting_list = result['UserDir']
    assert len(setting_list) == 2
    assert setting_list[0].value == 'disable'
    assert setting_list[0].line == 'UserDir disable'
    assert setting_list[0].file_path == '/etc/httpd/conf/httpd.conf'
    assert setting_list[0].file_name == 'httpd.conf'
    assert setting_list[0].section is None
    assert setting_list[1].value == 'enable bob'
    assert setting_list[1].line == 'UserDir enable bob'
    assert setting_list[1].file_path == '/etc/httpd/conf/httpd.conf'
    assert setting_list[1].file_name == 'httpd.conf'
    assert setting_list[1].section_name is None


def test_httpd_conf_empty():
    with pytest.raises(SkipException):
        assert _HttpdConf(context_wrap('', path='/etc/httpd/httpd.conf')) is None


def test_empty_last_line():
    httpd = _HttpdConf(context_wrap(HTTPD_EMPTY_LAST, path='/etc/httpd/conf/httpd.conf'))
    result = HttpdConfTree([httpd])

    index_options = result['IndexOptions'][last]
    assert index_options.value == 'FancyIndexing HTMLTable VersionSort'
