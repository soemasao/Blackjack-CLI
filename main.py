import random

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        return f"[{self.suit} {self.rank}]"

    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

class Deck:
    def __init__(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks]
        random.shuffle(self.cards)

    def deal_card(self):
        return self.cards.pop()

class Hand:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_value(self):
        value = sum(card.get_value() for card in self.cards)
        aces = sum(1 for card in self.cards if card.rank == 'A')
        
        while value > 21 and aces > 0:
            value -= 10
            aces -= 1

        return value

    def display(self, hide_first_card=False):
        if hide_first_card:
            return f"[❓] " + " ".join(str(card) for card in self.cards[1:])
        return " ".join(str(card) for card in self.cards)

def play_round(chips):
    print("\n" + "=" * 40)
    print(f" Total Chip Kamu: ${chips}")
    print("=" * 40)

    # Input taruhan awal
    while True:
        try:
            bet = int(input(f"Masukkan jumlah taruhan (1 - {chips}): $"))
            if 1 <= bet <= chips:
                break
            print(f"Taruhan tidak valid! Harus antara $1 dan ${chips}.")
        except ValueError:
            print("Masukkan angka yang valid!")

    deck = Deck()
    player_hand = Hand()
    dealer_hand = Hand()

    for _ in range(2):
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())

    print(f"\nKartu Dealer : {dealer_hand.display(hide_first_card=True)}")
    print(f"Kartu Kamu   : {player_hand.display()}  (Total: {player_hand.get_value()})")

    # --- FITUR INSURANCE ---
    insurance_bet = 0
    # Kartu terbuka dealer adalah kartu kedua di list dealer_hand.cards (karena kartu pertama disembunyikan)
    dealer_upcard = dealer_hand.cards[1]
    
    if dealer_upcard.rank == 'A':
        max_insurance = bet / 2
        if chips - bet >= max_insurance:
            print("\n⚠️ Dealer menunjukkan kartu ACE!")
            take_insurance = input(f"Beli Insurance senilai ${int(max_insurance)}? (y/n): ").strip().lower()
            if take_insurance == 'y':
                insurance_bet = max_insurance
                print(f"-> Insurance dipasang sebesar ${int(insurance_bet)}.")

    # Cek apakah Dealer Blackjack saat kartu tertutup dibuka
    dealer_has_blackjack = (dealer_hand.get_value() == 21)

    if dealer_upcard.rank == 'A' and dealer_has_blackjack:
        print("\n" + "=" * 40)
        print(f"Dealer membuka kartu: {dealer_hand.display()}")
        print("DEALER DAPAT BLACKJACK!")
        print("=" * 40)

        if insurance_bet > 0:
            payout = insurance_bet * 2
            print(f"✅ Insurance KAMU MENANG! Kamu dibayar ${int(payout)}.")
            chips += payout  # Menang insurance 2:1
        
        if player_hand.get_value() == 21:
            print("Pemain juga Blackjack! Taruhan utama SERI (Push).")
        else:
            print(f"❌ Taruhan utama kalah. Kamu kehilangan ${bet}.")
            chips -= bet

        return int(chips)
    
    elif insurance_bet > 0:
        print("-> Dealer TIDAK Blackjack. Uang Insurance hangus.")
        chips -= insurance_bet

    # --- GILIRAN PLAYER ---
    player_busted = False
    
    while True:
        if player_hand.get_value() == 21:
            print("\nBLACKJACK!")
            break
        elif player_hand.get_value() > 21:
            print("\nBUST! Total kartu kamu melebihi 21.")
            player_busted = True
            break

        can_double = (len(player_hand.cards) == 2) and (chips >= bet * 2)

        if can_double:
            prompt = "\nPilih aksi ([1] Hit / [2] Stand / [3] Double Down): "
        else:
            prompt = "\nPilih aksi ([1] Hit / [2] Stand): "

        choice = input(prompt).strip()

        if choice == '1':
            player_hand.add_card(deck.deal_card())
            print("-> Kamu memilih HIT!")
            print(f"Kartu Kamu   : {player_hand.display()}  (Total: {player_hand.get_value()})")
        elif choice == '2':
            print("-> Kamu memilih STAND.")
            break
        elif choice == '3' and can_double:
            bet *= 2
            print(f"-> Kamu memilih DOUBLE DOWN! Taruhan naik menjadi ${bet}.")
            player_hand.add_card(deck.deal_card())
            print(f"Kartu Kamu   : {player_hand.display()}  (Total: {player_hand.get_value()})")
            
            if player_hand.get_value() > 21:
                print("\nBUST! Total kartu kamu melebihi 21.")
                player_busted = True
            break
        else:
            print("Pilihan tidak valid.")

    if player_busted:
        print(f"\nKAMU KALAH! Kamu kehilangan ${bet}.")
        return int(chips - bet)

    # --- GILIRAN DEALER ---
    print("\n" + "-" * 40)
    print("Giliran Dealer...")
    print(f"Kartu Dealer : {dealer_hand.display()}  (Total: {dealer_hand.get_value()})")

    while dealer_hand.get_value() < 17:
        print("Dealer memilih HIT...")
        dealer_hand.add_card(deck.deal_card())
        print(f"Kartu Dealer : {dealer_hand.display()}  (Total: {dealer_hand.get_value()})")

    dealer_total = dealer_hand.get_value()
    player_total = player_hand.get_value()

    # --- PENENTUAN PEMENANG ---
    print("\n" + "=" * 40)
    if dealer_total > 21:
        print(f"Dealer BUST ({dealer_total})! KAMU MENANG!")
        chips += bet
        print(f"Kamu mendapatkan ${bet}!")
    elif player_total > dealer_total:
        print(f"HASIL: Kamu ({player_total}) vs Dealer ({dealer_total}) -> KAMU MENANG!")
        chips += bet
        print(f"Kamu mendapatkan ${bet}!")
    elif player_total < dealer_total:
        print(f"HASIL: Kamu ({player_total}) vs Dealer ({dealer_total}) -> DEALER MENANG!")
        chips -= bet
        print(f"Kamu kehilangan ${bet}.")
    else:
        print(f"HASIL: Kamu ({player_total}) vs Dealer ({dealer_total}) -> SERI (PUSH)!")
        print("Taruhan kamu dikembalikan.")

    return int(chips)

def main():
    print("========================================")
    print("        WELCOME TO BLACKJACK CLI        ")
    print("========================================")

    chips = 100

    while chips > 0:
        chips = play_round(chips)

        if chips <= 0:
            print("\n" + "x" * 40)
            print("BANKRUPT! Chip kamu habis. Game Over.")
            print("x" * 40)
            break

        play_again = input("\nMain ronde berikutnya? ([y]/n): ").strip().lower()
        if play_again == 'n':
            print(f"\nTerima kasih sudah bermain! Sisa chip kamu: ${int(chips)}")
            break

if __name__ == "__main__":
    main()