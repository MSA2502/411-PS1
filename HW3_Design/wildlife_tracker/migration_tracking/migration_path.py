from typing import Optional

from habitat_management.habitat import Habitat 

class MigrationPath:

    def __init__(self,
                 path_id: int, 
                 start_location: Habitat,
                 duration: Optional[int],
                 destination: Habitat,
                 species:str

                 ) -> None:
        self.path_id = path_id
        self.start_location = start_location
        self.duration = duration
        self.desination = destination
        self.species = species



        pass