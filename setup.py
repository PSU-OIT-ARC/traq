from setuptools import setup, find_packages


setup(
    name='traq',
    version='0.0.0.dev0',
    description='Traq',
    long_description='Internal ticketing and invoice system for ARC',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'django==1.5.6',
        'djangocas',
        'django-arcutils',
        'django-cloak',
        'django-extensions',
        'django_filter',
        'Markdown==2.3.1',
        'MySQL-python==1.2.5',
        'python-ldap==2.3.13',
        'pytz>=2013b',
        'shortuuid',
        'South<2.0',
        'wsgiref==0.1.2',
    ],
)
