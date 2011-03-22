from setuptools import setup, find_packages

setup(
    name='rezine_analytics',
    version='0.1',
    url='https://github.com/rockyburt/rezine_analytics',
    license='BSD',
    author='Rocky Burt',
    author_email='rocky@serverzen.com',
    description='A Google Analytics plugin for Rezine',
    long_description=open('README.rst').read() \
        + '\n\n' + open('CHANGES.rst').read(),
    zip_safe=False,
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
    ],
    packages=find_packages(),
    install_requires=[
        ],
    entry_points={
        'rezine_plugins': [
            'rezine_analytics = rezine_analytics'
            ],
        },
    test_suite="rezine_analytics",
    platforms='any',
    include_package_data=True,
)
