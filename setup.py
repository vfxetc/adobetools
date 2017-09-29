from setuptools import setup, find_packages

setup(
    name='adobetools',
    version='0.1',
    description='Lofty Sky\'s Adobe Tools',
    url='',
    
    packages=find_packages(exclude=['build*', 'tests*']),
    include_package_data=True,
    
    author='Mike Boers',
    author_email='mikeb+adobetools@loftysky.com',
    license='BSD-3',

    entry_points={
        'console_scripts': '''
            adobetools-cep-install = adobetools.cep.install:main
        ''',
    },
    
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    
)
