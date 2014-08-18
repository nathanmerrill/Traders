import sys
import subprocess
import os
import random
import select
import time
import copy
import shlex

debug = __debug__ #True by default, False if -O is passed to python.
                  #Debug being true will print out communication to/from bot
                  #Debug being false will execute the program for 50 games,
                  #and create 5 duplicates of each bot
total_points = 30
min_points = 3
num_trades = 50
amount_to_eat = 2
num_products = 5
good_letters = [chr(ord("A")+x) for x in xrange(num_products)]
num_games = 1 if debug else 50
num_player_copies = 1 if debug else 5


class Communicator(object):
    ON_POSIX = 'posix' in sys.builtin_module_names
    WINDOWS = False
    try:
        select.poll()
        from interruptingcow import timeout
    except:
        WINDOWS = True
        pass

    @classmethod
    def read_bot_list(cls):
        players = []
        for d in os.listdir(r"bots/"):
            try:
                f = open("bots/"+d+"/command.txt", 'r')
            except IOError:
                continue
            commands = f.read().splitlines()
            f.close()
            if commands:
                for command in commands[0:-1]:
                    subprocess.call(command.split(" "), cwd="bots/"+d+"/")
                if cls.WINDOWS:
                    commands[-1]=commands[-1].replace("./", "bots/"+d+"/")
                no_print = os.path.isfile("bots/"+d+"/noprint")
                players.append(Communicator(d, commands[-1], no_print))
        return players

    def __init__(self, bot_name, command, no_print):
        self.name = bot_name
        self.no_print = no_print
        self.process = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE,
                                        stdin=subprocess.PIPE, bufsize=1,
                                        close_fds=Communicator.ON_POSIX,
                                        cwd="bots/"+self.name+"/", shell=True)
        if not Communicator.WINDOWS:
            self.pollin = select.poll()
            self.pollin.register(self.process.stdin, select.POLLOUT)

    def get_response(self):
        if Communicator.WINDOWS:
            message = self.process.stdout.readline()
            if debug and not self.no_print:
                print "got message from "+self.name+" : "+message
            return message

        if debug and not self.no_print: print "waiting for response from " + self.name
        try:
            with Communicator.timeout(self.time_limit, exception=RuntimeError):
                response = self.process.stdout.readline()
                if debug and not self.no_print: print "got response from " + \
                                    self.name + " : " + response.strip()
                return response
        except RuntimeError:
            if debug and not self.no_print: print "gave up on " + self.name
            raise RuntimeError(self.name+
                               " didn't produce a response within one second")

    def send_message(self, message):
        if not message:
            raise IOError("Bad Message")
        message = str(message)
        if debug and not self.no_print :
            print "send message to " + self.name + " : " + message
        if Communicator.WINDOWS:
            self.process.stdin.write(message+"\n")
            self.process.stdin.flush()
            return
        try:
            with Communicator.timeout(self.time_limit, exception=RuntimeError):
                while not self.pollin.poll(0):
                    time.sleep(0.1)
                self.process.stdin.write(message+"\n")
                if debug and not self.no_print: print "sent message to " + self.name
        except RuntimeError:
            if debug and not self.no_print: print "gave up on " + self.name
            raise RuntimeError(self.name+
                               " didn't accept a message within one second")


class Trader(object):
    MarketActions = LeaveMarket, Buy, Sell = range(3)

    def __init__(self, communicator, base_productivity):
        self.communicator = communicator
        offsets = range(-1*int(num_products/2), num_products/2+1)
        random.shuffle(offsets)
        self.productivity = Goods(
            goods=[Good(index=i, amount=a[0]+a[1])
                   for i, a in enumerate(zip(base_productivity, offsets))])
        self.total_goods = Goods(goods=[Good(index=i, amount=10)
                                        for i in xrange(num_products)])
        self.new_goods = Goods()
        self.to_sell = 0
        self.alive = True
        self.years_lived = 0
        self.communicator.send_message(",".join([str(a) for a in self.productivity]))

    def produce(self):
        product = self.prompt("", "P")
        try:
            new_good = self.productivity[product]
        except:
            raise
        self.new_goods += new_good
        self.total_goods += new_good

    def market(self, market_size):
        return {
            "L": Trader.LeaveMarket,
            "P": Trader.Buy,
            "S": Trader.Sell}.get(self.prompt("", "M", market_size=market_size))

    def sell(self, buyer, market_size):
        seller = self
        seller_good = Good.parse(seller.prompt(
            "", "T", player_id=id(buyer), market_size=market_size))
        if seller.total_goods < seller_good:
            print seller.communicator.name + " wanted to sell too much"
            return
        if seller_good.amount <= 0:
            print seller.communicator.name + " wanted to sell too few"
            return
        products_accepts = Goods.parse(seller.prompt(
            "", "T", player_id=id(buyer), market_size=market_size))
        if not products_accepts:
            print seller.communicator.name +" didn't accept any products"
            return
        for product in products_accepts:
            if product.amount < 0:
                print seller.communicator.name +" accepted a negative product"
                return
        buyer.communicator.send_message(seller_good)
        to_buy = buyer.prompt(products_accepts, "T",
                              player_id=id(seller), market_size=market_size)
        if to_buy == "X":
            return
        buyer_good = products_accepts[to_buy]
        if buyer.total_goods < buyer_good:
            print buyer.communicator.name + " tried to trade too much"
            return
        seller.transfer_good_to(buyer, seller_good)
        buyer.transfer_good_to(seller, buyer_good)

    def transfer_good_to(self, trader, good):
        self.total_goods -= good
        trader.total_goods += good
        if self.new_goods[good] < good:
            trader.new_goods += self.new_goods[good]
            self.new_goods[good] = 0
        else:
            self.new_goods -= good
            trader.new_goods += good

    def eat(self):
        self.total_goods += [Good(i, -1*amount_to_eat)
                             for i in xrange(num_products)]
        self.new_goods = Goods()
        for good in self.total_goods:
            if good.amount < 0:
                self.alive = False
                self.communicator.send_message("Q")
        self.years_lived += 1

    def prompt(self, message, phase, market_size=None, player_id=None):
        response = None
        if str(message):
            self.communicator.send_message(str(message))
        while True:
            response = self.communicator.get_response().strip()
            if not response:
                raise IOError("Empty response from "+self.communicator.name)
            replies = {
                "G": self.total_goods,
                "N": self.new_goods,
                "T": phase,
                "I": player_id,
                "M": market_size}
            if response in replies:
                if replies[response] is None:
                    raise IOError("Input not allowed at this time")
                else:
                    self.communicator.send_message(str(replies[response]))
                continue
            break
        return response


class Good(object):

    def __init__(self, index, amount=1):
        self.index = index
        self.amount = amount

    def __str__(self):
        return str(str(self.amount)+"-"+chr(self.index+ord("A")))

    def __cmp__(self, other):
        if isinstance(other, Goods):
            return self.amount.__cmp__(other[chr(self.index+ord("A"))].amount)
        else:
            return self.amount.__cmp__(other.amount)

    @staticmethod
    def parse(string):
        amount, letter = tuple(string.split("-"))
        return Good(ord(letter.upper())-ord("A"), int(amount))


class Goods(object):
    def __init__(self, goods=[Good(index=i, amount=0) for i in xrange(num_products)]):
        self.goods = goods[:]

    def __iter__(self):
        return iter(self.goods)

    def __add__(self, other):
        s = copy.deepcopy(self)
        if isinstance(other, Good):
            s.goods[other.index].amount += other.amount
            return s
        if isinstance(other, basestring):
            other = Goods.parse(other)
        for a in other:
            s += a
        return s

    def __sub__(self, other):
        s = copy.deepcopy(self)
        if isinstance(other, Good):
            s.goods[other.index].amount -= other.amount
            return s
        if isinstance(other, basestring):
            other = Goods.parse(other)
        for a in other:
            s -= a
        return s

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.goods[ord(item) - ord("A")]
        else:
            return self.goods[item.index]

    def __setitem__(self, key, value):
        if isinstance(key, str):
            self.goods[ord(key) - ord("A")].amount = value
        else:
            self.goods[key.index].amount = value

    def __str__(self):
        return ",".join([str(good) for good in self.goods if good.amount])

    def __nonzero__(self):
        return bool(self.goods)

    @staticmethod
    def parse(string):
        goods = Goods()
        for good in string.split(","):
            goods += Good.parse(good)
        return goods


def kill_traders():
    alive_traders = traders[:]
    while alive_traders:
        for trader in alive_traders:
            trader.produce()
        market_traders = alive_traders[:]
        for trade in xrange(num_trades):
            sellers = []
            buyers = []
            for trader in market_traders[:]:
                choice = trader.market(len(market_traders))
                if choice == Trader.Buy:
                    buyers.append(trader)
                elif choice == Trader.Sell:
                    sellers.append(trader)
                else:
                    market_traders.remove(trader)
            random.shuffle(buyers)
            random.shuffle(sellers)
            for seller, buyer in zip(sellers, buyers):
                seller.communicator.send_message("T")
                buyer.communicator.send_message("T")
                seller.sell(buyer, len(market_traders))
            extras = []
            if len(sellers) > len(buyers):
                extras = sellers[len(buyers):]
            elif len(buyers) > len(sellers):
                extras = buyers[len(sellers):]
            for extra in extras:
                extra.communicator.send_message("S")

        for trader in alive_traders[:]:
            trader.eat()
            if not trader.alive:
                alive_traders.remove(trader)

if __name__ == "__main__":
    total_scores = {}
    for game in xrange(num_games):
        if not debug:
            print "Game "+str(game)
        validated = False
        while not validated:
            splits = sorted([random.randrange(total_points)
                             for x in xrange(num_products-1)])
            splits.insert(0, 0)
            splits.append(total_points)
            for split, next_split in zip(splits, splits[1:]):
                if next_split - split < min_points:
                    break
            else:
                validated = True
        base_productivity = [next_split-split
                             for split, next_split in zip(splits, splits[1:])]
        traders = []
        for _ in xrange(num_player_copies):
            traders.extend([Trader(communicator=communicator,
                                   base_productivity=base_productivity)
                            for communicator in Communicator.read_bot_list()])
        kill_traders()
        for trader in traders:
            if trader.communicator.name not in total_scores:
                total_scores[trader.communicator.name] = trader.years_lived
            else:
                total_scores[trader.communicator.name] += trader.years_lived

    for name in total_scores:
        total_scores[name] /= 1.0*(num_games*num_player_copies)

    for name in total_scores:
        print name + " lived for an average of "+str(total_scores[name])+" years"







