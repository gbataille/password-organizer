from . import prompts
from .prompts import confirm, listmenu  # noqa  # pylint:disable=unused-import


def prompt(questions, answers=None, **kwargs):
    if isinstance(questions, dict):
        questions = [questions]
    answers = answers or {}

    for question in questions:
        # import the question
        if 'type' not in question:
            raise ValueError('you must provide a type parameter')
        if 'name' not in question:
            raise ValueError('you must provide a name parameter')
        if 'message' not in question:
            raise ValueError('you must provide a message parameter')
        try:
            choices = question.get('choices')
            if choices is not None and callable(choices):
                question['choices'] = choices(answers)

            _kwargs = {}
            _kwargs.update(kwargs)
            _kwargs.update(question)
            question_type = _kwargs.pop('type')
            name = _kwargs.pop('name')
            message = _kwargs.pop('message')
            question_when = _kwargs.pop('when', None)
            question_filter = _kwargs.pop('filter', None)

            if question_when:
                # at least a little sanity check!
                if callable(question['when']):
                    try:
                        if not question['when'](answers):
                            continue
                    except Exception as e:
                        raise ValueError(
                            'Problem in \'when\' check of %s question: %s' %
                            (name, e))
                else:
                    raise ValueError('\'when\' needs to be function that accepts a dict argument')
            if question_filter:
                # at least a little sanity check!
                if not callable(question['filter']):
                    raise ValueError('\'filter\' needs to be function that accepts an argument')

            if callable(question.get('default')):
                _kwargs['default'] = question['default'](answers)

            application = getattr(prompts, question_type).question(message, **_kwargs)
            answer = application.run()

            if answer is not None:
                if question_filter:
                    try:
                        answer = question['filter'](answer)
                    except Exception as e:
                        raise ValueError(
                            'Problem processing \'filter\' of %s question: %s' %
                            (name, e))
                answers[name] = answer
        except AttributeError as e:
            print(e)
            raise ValueError('No question type \'%s\'' % question_type)
        except KeyboardInterrupt:
            return {}
    return answers
