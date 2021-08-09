
class ReSkinData:
    """
    ReSkin Data object.
    
    Attributes
    ----------
    device_id: int
        id of the sensor device
    time: int
        timestamp
    acquisition_delay: int
        delay in acquiring data
    data: list
        data from sensor

    """
    def __init__(self, time=-1., acquisition_delay=-1., data=[],
        device_id:int = -1) -> None:
        """
        Create a ReSkinData object
        
        Parameters
        ----------
        time: int, optional
            timestamp
        acquisition_delay: int, optional
            delay in acquiring data
        data: list
            data from sensor
        device_id: int, optional
            id of the sensor device
        """
        
        self.time = time
        self.acquisition_delay = acquisition_delay
        self.data = data
        self.device_id = device_id