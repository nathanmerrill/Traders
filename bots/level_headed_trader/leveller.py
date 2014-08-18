import sys

def current_goods():
    print "G"
    return parse_goods(readline())

def parse_goods(good_string):
    return dict([(a, int(b))
                 for b, a in [product.split("-")
                              for product in good_string.split(",")]])

def get_minimum(goods):
    cur_min = 200
    min_good = "X"
    for good, amount in goods.items():
        if amount < cur_min:
            min_good = good
            cur_min = amount
    return min_good

def get_maximum(goods):
    cur_max = -1
    max_good = "X"
    for good, amount in goods.items():
        if amount > cur_max:
            max_good = good
            cur_max = amount
    return max_good

def add_goods(x, y):
    return {k: int(x.get(k, 0)) + int(y.get(k, 0)) for k in set(x) | set(y)}

def readline():
    line = sys.stdin.readline().strip()
    if line == 'Q' or not line:
        exit()
    return line

def output_goods(goods):
    print ",".join([str(amount)+"-"+good for good, amount in goods.items()])

def output_good(good, amount):
    print str(amount)+"-"+good

def current_turn_is(turn):
    print "T"
    return readline() == turn

turns = MARKET, PRODUCE, TRADING, SKIPPED = "M", "P", "T", "S"
market_options = PURCHASE, SELL = "P", "S"
items = APRICOTS, BOARS, CANARIES, DAFFODILS, EARWIGS, NOTHING = "A", "B", "C", "D", "E", "X"

productivity = parse_goods(readline())
while True:
    product_to_produce = get_minimum(current_goods())
    print product_to_produce
    while current_turn_is(MARKET):
        print SELL
        if readline() != SKIPPED:
            maximum = get_maximum(current_goods())
            goods = {"A": 1, "B": 1, "C": 1, "D": 1, "E": 1}
            del goods[maximum]
            output_good(maximum, 1)
            output_goods(goods)
