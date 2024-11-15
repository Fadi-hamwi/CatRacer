"""Typing test implementation"""
import math
import operator

from utils import lower, split, remove_punctuation, lines_from_file
from ucb import main, interact, trace
from datetime import datetime


###########
# Phase 1 #
###########


def pick(paragraphs, select, k):
    """Return the Kth paragraph from PARAGRAPHS for which SELECT called on the
    paragraph returns True. If there are fewer than K such paragraphs, return
    the empty string.

    Arguments:
        paragraphs: a list of strings
        select: a function that returns True for paragraphs that can be selected
        k: an integer

    >>> ps = ['hi', 'how are you', 'fine']
    >>> s = lambda p: len(p) <= 4
    >>> pick(ps, s, 0)
    'hi'
    >>> pick(ps, s, 1)
    'fine'
    >>> pick(ps, s, 2)
    ''
    """
    empty_paragraph = ""
    for paragraph in paragraphs:
        if select(paragraph) is True:
            if k == 0:
                return paragraph
            else:
                k = k - 1
    return empty_paragraph


def about(topic):
    """Return a select function that returns whether
    a paragraph contains one of the words in TOPIC.

    Arguments:
        topic: a list of words related to a subject

    >>> about_dogs = about(['dog', 'dogs', 'pup', 'puppy'])
    >>> pick(['Cute Dog!', 'That is a cat.', 'Nice pup!'], about_dogs, 0)
    'Cute Dog!'
    >>> pick(['Cute Dog!', 'That is a cat.', 'Nice pup.'], about_dogs, 1)
    'Nice pup.'
    """
    assert all([lower(x) == x for x in topic]), 'topics should be lowercase.'

    def select(paragraph):
        paragraph = apply_changes_on(paragraph)
        for word in topic:
            if lower(word) in paragraph:
                return True
        return False

    return select


def apply_changes_on(paragraph):
    paragraph = lower(paragraph)
    paragraph = remove_punctuation(paragraph)
    paragraph = split(paragraph)
    return paragraph


def accuracy(typed, source):
    """Return the accuracy (percentage of words typed correctly) of TYPED
    when compared to the prefix of SOURCE that was typed.

    Arguments:
        typed: a string that may contain typos
        source: a string without errors

    >>> accuracy('Cute Dog!', 'Cute Dog.')
    50.0
    >>> accuracy('A Cute Dog!', 'Cute Dog.')
    0.0
    >>> accuracy('cute Dog.', 'Cute Dog.')
    50.0
    >>> accuracy('Cute Dog. I say!', 'Cute Dog.')
    50.0
    >>> accuracy('Cute', 'Cute Dog.')
    100.0
    >>> accuracy('', 'Cute Dog.')
    0.0
    >>> accuracy('', '')
    100.0
    """
    typed_words = split(typed)
    source_words = split(source)
    source_len = len(source_words)
    typed_len = len(typed_words)

    if typed_len == 0 and source_len == 0:
        return 100.0
    if typed_len == 0 or source_len == 0:
        return 0.0

    extra_typed_words_cnt = compute_extra_typed_words(typed_len, source_len)
    mistyped_words_cnt = compute_mistyped_words(typed_words, source_words)

    return compute_accuracy(mistyped_words_cnt, extra_typed_words_cnt, typed_len)


def compute_mistyped_words(typed_words, source_words):
    miss_typed_words_cnt = 0
    for i in range(min(len(typed_words), len(source_words))):
        if typed_words[i] != source_words[i]:
            miss_typed_words_cnt += 1

    return miss_typed_words_cnt


def compute_extra_typed_words(typed_words_len, source_words_len):
    if typed_words_len > source_words_len:
        return operator.sub(typed_words_len, source_words_len)
    return 0


def compute_accuracy(mistyped_words_cnt, extra_typed_words_cnt, typed_words_len):
    correctly_typed_words = (mistyped_words_cnt + extra_typed_words_cnt) / typed_words_len
    return (1 - correctly_typed_words) * 100


def wpm(typed, elapsed):
    """Return the words-per-minute (WPM) of the TYPED string.

    Arguments:
        typed: an entered string
        elapsed: an amount of time in seconds

    >>> wpm('hello friend hello buddy hello', 15)
    24.0
    >>> wpm('0123456789',60)
    2.0
    """
    assert elapsed > 0, 'Elapsed time must be positive'
    return (len(typed) / 5) * (60 / elapsed)


###########
# Phase 2 #
###########

def autocorrect(typed_word, word_list, diff_function, limit):
    """Returns the element of WORD_LIST that has the smallest difference
    from TYPED_WORD. Instead, returns TYPED_WORD if that difference is greater
    than LIMIT.

    Arguments:
        typed_word: a string representing a word that may contain typos
        word_list: a list of strings representing source words
        diff_function: a function quantifying the difference between two words
        limit: a number

    >>> ten_diff = lambda w1, w2, limit: 10 # Always returns 10
    >>> autocorrect("hwllo", ["butter", "hello", "potato"], ten_diff, 20)
    'butter'
    >>> first_diff = lambda w1, w2, limit: (1 if w1[0] != w2[0] else 0) # Checks for matching first char
    >>> autocorrect("tosting", ["testing", "asking", "fasting"], first_diff, 10)
    'testing'
    """
    if typed_word in word_list:
        return typed_word
    autocorrect_word, smallest_diff = compute_smallest_diff_and_return_word(diff_function, limit, typed_word, word_list)

    return typed_word if smallest_diff > limit else autocorrect_word


def compute_smallest_diff_and_return_word(diff_function, limit, typed_word, word_list):
    smallest_diff, autocorrect_word = math.inf, ""
    for word in word_list:
        current_diff = diff_function(typed_word, word, limit)
        if current_diff < smallest_diff:
            smallest_diff = current_diff
            autocorrect_word = word
    return autocorrect_word, smallest_diff


def feline_fixes(typed, source, limit):
    """A diff function for autocorrect that determines how many letters
    in TYPED need to be substituted to create SOURCE, then adds the difference in
    their lengths and returns the result.

    Arguments:
        typed: a starting word
        source: a string representing a desired goal word
        limit: a number representing an upper bound on the number of chars that must change

    >>> big_limit = 10
    >>> feline_fixes("nice", "rice", big_limit)    # Substitute: n -> r
    1
    >>> feline_fixes("range", "rungs", big_limit)  # Substitute: a -> u, e -> s
    2
    >>> feline_fixes("pill", "pillage", big_limit) # Don't substitute anything, length difference of 3.
    3
    >>> feline_fixes("roses", "arose", big_limit)  # Substitute: r -> a, o -> r, s -> o, e -> s, s -> e
    5
    >>> feline_fixes("rose", "hello", big_limit)   # Substitute: r->h, o->e, s->l, e->l, length difference of 1.
    5
    """
    if limit < 0:
        return 0

    if len(typed) == 0 or len(source) == 0:
        return len(source) + len(typed)

    if typed[0] == source[0]:
        return feline_fixes(typed[1:], source[1:], limit)

    return 1 + feline_fixes(typed[1:], source[1:], limit - 1)


def minimum_mewtations(start, goal, limit):
    """A diff function that computes the edit distance from START to GOAL.
    This function takes in a string START, a string GOAL, and a number LIMIT.
    Arguments:
        start: a starting word
        goal: a goal word
        limit: a number representing an upper bound on the number of edits
    >>> big_limit = 10
    >>> minimum_mewtations("cats", "scat", big_limit)       # cats -> scats -> scat
    2
    >>> minimum_mewtations("purng", "purring", big_limit)   # purng -> purrng -> purring
    2
    >>> minimum_mewtations("ckiteus", "kittens", big_limit) # ckiteus -> kiteus -> kitteus -> kittens
    3
    """
    if limit < 0:
        return 0
    elif len(goal) == 0 or len(start) == 0:
        return len(goal) + len(start)
    else:
        if goal[0] == start[0]:
            return minimum_mewtations(start[1:], goal[1:], limit)

        add = minimum_mewtations(start, goal[1:], limit - 1)
        remove = minimum_mewtations(start[1:], goal, limit - 1)
        substitute = minimum_mewtations(start[1:], goal[1:], limit - 1)

        return 1 + min(add, remove, substitute)


def final_diff(typed, source, limit):
    """A diff function that takes in a string TYPED, a string SOURCE, and a number LIMIT.
    If you implement this function, it will be used."""
    return minimum_mewtations(typed, source, max(len(typed), len(source), FINAL_DIFF_LIMIT))


FINAL_DIFF_LIMIT = 6  # REPLACE THIS WITH YOUR LIMIT


###########
# Phase 3 #
###########


def report_progress(typed, prompt, user_id, upload):
    """Upload a report of your id and progress so far to the multiplayer server.
    Returns the progress so far.

    Arguments:
        typed: a list of the words typed so far
        prompt: a list of the words in the typing prompt
        user_id: a number representing the id of the current user
        upload: a function used to upload progress to the multiplayer server

    >>> print_progress = lambda d: print('ID:', d['id'], 'Progress:', d['progress'])
    >>> # The above function displays progress in the format ID: __, Progress: __
    >>> print_progress({'id': 1, 'progress': 0.6})
    ID: 1 Progress: 0.6
    >>> typed = ['how', 'are', 'you']
    >>> prompt = ['how', 'are', 'you', 'doing', 'today']
    >>> report_progress(typed, prompt, 2, print_progress)
    ID: 2 Progress: 0.6
    0.6
    >>> report_progress(['how', 'aree'], prompt, 3, print_progress)
    ID: 3 Progress: 0.2
    0.2
    """
    progress_ratio = compute_progress_ratio(prompt, typed)
    upload({'id': user_id, 'progress': progress_ratio})
    return progress_ratio


def compute_progress_ratio(prompt, typed):
    correctly_typed_till_mistype = compute_correct_words_till_mistype(prompt, typed)
    progress_ratio = get_progress_ratio(correctly_typed_till_mistype, prompt)
    return progress_ratio


def get_progress_ratio(correctly_typed_till_mistype, prompt):
    return correctly_typed_till_mistype / len(prompt)


def compute_correct_words_till_mistype(prompt, typed):
    typed_correctly_till_mistype = 0
    for i in range(len(typed)):
        if typed[i] == prompt[i]:
            typed_correctly_till_mistype += 1
        else:
            break
    return typed_correctly_till_mistype


def time_per_word(words, times_per_player):
    """Given timing data, return a match dictionary, which contains a
    list of words and the amount of time each player took to type each word.

    Arguments:
        words: a list of words, in the order they are typed.
        times_per_player: A list of lists of timestamps including the time
                          the player started typing, followed by the time
                          the player finished typing each word.

    >>> p = [[75, 81, 84, 90, 92], [19, 29, 35, 36, 38]]
    >>> match = time_per_word(['collar', 'plush', 'blush', 'repute'], p)
    >>> match["words"]
    ['collar', 'plush', 'blush', 'repute']
    >>> match["times"]
    [[6, 3, 6, 2], [10, 6, 1, 2]]
    """
    p = times_per_player
    times = []
    for i in range(len(p)):
        times += [get_time_per_player(p[i])]

    return match(words, times)


def get_time_per_player(times):
    player_time = []
    for i in range(len(times)-1):
        player_time.append(times[i+1] - times[i])
    return player_time


def fastest_words(match):
    """Return a list of lists of which words each player typed fastest.

    Arguments:
        match: a match dictionary as returned by time_per_word.

    >>> p0 = [5, 1, 3]
    >>> p1 = [4, 1, 6]
    >>> fastest_words(match(['Just', 'have', 'fun'], [p0, p1]))
    [['have', 'fun'], ['Just']]
    >>> p0  # input lists should not be mutated
    [5, 1, 3]
    >>> p1
    [4, 1, 6]
    """
    player_count = len(get_all_times(match))
    word_count = len(get_all_words(match))
    fastest_words_per_player = [[] for _ in range(player_count)]

    for word_index in range(word_count):
        compute_fastest_words_for_each_player(fastest_words_per_player, match, player_count, word_index)
    return fastest_words_per_player


def compute_fastest_words_for_each_player(fastest_words_per_player, match, player_count, word_index):
    min_time_per_word_for_player = math.inf
    player = 0
    word = ""
    for player_index in range(player_count):
        current_word_time = time(match, player_index, word_index)
        if current_word_time < min_time_per_word_for_player:
            min_time_per_word_for_player = current_word_time
            player = player_index
            word = get_word(match, word_index)
    fastest_words_per_player[player].append(word)


def match(words, times):
    """A dictionary containing all words typed and their times.

    Arguments:
        words: A list of strings, each string representing a word typed.
        times: A list of lists for how long it took for each player to type
            each word.
            times[i][j] = time it took for player i to type words[j].

    Example input:
        words: ['Hello', 'world']
        times: [[5, 1], [4, 2]]
    """
    assert all([type(w) == str for w in words]), 'words should be a list of strings'
    assert all([type(t) == list for t in times]), 'times should be a list of lists'
    assert all([isinstance(i, (int, float)) for t in times for i in t]), 'times lists should contain numbers'
    assert all([len(t) == len(words) for t in times]), 'There should be one word per time.'
    return {"words": words, "times": times}


def get_word(match, word_index):
    """A utility function that gets the word with index word_index"""
    assert 0 <= word_index < len(match["words"]), "word_index out of range of words"
    return match["words"][word_index]


def time(match, player_num, word_index):
    """A utility function for the time it took player_num to type the word at word_index"""
    assert word_index < len(match["words"]), "word_index out of range of words"
    assert player_num < len(match["times"]), "player_num out of range of players"
    return match["times"][player_num][word_index]


def get_all_words(match):
    """A selector function for all the words in the match"""
    return match["words"]


def get_all_times(match):
    """A selector function for all typing times for all players"""
    return match["times"]


def match_string(match):
    """A helper function that takes in a match dictionary and returns a string representation of it"""
    return f"match({match['words']}, {match['times']})"


enable_multiplayer = False  # Change to True when you're ready to race.


##########################
# Command Line Interface #
##########################


def run_typing_test(topics):
    """Measure typing speed and accuracy on the command line."""
    paragraphs = lines_from_file('data/sample_paragraphs.txt')
    select = lambda p: True
    if topics:
        select = about(topics)
    i = 0
    while True:
        source = pick(paragraphs, select, i)
        if not source:
            print('No more paragraphs about', topics, 'are available.')
            return
        print('Type the following paragraph and then press enter/return.')
        print('If you only type part of it, you will be scored only on that part.\n')
        print(source)
        print()

        start = datetime.now()
        typed = input()
        if not typed:
            print('Goodbye.')
            return
        print()

        elapsed = (datetime.now() - start).total_seconds()
        print("Nice work!")
        print('Words per minute:', wpm(typed, elapsed))
        print('Accuracy:        ', accuracy(typed, source))

        print('\nPress enter/return for the next paragraph or type q to quit.')
        if input().strip() == 'q':
            return
        i += 1


@main
def run(*args):
    """Read in the command-line argument and calls corresponding functions."""
    import argparse
    parser = argparse.ArgumentParser(description="Typing Test")
    parser.add_argument('topic', help="Topic word", nargs='*')
    parser.add_argument('-t', help="Run typing test", action='store_true')

    args = parser.parse_args()
    if args.t:
        run_typing_test(args.topic)
