class BrainException(Exception):
    """Base exception for Brain module"""
    pass

class DataFetchException(BrainException):
    """Failed to fetch data"""
    pass

class ModelLoadException(BrainException):
    """Failed to load ML model"""
    pass

class AnalysisException(BrainException):
    """Error during analysis"""
    pass
