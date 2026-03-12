from ..processing.extractors import extract_comments


def export_poll(poll):
    """Export a single poll with all its data including answers."""
    questions_list = []
    for question in poll.questions.all().order_by("weight"):
        choices_list = []
        for choice in question.choices.all().order_by("weight"):
            choices_list.append(
                {
                    "label": choice.label,
                    "is_other_choice": choice.is_other_choice,
                    "vote_count": choice.votes.count(),
                }
            )

        # Regular answers (for open questions) - just strings
        answers_list = [
            answer.answer for answer in question.answers.all().order_by("created")
        ]

        # Other answers (for "other" choice) - just strings
        other_answers = []
        if question.has_other_option:
            other_choice = question.get_other_option()
            if other_choice:
                other_answers = [
                    vote.other_vote.answer
                    for vote in other_choice.votes.filter(other_vote__isnull=False)
                ]

        questions_list.append(
            {
                "id": question.id,
                "label": question.label,
                "help_text": question.help_text,
                "weight": question.weight,
                "multiple_choice": question.multiple_choice,
                "is_open": question.is_open,
                "choices": choices_list,
                "answers": answers_list if question.is_open else [],
                "other_answers": other_answers if question.has_other_option else [],
                "vote_count": sum(c["vote_count"] for c in choices_list),
                "answer_count": len(answers_list),
                "other_answer_count": len(other_answers),
            }
        )

    return {
        "id": poll.id,
        "url": poll.get_absolute_url(),
        "questions": questions_list,
        "comments": extract_comments(poll.comments.all()),
        "comment_count": poll.comments.count(),
        "total_votes": sum(q["vote_count"] for q in questions_list),
        "total_answers": sum(q["answer_count"] for q in questions_list if q["is_open"]),
        "total_other_answers": sum(q["other_answer_count"] for q in questions_list),
    }
