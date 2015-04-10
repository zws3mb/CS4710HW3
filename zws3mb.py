__author__ = 'Zachary'
from negotiator_base import BaseNegotiator
from itertools import permutations
from random import sample

class zws3mb_Negotiator(BaseNegotiator):
    # initialize(self : BaseNegotiator, preferences : list(String), iter_limit : Int)
        # Performs per-round initialization - takes in a list of items, ordered by the item's
        # preferability for this negotiator
        # You can do other work here, but still need to store the preferences
#    def __init__(self):

    def initialize(self, preferences, iter_limit):
        BaseNegotiator.initialize(self,preferences,iter_limit)
        self.round_count=0
        self.first=False
        self.their_offers=[]
        self.their_utilities=[]
        self.our_score=0
        self.their_score=0
        self.offer_space()
        self.last_offer=None
        self.encounter=0


    # make_offer(self : BaseNegotiator, offer : list(String)) --> list(String)
        # Given the opposing negotiator's last offer (represented as an ordered list),
        # return a new offer. If you wish to accept an offer & end negotiations, return the same offer
        # Note: Store a copy of whatever offer you make in self.offer at the end of this method.
    def offer_space(self):
        offerspace=[]
        if len(self.preferences)<7:     #Enumerate the whole space
            for subset in permutations(self.preferences,len(self.preferences)):
                self.offer=subset
                temp=self.utility()
                offerspace.append((subset,temp))

        else:
            for i in range(0,5000):
                self.offer=sample(self.preferences,len(self.preferences))
                temp=self.utility()
                offerspace.append((self.offer,temp))
        offerspace.sort(key=lambda tup:tup[1],reverse=True)
        #print offerspace
        self.my_offerspace=offerspace

    def ith_in_our_space(self,their_offer):
        temp=self.offer
        self.offer=their_offer
        this_util=self.utility()
        self.offer=temp
        for i in range(0,len(self.my_offerspace)):
            off,util=self.my_offerspace[i]
            if off==their_offer:
                return i
            if util<=this_util:
                return i
        return -1;
    def tic_tac_check(self,offer):
        if self.round_count+1==self.iter_limit: #last round
            print 'Last round behavior',
            if self.first:      #We accept/receive this final offer
                if self.their_score>self.our_score:
                    if self.encounter>=3:   #potentially last time we see this opponenet
                        if self.our_score>self.my_offerspace[0][1]:#>len(self.preferences):
                            return self.preferences[:] #spite them
                        else:
                            print 'Try to accept'
                            temp=self.offer
                            self.offer=self.their_offers[len(self.their_offers)-1]
                            val=self.utility()
                            self.offer=temp
                            if val>0:
                                return self.their_offers[len(self.their_offers)-1] #if we aren't hurt by accepting,
                            else:
                                return self.preferences[:]                          # or screw both of us!
                    else:                   #can we manipulate them into being softer?
                        print 'not the last encounter, deny'
                        return self.preferences[:]
                else:
                    print 'Accepted!'
                    return self.their_offers[len(self.their_offers)-1] #we're ahead, can afford to be gracious and accept
            else:               # We make final offer
                if self.their_score >self.our_score:    #been beating usd
                    if not self.agreed:     #They may have spited us:
                        return offer
                    else:
                        print 'Come down some',
                        our_i=self.ith_in_our_space(self.last_offer)
                        return self.my_offerspace[our_i+1][0]  #be ballsy
                else:
                    if self.encounter>=3:
                        our_i=self.ith_in_our_space(self.last_offer)
                        return self.my_offerspace[our_i+1][0]  #be ballsy
                        #return self.preferences[:]
                    else:
                        return offer
        return offer
    def make_offer(self, offer):
        dec_off=None
        if offer==None and self.round_count==0:
            print "I am Negotiator A!"
            self.first=True
            self.offer=self.preferences[:]
            return self.offer
        else:
            self.their_offers.append(offer)
            if len(self.their_offers)>1: #not their first offer
                if self.their_utilities[len(self.their_utilities)-1]<self.their_utilities[len(self.their_utilities)-2]: #coming down
                    their_i=self.ith_in_our_space(offer)
                    last_i=self.ith_in_our_space(self.last_offer)
                    print 'Haggling:'+str(last_i)+' '+str(their_i)
                    if their_i-last_i>0:        #is there room to come down
                        dec_off= self.my_offerspace[last_i+(their_i-last_i)/2][0]
                    else:
                        dec_off=self.my_offerspace[last_i][0]
                else:                   #holding out or wrong direction
                    print 'Being stubborn'
                    dec_off=self.last_offer
            else:   #their first offer
                print 'refuse to budge'
                dec_off=self.preferences[:]
        self.offer=self.tic_tac_check(dec_off)
        self.last_offer=self.offer
        self.round_count+=1
        return self.offer

    # utility(self : BaseNegotiator) --> Float
        # Return the utility given by the last offer - Do not modify this method.
    def utility(self):
        total = len(self.preferences)
        return reduce(lambda points, item: points + ((total / (self.offer.index(item) + 1)) - abs(self.offer.index(item) - self.preferences.index(item))), self.offer, 0)

    # receive_utility(self : BaseNegotiator, utility : Float)
        # Store the utility the other negotiator received from their last offer
    def receive_utility(self, utility):
        self.their_utilities.append(utility)

    # receive_results(self : BaseNegotiator, results : (Boolean, Float, Float, Int))
        # Store the results of the last series of negotiation (points won, success, etc.)
    def receive_results(self, results):
        agreed,neg_a,neg_b,rounds=results
        self.agreed=agreed
        if self.first:
            self.our_score+=neg_a
            self.their_score+=neg_b
        else:
            self.our_score+=neg_b
            self.their_score+=neg_a
        self.first=False
        self.encounter+=1
        self.their_offers=[]
        self.round_count=0

