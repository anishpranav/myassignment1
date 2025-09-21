"""
Color utilities for terminal output
"""

class Colors:
    """ANSI color codes for terminal output"""
    
    # Basic colors
    RESET = '\033[0m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    UNDERLINE = '\033[4m'
    
    # Foreground colors
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MAGENTA = '\033[35m'
    CYAN = '\033[36m'
    WHITE = '\033[37m'
    
    # Bright colors
    BRIGHT_BLACK = '\033[90m'
    BRIGHT_RED = '\033[91m'
    BRIGHT_GREEN = '\033[92m'
    BRIGHT_YELLOW = '\033[93m'
    BRIGHT_BLUE = '\033[94m'
    BRIGHT_MAGENTA = '\033[95m'
    BRIGHT_CYAN = '\033[96m'
    BRIGHT_WHITE = '\033[97m'
    
    # Background colors
    BG_BLACK = '\033[40m'
    BG_RED = '\033[41m'
    BG_GREEN = '\033[42m'
    BG_YELLOW = '\033[43m'
    BG_BLUE = '\033[44m'
    BG_MAGENTA = '\033[45m'
    BG_CYAN = '\033[46m'
    BG_WHITE = '\033[47m'
    
    @staticmethod
    def strip_colors(text: str) -> str:
        """Remove ANSI color codes from text"""
        import re
        ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
        return ansi_escape.sub('', text)
    
    @staticmethod
    def colorize(text: str, color: str) -> str:
        """Colorize text with specified color"""
        return f"{color}{text}{Colors.RESET}"
    
    @staticmethod
    def success(text: str) -> str:
        """Format text as success message"""
        return f"{Colors.GREEN}{text}{Colors.RESET}"
    
    @staticmethod
    def error(text: str) -> str:
        """Format text as error message"""
        return f"{Colors.RED}{text}{Colors.RESET}"
    
    @staticmethod
    def warning(text: str) -> str:
        """Format text as warning message"""
        return f"{Colors.YELLOW}{text}{Colors.RESET}"
    
    @staticmethod
    def info(text: str) -> str:
        """Format text as info message"""
        return f"{Colors.CYAN}{text}{Colors.RESET}"
    
    @staticmethod
    def highlight(text: str) -> str:
        """Highlight text"""
        return f"{Colors.BOLD}{Colors.YELLOW}{text}{Colors.RESET}"