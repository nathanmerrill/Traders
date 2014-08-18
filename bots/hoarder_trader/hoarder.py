import sys

def current_goods():
    print "G"
    return parse_goods(readline())

def parse_goods(good_string):
    try:
        return dict([(a, int(b))
                     for b, a in [product.split("-")
                                  for product in good_string.split(",")]])
    except:
        raise IOError(good_string)

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

turns = MARKET, PRODUCE, TRADING, SKIPPED = "M", "P", "T","S"
market_options = PURCHASE, SELL = "P", "S"
items = APRICOTS, BOARS, CANARIES, DAFFODILS, EARWIGS, NOTHING = "A", "B", "C", "D", "E", "X"

productivity = parse_goods(readline())
while True:
    product_to_produce = get_minimum(add_goods(current_goods(), productivity))
    print product_to_produce
    while current_turn_is(MARKET):
        print PURCHASE
        if readline() != SKIPPED:
            offered_good = parse_goods(readline())
            accepted_goods = parse_goods(readline())
            minimum = get_minimum(accepted_goods)
            current = current_goods()
            if minimum not in current or current[minimum] < accepted_goods[minimum]:
                print NOTHING
            elif accepted_goods[minimum] < offered_good.values()[0]:
                print minimum
            elif accepted_goods[minimum] == offered_good.values()[0] \
                    and productivity[minimum] > productivity[offered_good.keys()[0]]:
                print minimum
            else:
                print NOTHING
