import random
from copy import deepcopy
import requests

def readfile(path):
    with open(path, 'r') as f:
        return f.read()

def writefile(path, content):
    with open(path, 'w') as f:
        f.write(content)


class Library:
    def __init__(self, name):
        self.name = name
        self._library = set()

    def __len__(self):
        return len(self._library)

    def __iter__(self):
        return iter(self._library)


    def add(self, book):
        assert isinstance(book, Book)
        self._library.add(book)

    def browse(self, language=None, **kwargs):
        kwargs.update(language=language)
        findings = set()
        for book in self._library:
            if book.check(**kwargs):
                findings.add(book)
        return findings

    def browse_one(self, language=None, **kwargs):
        kwargs.update(language=language)
        library = deepcopy(self._library)
        while library:
            book = library.pop()
            if book.check(**kwargs):
                return book
        return None

    def pick(self, n=1):
        result = random.sample(self._library, k=n)
        if n == 1:
            return result[0]
        else:
            return result
    



class Book:

    CHECK_DEFAULTS_EQUAL = {'author': False, 'subtitle': False}

    def __init__(self, title = '', author = '', gutid = None, gutyear = None, **kwargs):
        self.title = title
        self.author = author
        self.gutid = gutid
        self.gutyear = gutyear
        for key, val in kwargs.items():
            setattr(self, key.lower().strip(), val.strip())
        if not hasattr(self, 'language'):
            self.language = 'english'
        else:
            self.language = self.language.lower()

    def __repr__(self):
        return self.title + ', by ' + self.author

    @property
    def attrs(self):
        return self.__dict__

    @property
    def url(self):
        return "https://www.gutenberg.org/files/{0}/{0}-0.txt".format(self.gutid)



    def get_html(self):
        session = requests.Session()
        session.mount("http://", requests.adapters.HTTPAdapter(max_retries=2))
        session.mount("https://", requests.adapters.HTTPAdapter(max_retries=2))
        response = session.get(self.url)
        if response.status_code == 200:
            return response.text
        else:
            raise Exception
        

    

    def check(self, default=True, equal=None, **kwargs):
        for key, val in kwargs.items():
            if val is None:
                continue
            if not self._condition(key, val, default=default, equal=equal):
                return False
        return True

    def _condition(self, key, val, default=True, equal=None):
        """Checks if the instance's attribute 'key' has the value 'val'
        key: attribute to check
        val: value towards which the attribute is checked
        default: if False: the checking is done via the value of 'equal'
                 if True: the checking is done via the default behavior
        equal: if True: the checking is done via an equality
               if False: the checking is done via a 'contains'
        Note: if default is True, equal is ignored
        Note: if the instance doesn't have the attribute 'key', returns
              False
        """
        if not hasattr(self, key):
            return False
        if default:
            _equal = self.CHECK_DEFAULTS_EQUAL.get(key, True)
        else:
            _equal = equal
        if _equal:
            return getattr(self, key) == val
        else:
            return val in getattr(self, key)
