def get_cohort(program_term, academic_term) -> int:
    """
    Given a student's academic term and program term, return their cohort academic term.
    May terms (i.e., terms ending in '20') are skipped in program term progression.

    :param program_term: int from 1 to 8 indicating current term in the program.
    :param academic_term: int in form YYYYTT (e.g., 202530 = 2025 September).
    :return: int cohort academic term (e.g., 202430).
    """
    program_term = int(program_term)
    academic_term = int(academic_term)

    if program_term < 1 or program_term > 8:
        raise ValueError("Program term must be between 1 and 8.")

    year = academic_term // 100
    term = academic_term % 100

    while program_term > 1:
        # Move back to previous term
        if term == 10:
            term = 30
            year -= 1
        elif term == 30:
            term = 20
        elif term == 20:
            term = 10
            year -= 1

        # Only decrement program term if current term is not May (20)
        if term != 20:
            program_term -= 1

    return year * 100 + term

def get_achievement_level(gai_score, question_max):
    """
    Returns the achievement level as a float formatted to 2 decimal places.
    """
    if question_max == 0:
        raise ValueError("Maximum question score cannot be zero.")
    return round(gai_score / question_max, 2)
