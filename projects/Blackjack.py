import sys
import os
import pygame

from pygame.locals import *
# some resource related warnings
if not pygame.font: print('Warning, fonts disabled')
if not pygame.mixer: print('Warning, sound disabled')

# initializations
pygame.init()

try:
    import simplegui
except ImportError:
    import SimpleGUICS2Pygame.simpleguics2pygame as simplegui
    
import random

def resource_path(relative_path):
    try:
    # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# load card sprite - 936x384 - source: jfitz.com
CARD_SIZE = (72, 96)
CARD_CENTER = (36, 48)
card_images = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/cards_jfitz.png")

CARD_BACK_SIZE = (72, 96)
CARD_BACK_CENTER = (36, 48)
card_back = simplegui.load_image("http://storage.googleapis.com/codeskulptor-assets/card_jfitz_back.png")    

# initialize some useful global variables
in_play = False
outcome = ""
score = 100
bet = 1

# define globals for cards
SUITS = ('C', 'S', 'H', 'D')
RANKS = ('A', '2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K')
VALUES = {'A':1, '2':2, '3':3, '4':4, '5':5, '6':6, '7':7, '8':8, '9':9, 'T':10, 'J':10, 'Q':10, 'K':10}

# define card class
class Card:
    def __init__(self, suit, rank):
        if (suit in SUITS) and (rank in RANKS):
            self.suit = suit
            self.rank = rank
        else:
            self.suit = None
            self.rank = None
            print ("Invalid card: ", suit, rank)

    def __str__(self):
        return self.suit + self.rank

    def get_suit(self):
        return self.suit

    def get_rank(self):
        return self.rank

    def draw(self, canvas, pos):
        card_loc = (CARD_CENTER[0] + CARD_SIZE[0] * RANKS.index(self.rank), 
                    CARD_CENTER[1] + CARD_SIZE[1] * SUITS.index(self.suit))
        canvas.draw_image(card_images, card_loc, CARD_SIZE, 
                          [pos[0] + CARD_CENTER[0], pos[1] + CARD_CENTER[1]], 
                          CARD_SIZE)
        
# define hand class
class Hand:
    def __init__(self):
        self.hand = [] #none at first

    def __str__(self):
        string_hand = ""
        for card in self.hand:
            string_hand = "Hand contains " + string_hand + " " + str(card)
        return string_hand

    def add_card(self, card):
        self.hand.append(card)

    def get_value(self):
        value = 0
        num_ace = 0
        for c in self.hand:
            value += VALUES.get(c.get_rank())
            if c.get_rank() == "A":
                num_ace += 1
        if num_ace > 0 and (value+10) <= 21:
            value += 10
        return value
   
    def draw(self, canvas, pos):
        for c in self.hand:
            card_location = (CARD_CENTER[0] + CARD_SIZE[0]*RANKS.index(c.rank), 
                    CARD_CENTER[1] + CARD_SIZE[1]*SUITS.index(c.suit))
            canvas.draw_image(card_images, card_location, CARD_SIZE, 
                              [pos[0] + CARD_CENTER[0] + 73 * self.hand.index(c), 
                               pos[1] + CARD_CENTER[1]],
                              CARD_SIZE)
        
# define deck class 
class Deck:
    def __init__(self):
        self.deck = [Card(cshd, kqj) for cshd in SUITS for kqj in RANKS]
        
    def shuffle(self):
        random.shuffle(self.deck)

    def deal_card(self):
        self.card = self.deck[0]
        self.deck.remove(self.card)
        return self.card
       
#define event handlers for buttons
def deal():
    global outcome, in_play, score, myhand, computerhand, newdeck
    if in_play is True:
        score -= bet
    myhand = Hand()
    computerhand = Hand()
    newdeck = Deck()
    newdeck.shuffle()
    myhand.add_card(newdeck.deal_card())
    myhand.add_card(newdeck.deal_card())
    computerhand.add_card(newdeck.deal_card())
    computerhand.add_card(newdeck.deal_card())
    outcome = "Choose HIT or STAND"
    in_play = True

def hit():
    global outcome, in_play, score, myhand, computerhand, newdeck
    if in_play:
        myhand.add_card(newdeck.deal_card())
        # if busted, assign a message to outcome, update in_play and score
        if myhand.get_value() > 21:
            outcome = "BUSTED. New DEAL? "
            score -= bet
            in_play = False
        else:
            outcome = "Choose HIT or STAND"
   
def stand():
    global outcome, in_play, score, myhand, computerhand
    if in_play:
        in_play = False
        if myhand.get_value() > 21:
            outcome = "BUSTED. New DEAL? "
            score -= bet
            in_play = False
        else:
            while computerhand.get_value() < 17:
                computerhand.add_card(newdeck.deal_card())
            else:
                if computerhand.get_value() > 21:
                    outcome = "Dealer busted. You WIN! New DEAL? "
                    score += bet
                elif computerhand.get_value() >= myhand.get_value():
                    outcome = "Dealer wins. You LOSE! New DEAL? "
                    score -= bet
                else:
                    outcome = "You WIN! New DEAL? "
                    score += bet
  
    
# draw handler    
def draw(canvas):
    #draw hand for both player and dealer
    computerhand.draw(canvas, [100, 175])    
    myhand.draw(canvas, [100, 370])
    if in_play:
        canvas.draw_image(card_back, CARD_BACK_CENTER, 
                          CARD_BACK_SIZE, 
                          [100 + 36, 175 + 48], 
                          CARD_SIZE)    
    #draw text and scoring
    canvas.draw_text(outcome, [100,125],25,"Blue")
    canvas.draw_text("Total Funds: $"+str(score),[400,30],25,"Silver")
    canvas.draw_text("Bet: $" + str(bet), [420,60],20,"Silver")
    canvas.draw_text("BLACK JACK",[120,50],40,"Gold")
    canvas.draw_text('Current Card Value: ' + str(myhand.get_value()),
                     [100, 340], 20, "Black")

#bet mechanism
def increase():
    global bet
    if in_play is False:
        bet += 1

def decrease():
    global bet
    if in_play is False and bet > 1:
        bet -= 1
    
# initialization frame
frame = simplegui.create_frame("Blackjack", 600, 500)
frame.set_canvas_background("Green")

#create buttons and canvas callback
frame.add_button("DEAL", deal, 200)
frame.add_button("HIT",  hit, 200)
frame.add_button("STAND", stand, 200)
frame.add_button("Increase Bet", increase, 100)
frame.add_button("Decrease Bet", decrease, 100)
frame.set_draw_handler(draw)

# get things rolling
deal()
frame.start()


# call this function to start everything
# could be thought of as the implemntation of the CodeSkulptor frame .start() method.
def main():
    # initialize loop until quit variable
    running = True
    
    # create our FPS timer clock
    clock = pygame.time.Clock()    

#---------------------------Frame is now Running-----------------------------------------
    
    # doing the infinte loop until quit -- the game is running
    while running:
        
        # event queue iteration
        for event in pygame.event.get():
            
            # window GUI ('x' the window)
            if event.type == pygame.QUIT:
                running = False

            # input - key and mouse event handlers
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass
                # just respond to left mouse clicks
                #if pygame.mouse.get_pressed()[0]:
                    #mc_handler(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                pass
                #kd_handler(event.key)

            # timers
            #elif event.type == timer_example:
                #t_example()      
                
        # the call to the draw handler
        draw_handler(canvas)
        
        # FPS limit to 60 -- essentially, setting the draw handler timing
        # it micro pauses so while loop only runs 60 times a second max.
        clock.tick(60)
        
#-----------------------------Frame Stops------------------------------------------

    # quit game -- we're now allowed to hit the quit call
    pygame.quit ()
