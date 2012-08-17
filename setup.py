from setuptools import setup, find_packages

READMEFILE = 'README.rst'


setup(
        name='desqus',
        version='0.1-dev',
        packages=find_packages(),
        install_requires=[
            'flask',
            'Flask-SQLAlchemy',
            'flask-bootstrap',
            'Flask-WTF',
            'py-bcrypt',
            'flup',
            'sphinx'],
        author_email='joar@desqus.org',
        url='http://desqus.org',
        long_description=open(READMEFILE).read(),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Programming Language :: Python'],
        )
