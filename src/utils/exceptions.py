from typing import Any
from abc import ABC,abstractmethod

class FintechBaseException(Exception,ABC):
    def __init__(self,message:str,details:dict[str,Any]| None=None)->None:
        super().__init__(message)
        self.message=message
        self.details=details or {}

    def __str__(self)->str:
        if self.details:
            return f"message:{self.message}|details:{self.details}"
        return self.message
    
    @abstractmethod
    def error_status(self,status_code:int)-> str:
        pass

class TransientIngestionError(FintechBaseException):

    def error_status(self,status_code:int)->str:
        return f"TransientError:{status_code}:{self.message}"



class FatalSchemaError(FintechBaseException):
    def error_status(self,status_code:int)->str:
        return f"FatalSchemaError:{status_code}:{self.message}"

class RateLimitError(TransientIngestionError):
    def error_status(self,status_code:int)->str:
        return f"RateLimitError:{status_code}:{self.message}"

class ServiceUnavailableError(TransientIngestionError):
    def error_status(self,status_code:int)->str:
        return f"ServiceUnavailableError:{status_code}:{self.message}"

