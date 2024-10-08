from typing import Any

from wildlife_tracker.habitat_management.habitat import Habitat

class Migration:

    def __init__(self, 
                 migration_id: int, 
                 start_date: str,
                 start_location: Habitat,
                 current_location: str,
                 status: str):
            
            self.migration_id = migration_id
            self.start_date = start_date
            self.start_location = start_location
            self.current_location = current_location
            self.status = status

            # this is Pythonic for
            # if animals is not None:
            #   self.animals = animals
            # else:
            #self.animals = []
            pass

