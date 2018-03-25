import sys
import argparse
# import numpy
import random
from operator import attrgetter


class Card:
    def __init__(self, card):
        if card[0] != 'X':
            self.rank = card[0]
            self.suit = card[1]
        else:
            self.rank = ''
            self.suit = 'X'
        self.ranking_value = self.ranking()

    def points(self):
        if self.rank == 'A':
            return 11
        elif self.rank == '7':
            return 10
        elif self.rank == 'K':
            return 4
        elif self.rank == 'J':
            return 3
        elif self.rank == 'Q':
            return 2
        return 0

    def ranking(self) -> int:
        if self.suit == 'X':
            return 0
        elif self.rank == 'A':
            return 11
        elif self.rank == '7':
            return 10
        elif self.rank == 'K':
            return 9
        elif self.rank == 'J':
            return 8
        elif self.rank == 'Q':
            return 7
        return int(self.rank)


class Hand:
    def __init__(self, cards_line):
        cards_list = cards_line.split(' ')[1:]
        self.cards = [Card(card) for card in cards_list]


class Trick:
    def __init__(self, trick_data):
        if not isinstance(trick_data, list):
            trick_data = trick_data.split(' ')
        self.cards = [Card(card) for card in trick_data[1:]]
        self.starting_player = int(trick_data[0])
        self.suit = self.cards[self.starting_player].suit


class Input:
    def __init__(self, input_data):
        self.player_number = int(input_data[0])
        self.hand = Hand(input_data[1])
        self.trump_player = int(input_data[2])
        self.trump_card = Card(input_data[3])
        self.current_trick = Trick(input_data[4])
        self.current_suit = input_data[5].strip()

        previous_tricks_data = input_data[6].split(' ')
        tricks_count = int(previous_tricks_data[0])
        self.previous_tricks = []
        for i in range(tricks_count):
            start = i*5+1
            trick = Trick(previous_tricks_data[start:start+5])
            self.previous_tricks.append(trick)

        point_data = input_data[7].split(' ')
        self.points = [int(point_data[0]), int(point_data[1])]


def card_ranking_on_trick(card: Card, input: Input) -> int:
    ranking = card.ranking()
    if input.current_suit == card.suit:
        ranking += 10
    return ranking

def can_cut(hand: Hand, current_suit: str, trump_suit: str) -> bool:
    for card in hand.cards:
        if card.suit == current_suit:
            return False
    for card in hand.cards:
        if card.suit == trump_suit:
            return True
    return False


def play(input: Input) -> Card:
    # first play: play an Ace if we have one
    if input.current_suit == 'X':
        for card in input.hand.cards:
            if card.rank == 'A' and card.suit != input.trump_card.suit:
                return card
    
    if can_cut(input.hand,input.current_suit,input.trump_card.suit) and input.current_suit != 'X':
        filtered_hands = list(filter(lambda card: card.suit == input.trump_card.suit, input.hand.cards))
    else:
        filtered_hands = list(filter(lambda card: card.suit == input.current_suit, input.hand.cards))
    
    can_assist = False if len(filtered_hands) == 0 else True
    if not can_assist:
        return min(input.hand.cards,key=attrgetter('ranking_value'))

    max_playable_card = max(filtered_hands,key=attrgetter('ranking_value'))
    min_playable_card = min(filtered_hands,key=attrgetter('ranking_value'))
    if max_playable_card.rank == 'A':
        return max_playable_card

    flat_last_tricks_cards = []
    for previous_trick in input.previous_tricks:
        for previous_card in previous_trick.cards:
            flat_last_tricks_cards.append(previous_card)

    if input.player_number == 0 or input.player_number == 2:
        flat_last_tricks_cards.append(input.current_trick.cards[0])
        flat_last_tricks_cards.append(input.current_trick.cards[2])
    else:
        flat_last_tricks_cards.append(input.current_trick.cards[1])
        flat_last_tricks_cards.append(input.current_trick.cards[3])

    filtered_last_tricks_cards = list(filter(lambda card: card.suit == input.current_suit and card.ranking_value > max_playable_card.ranking_value, flat_last_tricks_cards))
    
    if len(list(range(max_playable_card.ranking_value,12))) == len(filtered_last_tricks_cards):
        if (
            (input.player_number == 0 or input.player_number == 2) and (card_ranking_on_trick(input.current_trick.cards[1],input) < max_playable_card.ranking_value and card_ranking_on_trick(input.current_trick.cards[3],input) < max_playable_card.ranking_value) 
            or (input.player_number == 1 or input.player_number == 3) and (card_ranking_on_trick(input.current_trick.cards[0],input) < max_playable_card.ranking_value and card_ranking_on_trick(input.current_trick.cards[2],input) < max_playable_card.ranking_value)
        ):
            return max_playable_card
        else:
            if can_cut:
                return min(input.hand.cards,key=attrgetter('ranking_value'))
            return min_playable_card
    else:
        return min_playable_card


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', nargs='?', type=argparse.FileType('r'),
                        default=sys.stdin)

    args = parser.parse_args()

    input = Input(args.infile.readlines())
    card = play(input)
    print(card.rank + card.suit)
