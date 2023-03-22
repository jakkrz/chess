def get_positive_number_input(prompt: str) -> int:
    while True:
        print(prompt, end="")
        input_str = input()

        try:
            return string_to_positive_number(input_str)
        except ValueError:
            print(f"'{input_str}' is not a valid positive number. Try again")


def string_to_positive_number(string: str) -> int:
    integer = int(string)

    if integer > 0:
        return integer

    raise ValueError
