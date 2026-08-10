from .spain_validator import SpainValidator
from .france_validator import FranceValidator
from .italy_validator import ItalyValidator

class ValidatorFactory:
    @staticmethod
    def get_validator(country_code: str):
        validators = {
            "spain": SpainValidator,
            "france": FranceValidator,
            "italy": ItalyValidator,
            "ispanya": SpainValidator,
            "fransa": FranceValidator,
            "italya": ItalyValidator
        }
        
        validator_class = validators.get(country_code.lower())
        if not validator_class:
            raise ValueError(f"Desteklenmeyen veya yapılandırılmamış ülke: {country_code}")
            
        return validator_class()
