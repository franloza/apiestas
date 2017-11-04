from distutils.core import setup

setup(
    name='apiestas',
    version='1.0',
    packages=['', 'arbs', 'utils', 'server', 'spiders'],
    package_dir={'': 'apiestas'},
    url='localhost',
    license='MIT License',
    author='Fran Lozano,  Jorge Sánchez',
    author_email='',
    description='API to get arbs from bookmakers '
)
