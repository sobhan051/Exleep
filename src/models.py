import collections.abc

# Patch for Experta compatibility inside models if needed
if not hasattr(collections, 'Mapping'):
    collections.Mapping = collections.abc.Mapping

from experta import Fact

class Person(Fact):
    """Stores user demographics, lifestyle, and habits."""
    pass

class Diagnosis(Fact):
    """Stores a detected disorder name."""
    pass

class Advice(Fact):
    """Stores a piece of generated coaching advice."""
    pass