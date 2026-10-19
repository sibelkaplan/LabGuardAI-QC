"""Short checks about how this application may be used.

The correct answers are the limits of the product. A score is not a certificate.
"""

QUIZ = (
    {
        "question": "quiz_q1",
        "choices": ("quiz_q1_a", "quiz_q1_b", "quiz_q1_c"),
        "answer": 1,
    },
    {
        "question": "quiz_q2",
        "choices": ("quiz_q2_a", "quiz_q2_b", "quiz_q2_c"),
        "answer": 1,
    },
    {
        "question": "quiz_q3",
        "choices": ("quiz_q3_a", "quiz_q3_b", "quiz_q3_c"),
        "answer": 1,
    },
)


def score_quiz(choices: list[int]) -> tuple[int, int]:
    correct = 0
    for item, choice in zip(QUIZ, choices):
        if choice == item["answer"]:
            correct += 1
    return correct, len(QUIZ)
