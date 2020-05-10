from setuptools import setup


setup(
    name='flake8-prometheus',
    version='0.0.1',
    description='',
    long_description='',
    # Get more from https://pypi.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Framework :: Flake8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Software Development',
        'Topic :: Software Development :: Quality Assurance',
    ],
    keywords='flake8 python prometheus',
    author='perminovs',
    license='MIT',
    install_requires=[
        'flake8',
        'prometheus_client',
    ],
    url='https://github.com/perminovs/flake8_prometheus',
    packages=['flake8_prometheus'],
    py_modules=['flake8_prometheus'],
    include_package_data=True,
    entry_points={
        'flake8.extension': [
            'PRM = flake8_prometheus.flake8_prometheus:PrometheusChecker',
        ],
    },
)
