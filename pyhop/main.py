"""Planowanie dla problemu przemieszczenia osób z jednej strony mostu na drugą.

Z racji wieku mostu tylko 2 osoby mogą się naraz na nim znaleźć;
Z powodu nocy potrzebujemy pochodni by przejść przez most, a ta jest tylko jedna;
Z powodu nadbiegającego tłumu zombie mamy tylko 15 min by wszystkich przerzucić.
"""

import pyhop


def has_time(state, _):
    return False if state.time < 0 else state


def all_on_right_within_time(state, _):
    if all(person in state.side['right']
           for person in state.people.keys()) and state.time >= 0:
        return state
    else:
        return False


def none_on_left(state, _):
    return state if all(person not in state.side['left']
                        for person in state.people.keys()) else False


def walk_people(state, prev_side, next_side):
    time = 0
    for person in state.chosen:
        state.side[prev_side].remove(person)
        state.side[next_side].add(person)
        time = state.people[person] if state.people[person] > time else time
    else:
        state.time -= time
        state.torch = next_side
        state.chosen = []
        return state


def is_person_on_side(state, side):
    return state if state.chosen[-1] in state.side[side] else False


def is_not_chosen(state, _):
    return False if state.chosen.count(state.chosen[-1]) > 1 else state


def append_person_to_chosen(state, person):
    state.chosen.append(person)
    return state


def fun_factory(name, index):
    def fun(state):
        return [('append_person_to_chosen', list(state.people.keys())[index])]
    fun.__name__ = name
    return fun


def chose_person(state):
    return [('pick_person',), ('is_person_on_side', state.torch),
            ('is_not_chosen', None)]


def travel_person(state):
    return [('has_time', None), ('chose_person',),
            ('walk_people', state.torch,
             'right' if state.torch == 'left' else 'left'),
            ('escape',)]


def travel_2_people(state):
    return [('has_time', None), ('chose_person',), ('chose_person',),
            ('walk_people', state.torch,
             'right' if state.torch == 'left' else 'left'),
            ('escape',)]


def assert_escape(_):
    return [('all_on_right_within_time', None), ('none_on_left', None)]


def main():
    state = pyhop.State('state')

    state.people = {
        'me': 1,
        'assistant': 2,
        'janitor': 5,
        'professor': 8
    }
    state.side = {
        'left': {person for person in state.people.keys()},
        'right': set()
    }
    state.chosen = []
    state.torch = 'left'
    state.time = 15

    pyhop.declare_operators(all_on_right_within_time, none_on_left, walk_people,
                            is_person_on_side, is_not_chosen, has_time,
                            append_person_to_chosen)

    pyhop.declare_methods('pick_person',
                          *[fun_factory('chose_{:d}'.format(i), i-1)
                            for i in range(len(state.people.keys()))])
    pyhop.declare_methods('chose_person', chose_person)
    pyhop.declare_methods('travel_person', travel_person)
    pyhop.declare_methods('travel_2_people', travel_2_people)
    pyhop.declare_methods('assert_escape', assert_escape)
    pyhop.declare_methods('escape', assert_escape,
                          travel_person, travel_2_people)

    pyhop.pyhop(state, [('escape',)], verbose=3)


if __name__ == "__main__":
    main()
