from .entity import Entity


class Step(Entity):
    def __str__(self):
        return "{}\t{}\t{}".format(self.id, self.position, self.block['name'])
