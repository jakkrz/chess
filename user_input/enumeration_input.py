from typing import List, Optional, TypeVar


def get_enumeration_input(prompt: str, choices: List[str]) -> str:
    while True:
        possible_input_str = generate_possible_input_string(choices)
        print(f"{prompt}({possible_input_str}) ", end="")
        choice_string = input()

        choice = match_choice_string(choice_string, choices)

        if choice is not None:
            return choice

        print(f"{choice} is not a valid choice. Try again")


def match_choice_string(choice_string: str, choices: List[str]) -> Optional[str]:
    if len(choice_string) == 0:
        return None
    elif len(choice_string) == 1:
        return match_singular_letter_choice_string(choice_string, choices)
    else:
        return match_multiple_letter_choice_string(choice_string, choices)


def match_singular_letter_choice_string(choice_string: str, choices: List[str]) -> Optional[str]:
    for choice in choices:
        if choice[0].lower() == choice_string:
            return choice

    return None


def match_multiple_letter_choice_string(choice_string: str, choices: List[str]) -> Optional[str]:
    for choice in choices:
        if choice.lower() == choice_string:
            return choice

    return None


def generate_possible_input_string(choices: List[str]) -> str:
    choice_first_letters = get_choice_first_letters(choices)
    alternating_possible_inputs = alternating_elements(choice_first_letters, choices)

    return "|".join(alternating_possible_inputs)


T = TypeVar("T")
def alternating_elements(list_a: List[T], list_b: List[T]) -> List[T]:
    result = []
    index = 0
    shorter_length = min(len(list_a), len(list_b))
    take_from_list_a = True
    
    while True:
        if index >= shorter_length:
            break

        if take_from_list_a:
            result.append(list_a[index])
        else:
            result.append(list_b[index])
            index += 1

        take_from_list_a = not take_from_list_a

    return result


def get_choice_first_letters(choices: List[str]) -> List[str]:
    result = []

    for choice in choices:
        result.append(choice[0])

    return result
