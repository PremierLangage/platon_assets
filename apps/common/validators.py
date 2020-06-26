from datetime import timedelta
from typing import Union

from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible



@deconstructible
class MinDurationValidator:
    """Ensure that a DurationField is not shorter than the given duration."""
    
    
    def __init__(self, duration: Union[int, timedelta]):
        self.duration = duration.total_seconds() if isinstance(duration, timedelta) else duration
    
    
    def __call__(self, value):
        seconds = value.total_seconds() if isinstance(value, timedelta) else value
        if seconds < self.duration:
            raise ValidationError(
                'Given duration (%(value)s should not be shorter than %(duration)s',
                params={'value': value, 'duration': self.duration},
            )
    
    
    def __eq__(self, other) -> bool:
        return self.duration == other.duration



@deconstructible
class MaxDurationValidator:
    """Ensure that a DurationField is not longer than the given duration."""
    
    
    def __init__(self, duration: Union[int, timedelta]):
        self.duration = duration.total_seconds() if isinstance(duration, timedelta) else duration
    
    
    def __call__(self, value):
        seconds = value.total_seconds() if isinstance(value, timedelta) else value
        if seconds > self.duration:
            raise ValidationError(
                'Given duration (%(value)s should not be longer than %(duration)s',
                params={'value': value, 'duration': self.duration},
            )
    
    
    def __eq__(self, other) -> bool:
        return self.duration == other.duration
