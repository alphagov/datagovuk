"""
WSGI config for data.gov.uk project.

This module contains the WSGI application used by Django's development server
and any production WSGI deployments. It should expose a module-level variable
named ``application``. Django's ``runserver`` and ``runfcgi`` commands discover
this application via the ``WSGI_APPLICATION`` setting.

Usually you will have the standard Django WSGI application here, but it also
might make sense to replace the whole Django WSGI application with a custom one
that later delegates to the Django one. For example, you could introduce WSGI
middleware here, or combine a Django application with an application of another
framework.

"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# This allows easy placement of apps within the interior
# datagovuk directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "datagovuk"))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
application = get_wsgi_application()

# The following monkeypatching is necessary for DSIT developer laptops which
# use zscaler.
#
# zscaler acts as a middle-man for internet-bound https connections.  This means
# SSL connections made by the python app will need to be made with zscaler's
# root certificate.  The installation/use of the root certificate is handled for
# local copies by `just patch-zscaler-ssl` - however we also need to do some
# monkeypatching below.
#
# This is due to SSL security changes introduced in python3.13; https://discuss.python.org/t/python-3-13-x-ssl-security-changes/91266
# The changes introduced enhanced SSL certificate verification by setting the
# `ssl.VERIFY_X509_STRICT` flag.  Zscaler's certificate issued within DSIT does
# not adhere to that enhanced verification.
#
# The following monkeypatch ensures that we can use the python requests library
# on local copies running on DSIT laptops.  Otherwise we would get the following
# error when calling out to the internet;
#
# requests.exceptions.SSLError: HTTPSConnectionPool(host='www.google.com', port=443):
# Max retries exceeded with url:
# (Caused by SSLError(
#   SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED]
# certificate verify failed: Basic Constraints of CA cert not marked critical (_ssl.c:1028)')))
from django.conf import settings  # noqa: E402

if settings.MONKEYPATCH_ZSCALER_SSL:
    import ssl

    from requests.adapters import HTTPAdapter

    _orig_init_poolmanager = HTTPAdapter.init_poolmanager

    def _custom_init_poolmanager(self, *args, **kwargs):
        if "ssl_context" not in kwargs:
            ctx = ssl.create_default_context()
            ctx.verify_flags &= ~ssl.VERIFY_X509_STRICT
            kwargs["ssl_context"] = ctx
        return _orig_init_poolmanager(self, *args, **kwargs)

    HTTPAdapter.init_poolmanager = _custom_init_poolmanager
