from setuptools import setup

setup(
    name='ds-bot',
    version='0.1',
    author='Altair Geo',
    author_email='altairgeo000@gmail.com',
    description='My discord bot',
    long_description='My own discord bot. Replace for Dyno',
    url='https://github.com/AltairGeo/DiscordBot',
    packages=['ds-bot'],
    install_requires=open('requirements.txt').read().splitlines(),
)
