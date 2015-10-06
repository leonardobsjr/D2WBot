from dotamatch.api import CachedApi


class Heroes(CachedApi):
    url = "https://api.steampowered.com/IEconDOTA2_570/GetHeroes/v0001/?"

    def heroes(self):
        self.key
        results = self._get()
        heroes = {}
        for result in results['result']['heroes']:
            heroes[result['id']] = Hero(result['id'], result['name'], result['localized_name'])
        return heroes


class Hero(object):
    def __init__(self, id_, name, lname):
        self.id_ = id_
        self.name = name
        self.localized_name = lname

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
