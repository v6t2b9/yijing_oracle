class HexagramManager:
    """
    HexagramManager manages hexagram data and contexts for Yijing oracle readings.
    Attributes:
        resources_path (Path): Path to the resources directory containing hexagram data.
    Methods:
        __init__(resources_path: Path):
            Initializes the HexagramManager with the specified resources path.
        get_hexagram_data(number: int) -> Dict[str, Any]:
            Retrieves the data for a specific hexagram number.
            Parameters:
                number (int): The hexagram number (must be between 1 and 64).
            Returns:
                Dict[str, Any]: The data associated with the hexagram.
            Raises:
                ValueError: If the hexagram number is not between 1 and 64.
        create_reading_context(original_hex_num: int, changing_lines: List[int], resulting_hex_num: int) -> HexagramContext:
            Creates a HexagramContext based on the original and resulting hexagrams and the changing lines.
            Parameters:
                original_hex_num (int): The number of the original hexagram.
                changing_lines (List[int]): The lines that are changing in the reading.
                resulting_hex_num (int): The number of the resulting hexagram.
            Returns:
                HexagramContext: The context for the hexagram reading.
    """
    def __init__(self, resources_path: Path):
        self.resources_path = resources_path

    def get_hexagram_data(self, number: int) -> Dict[str, Any]:
        if not 1 <= number <= 64:
            raise ValueError(f"Invalid hexagram number: {number}")
            
        return load_hexagram_data(number)

    def create_reading_context(
        self,
        original_hex_num: int,
        changing_lines: List[int],
        resulting_hex_num: int
    ) -> HexagramContext:
        original_data = self.get_hexagram_data(original_hex_num)
        resulting_data = self.get_hexagram_data(resulting_hex_num)
        
        return HexagramContext(
            original_hexagram=original_data,
            changing_lines=changing_lines,
            resulting_hexagram=resulting_data
        )