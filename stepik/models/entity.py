class Entity:
    def __init__(self, user, data):
        self.user = user

        self._load_from_data(data)

    def __str__(self):
        return "{}\t{}".format(self.id, self.title)

    def _load_from_data(self, data):
        for key in data:
            self.__dict__[key] = data[key]

    def _load(self):
        pass

    @classmethod
    def get(cls, user, entity_id):
        entity = cls(user, {"id": entity_id})
        entity._load()

        return entity
