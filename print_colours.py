class Print:

    @staticmethod
    def print_error(str):
        """
        Prints an error in red
        """
        print("\u001b[31;1m[!] {0}\u001b[0m".format(str))

    @staticmethod
    def print_success(str):
        """
        Prints a success in green
        """
        print("\u001b[32;1m[✓] {0}\u001b[0m".format(str))

    @staticmethod
    def print_warning(str):
        """
        Prints a warning in yellow
        """
        print("\u001b[33;1m[⚠] {0}\u001b[0m".format(str))

    @staticmethod
    def print_information(str):
        """
        Prints a success in blue
        """
        print("\u001b[34;1m[i] {0}\u001b[0m".format(str))
