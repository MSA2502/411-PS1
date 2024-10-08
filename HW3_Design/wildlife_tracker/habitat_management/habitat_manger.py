from typing import Optional, Any, List

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.animal_management.animal import Animal

class HabitatManager:
    def __init__(self, habitat_id: int,
                geographic_area: str,
                size: int,
                environment_type: str,
                animals: Optional[List[int]] = None) -> None:
        self.habitat_id = habitat_id
        self.geographic_area = geographic_area
        self.size = size
        self.environment_type = environment_type
        self.animals = animals or []
        habitats: dict[int, Habitat] = {}


      
        pass

    def create_habitat(habitat_id: int, geographic_area: str, size: int, environment_type: str) -> Habitat:
        pass

    def remove_habitat(habitat_id: int) -> None:
        pass

    def get_habitat_by_id(habitat_id: int) -> Habitat:
        pass

    #all habitats by environemnet, geographical details, etc

    def get_habitat_details(habitat_id: int) -> dict:
        pass

    def update_habitat_details(habitat_id: int, **kwargs: dict[str, Any]) -> None:
        pass

    def assign_animals_to_habitat(habitat_id: int, animals: List[Animal]) -> None:
        pass

    def get_animals_in_habitat(habitat_id: int) -> List[Animal]:
        pass
        
  


    
