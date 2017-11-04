from setuptools import setup, find_packages

setup(
    name='apiestas',
    version='1.0',
    packages=find_packages(),
    entry_points={'scrapy': ['settings = apiestas.settings']},
    url='localhost',
    license='MIT License',
    author='Fran Lozano,  Jorge Sánchez',
    author_email='',
    description='API to get arbs from bookmakers '
)
