from enum import Enum


class Color(Enum):
    """ Color definitions. """
    
    WHITE = 'white'
    GRAY = '#6f7066'
    DARK_GRAY = '#333'
    RED = '#ff4d4d'
    ORANGE = '#ffc966'
    YELLOW = '#ffff4d'
    GREEN = '#4dff4d'
    GREEN2 = '#39bf39'
    PURPLE = '#be90d4'
    BLUE = '#4a80ff'
    CYAN = '#0cf0f0'


def get_color_number(color: str) -> int:
    """ Gets color's number from colors list in the game.

    Args:
        color (str): Color's value (hex)

    Returns:
        int: Number of a color.
    """
    
    colors = [color.value for color in Color]
    return colors.index(color)


def get_color_by_number(number: int) -> str:
    """ Gets color's value by its number in the colors list.

    Args:
        number (int): Number of a color

    Returns:
        str: Color value.
    """
    
    colors = [color.value for color in Color]
    return colors[number]


def hex_to_rgba(hex_color, alpha=1.0):
    """ Converts a hex color code to an RGBA tuple.

    Args:
        hex_color (str): A string representing the hex color
            (e.g., "#333" or "#333333").
        alpha (float, optional): The transparency level (0.0 = fully
            transparent, 1.0 = fully opaque). Default is 1.0 (fully opaque).

    Returns:
        tuple: An (R, G, B, A) tuple where:
        - R, G, B are integers (0-255) representing red, green, and blue channels.
        - A is a float (0.0-1.0) representing the alpha (transparency) channel.
    """
    
    hex_color = hex_color.lstrip("#")
    
    if len(hex_color) == 3:
        hex_color = "".join([c * 2 for c in hex_color])
    
    r, g, b = [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
    
    return (r, g, b, alpha)
