
class Collection:

    parent_collections = ()
    parent_generators = ()

    def take(self, count):
        return TakeTransformation(self, count)

    def get_all_subcollections(self):
        collections = []
        def crawler(collection):
            if collection in collections:
                return
            for parent in collection.parent_collections:
                crawler(parent)
            for parent in collection.parent_generators:
                crawler(parent)
            collections.append(collection)
        crawler(self)
        return collections

    def declare(self, builder):
        pass

    def get_constructor_args(self, builder):
        return ()



from qit.base.transformation import TakeTransformation
