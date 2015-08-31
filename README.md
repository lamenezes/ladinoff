# ladinoff
***
## fanfiction.net fan fics metadata crawler
Crawls fics metadata from [fanfiction.net](http://fanfiction.net) and storing them in a database and displaying them using Django.
*Be sure to ask them for permission when doing this*

## Intallation
Clone the repository:
    ``
    $ git clone https://github.com/lamenezes/ladinoff.git
    $ cd ladinoff/ladino
    ``

Install requirements:
    ``$ pip install -r requirements.txt``

Open ladino/settings.py on a text editor and change your (line 78).
*(Optional)* if you want to use another db check the [django docs on databasse](https://docs.djangoproject.com/en/1.8/ref/databases/). You will probably have to install another db driver.

Database setup:
    ``
    $ python manage.py syncdb
    $ python manage.py migrate
    ``

## Usage
Soon.
