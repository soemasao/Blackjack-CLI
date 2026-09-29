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

# Class Deck mendukung Multi-Deck (Shoe) & Reshuffle
class Deck:
    def __init__(self, num_decks=6):
        self.num_decks = num_decks
        self.cards = []
        self.build_and_shuffle()

    def build_and_shuffle(self):
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        self.cards = [Card(suit, rank) for suit in suits for rank in ranks] * self.num_decks
        random.shuffle(self.cards)
        print(f"\n🔄 Tumpukan kartu dikocok ulang ({self.num_decks} Deck / {len(self.cards)} kartu).")

    def deal_card(self):
        return self.cards.pop()

    def remaining_cards(self):
        return len(self.cards)

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

# Fungsi untuk memainkan giliran satu Hand (Tangan)
def play_hand(hand, deck, bet, chips, hand_label=""):
    player_busted = False
    current_bet = bet

    while True:
        label_str = f" ({hand_label})" if hand_label else ""
        print(f"\nKartu Kamu{label_str} : {hand.display()}  (Total: {hand.get_value()})")

        if hand.get_value() == 21:
            print(f"BLACKJACK pada {hand_label if hand_label else 'tangan kamu'}!")
            break
        elif hand.get_value() > 21:
            print(f"BUST pada {hand_label if hand_label else 'tangan kamu'}!")
            player_busted = True
            break

        can_double = (len(hand.cards) == 2) and (chips >= current_bet)

        if can_double:
            prompt = "Pilih aksi ([1] Hit / [2] Stand / [3] Double Down): "
        else:
            prompt = "Pilih aksi ([1] Hit / [2] Stand): "

        choice = input(prompt).strip()

        if choice == '1':
            hand.add_card(deck.deal_card())
            print("-> Kamu memilih HIT!")
        elif choice == '2':
            print("-> Kamu memilih STAND.")
            break
        elif choice == '3' and can_double:
            chips -= current_bet
            current_bet *= 2
            print(f"-> Kamu memilih DOUBLE DOWN! Taruhan naik menjadi ${current_bet}.")
            hand.add_card(deck.deal_card())
            print(f"Kartu Kamu{label_str} : {hand.display()}  (Total: {hand.get_value()})")
            
            if hand.get_value() > 21:
                print(f"BUST pada {hand_label if hand_label else 'tangan kamu'}!")
                player_busted = True
            break
        else:
            print("Pilihan tidak valid.")

    return hand, current_bet, chips, player_busted

def play_round(chips, deck):
    # Cek jika sisa kartu di shoe kurang dari 52, maka kocok ulang
    if deck.remaining_cards() < 52:
        deck.build_and_shuffle()

    print("\n" + "=" * 40)
    print(f" Total Chip Kamu: ${chips} | Sisa Kartu di Shoe: {deck.remaining_cards()}")
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

    chips -= bet  # Kurangi taruhan awal dari saldo chip

    player_hand = Hand()
    dealer_hand = Hand()

    for _ in range(2):
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())

    print(f"\nKartu Dealer : {dealer_hand.display(hide_first_card=True)}")
    print(f"Kartu Kamu   : {player_hand.display()}  (Total: {player_hand.get_value()})")

    # --- FITUR INSURANCE ---
    insurance_bet = 0
    dealer_upcard = dealer_hand.cards[1]
    
    if dealer_upcard.rank == 'A' and chips >= (bet / 2):
        max_insurance = bet / 2
        print("\n⚠️ Dealer menunjukkan kartu ACE!")
        take_insurance = input(f"Beli Insurance senilai ${int(max_insurance)}? (y/n): ").strip().lower()
        if take_insurance == 'y':
            insurance_bet = max_insurance
            chips -= insurance_bet
            print(f"-> Insurance dipasang sebesar ${int(insurance_bet)}.")

    dealer_has_blackjack = (dealer_hand.get_value() == 21)

    if dealer_upcard.rank == 'A' and dealer_has_blackjack:
        print("\n" + "=" * 40)
        print(f"Dealer membuka kartu: {dealer_hand.display()}")
        print("DEALER DAPAT BLACKJACK!")
        print("=" * 40)

        if insurance_bet > 0:
            payout = insurance_bet * 3  # Kembalikan taruhan insurance + bayaran 2:1
            print(f"✅ Insurance KAMU MENANG! Kamu dibayar ${int(insurance_bet * 2)}.")
            chips += payout
        
        if player_hand.get_value() == 21:
            print("Pemain juga Blackjack! Taruhan utama SERI (Push).")
            chips += bet
        else:
            print(f"❌ Taruhan utama kalah. Kamu kehilangan ${bet}.")

        return int(chips)
    
    elif insurance_bet > 0:
        print("-> Dealer TIDAK Blackjack. Uang Insurance hangus.")

    # List untuk menampung semua tangan pemain
    player_hands = []

    # --- FITUR SPLIT ---
    can_split = (player_hand.cards[0].get_value() == player_hand.cards[1].get_value()) and (chips >= bet)

    if can_split:
        do_split = input("\nKartu kamu bernilai sama! Lakukan SPLIT? (y/n): ").strip().lower()
        if do_split == 'y':
            chips -= bet  # Kurangi chip untuk tangan kedua
            print(f"-> Kamu memilih SPLIT! Menambah taruhan ${bet} untuk tangan kedua.")

            hand1 = Hand()
            hand1.add_card(player_hand.cards[0])
            hand1.add_card(deck.deal_card())

            hand2 = Hand()
            hand2.add_card(player_hand.cards[1])
            hand2.add_card(deck.deal_card())

            print("\n--- Memainkan Tangan 1 ---")
            hand1, bet1, chips, bust1 = play_hand(hand1, deck, bet, chips, "Tangan 1")
            player_hands.append((hand1, bet1, bust1, "Tangan 1"))

            print("\n--- Memainkan Tangan 2 ---")
            hand2, bet2, chips, bust2 = play_hand(hand2, deck, bet, chips, "Tangan 2")
            player_hands.append((hand2, bet2, bust2, "Tangan 2"))

    if not player_hands:
        hand, final_bet, chips, is_bust = play_hand(player_hand, deck, bet, chips)
        player_hands.append((hand, final_bet, is_bust, "Utama"))

    # --- GILIRAN DEALER ---
    all_busted = all(busted for _, _, busted, _ in player_hands)

    if not all_busted:
        print("\n" + "-" * 40)
        print("Giliran Dealer...")
        print(f"Kartu Dealer : {dealer_hand.display()}  (Total: {dealer_hand.get_value()})")

        while dealer_hand.get_value() < 17:
            print("Dealer memilih HIT...")
            dealer_hand.add_card(deck.deal_card())
            print(f"Kartu Dealer : {dealer_hand.display()}  (Total: {dealer_hand.get_value()})")

    dealer_total = dealer_hand.get_value()

    # --- PENENTUAN PEMENANG ---
    print("\n" + "=" * 40)
    print("              HASIL RONDE              ")
    print("=" * 40)

    for hand, hand_bet, is_bust, label in player_hands:
        hand_val = hand.get_value()
        prefix = f"[{label}] " if len(player_hands) > 1 else ""

        if is_bust:
            print(f"{prefix}BUST ({hand_val})! Kamu kehilangan ${hand_bet}.")
        elif dealer_total > 21:
            print(f"{prefix}Dealer BUST! KAMU MENANG ${hand_bet}!")
            chips += hand_bet * 2
        elif hand_val > dealer_total:
            print(f"{prefix}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> KAMU MENANG ${hand_bet}!")
            chips += hand_bet * 2
        elif hand_val < dealer_total:
            print(f"{prefix}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> KALAH! Kehilangan ${hand_bet}.")
        else:
            print(f"{prefix}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> SERI (PUSH)! Taruhan dikembalikan.")
            chips += hand_bet

    return int(chips)

def main():
    print("========================================")
    print("        WELCOME TO BLACKJACK CLI        ")
    print("========================================")

    chips = 100
    deck = Deck(num_decks=6)  # Menggunakan 6 Multi-Deck (Shoe)

    while chips > 0:
        chips = play_round(chips, deck)

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