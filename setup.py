from setuptools import setup, find_packages


setup(
    name='traq',
    version='0.0.0.dev0',
    description='Traq for python 3.3',
    long_description='Internal ticketing and invoice system for ARC. Upgraded from Python 2.7 to run on Python 3.3',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django<=1.8',
        'djangocas',
        'django-arcutils',
        'django-cloak',
        'django-extensions',
        'django_filter',
        'Markdown==2.5.2',
        'PyMySQL',
        'python3-ldap',
        'pytz>=2013b',
        'six',
        #'shortuuid',
        #'South<2.0',
        #'wsgiref==0.1.2',
    ],
)
