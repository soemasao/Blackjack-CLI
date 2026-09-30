import random

# Definisi Kode Warna ANSI untuk Terminal
class Color:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    def display_card(self, owner="player"):
        suit_color = Color.RED if self.suit in ['♥', '♦'] else Color.WHITE
        border_color = Color.YELLOW if owner == "dealer" else Color.CYAN
        return f"{border_color}[{suit_color}{self.suit} {self.rank}{border_color}]{Color.RESET}"

    def get_value(self):
        if self.rank in ['J', 'Q', 'K']:
            return 10
        elif self.rank == 'A':
            return 11
        else:
            return int(self.rank)

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
        print(f"\n{Color.GREEN}🔄 Tumpukan kartu dikocok ulang ({self.num_decks} Deck / {len(self.cards)} kartu).{Color.RESET}")

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

    def is_natural_blackjack(self):
        return len(self.cards) == 2 and self.get_value() == 21

    def display(self, hide_first_card=False, owner="player"):
        if hide_first_card:
            hidden_symbol = f"{Color.YELLOW}[❓]{Color.RESET}"
            return f"{hidden_symbol} " + " ".join(card.display_card(owner) for card in self.cards[1:])
        return " ".join(card.display_card(owner) for card in self.cards)

def play_hand(hand, deck, bet, chips, hand_label=""):
    player_busted = False
    current_bet = bet

    while True:
        label_str = f" ({hand_label})" if hand_label else ""
        print(f"\n{Color.CYAN}{Color.BOLD}Kartu Kamu{label_str} : {hand.display(owner='player')}  {Color.WHITE}(Total: {hand.get_value()}){Color.RESET}")

        if hand.get_value() == 21:
            print(f"{Color.MAGENTA}{Color.BOLD}★ Total kamu 21 pada {hand_label if hand_label else 'tangan kamu'}! ★{Color.RESET}")
            break
        elif hand.get_value() > 21:
            print(f"{Color.RED}{Color.BOLD}💥 BUST pada {hand_label if hand_label else 'tangan kamu'}!{Color.RESET}")
            player_busted = True
            break

        can_double = (len(hand.cards) == 2) and (chips >= current_bet)

        if can_double:
            prompt = f"{Color.WHITE}Pilih aksi ([1] Hit / [2] Stand / [3] Double Down): {Color.RESET}"
        else:
            prompt = f"{Color.WHITE}Pilih aksi ([1] Hit / [2] Stand): {Color.RESET}"

        choice = input(prompt).strip()

        if choice == '1':
            hand.add_card(deck.deal_card())
            print(f"{Color.CYAN}-> Kamu memilih HIT!{Color.RESET}")
        elif choice == '2':
            print(f"{Color.CYAN}-> Kamu memilih STAND.{Color.RESET}")
            break
        elif choice == '3' and can_double:
            chips -= current_bet
            current_bet *= 2
            print(f"{Color.MAGENTA}-> Kamu memilih DOUBLE DOWN! Taruhan naik menjadi ${current_bet}.{Color.RESET}")
            hand.add_card(deck.deal_card())
            print(f"{Color.CYAN}{Color.BOLD}Kartu Kamu{label_str} : {hand.display(owner='player')}  {Color.WHITE}(Total: {hand.get_value()}){Color.RESET}")
            
            if hand.get_value() > 21:
                print(f"{Color.RED}{Color.BOLD}💥 BUST pada {hand_label if hand_label else 'tangan kamu'}!{Color.RESET}")
                player_busted = True
            break
        else:
            print(f"{Color.RED}Pilihan tidak valid.{Color.RESET}")

    return hand, current_bet, chips, player_busted

def play_round(chips, deck):
    if deck.remaining_cards() < 52:
        deck.build_and_shuffle()

    print("\n" + Color.GREEN + "=" * 45 + Color.RESET)
    print(f"{Color.YELLOW}{Color.BOLD} 💰 Total Chip: ${chips}{Color.RESET} | {Color.WHITE}🎴 Sisa Kartu: {deck.remaining_cards()}{Color.RESET}")
    print(Color.GREEN + "=" * 45 + Color.RESET)

    while True:
        try:
            bet = int(input(f"{Color.YELLOW}Masukkan jumlah taruhan (1 - {chips}): ${Color.RESET}"))
            if 1 <= bet <= chips:
                break
            print(f"{Color.RED}Taruhan tidak valid! Harus antara $1 dan ${chips}.{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}Masukkan angka yang valid!{Color.RESET}")

    chips -= bet

    player_hand = Hand()
    dealer_hand = Hand()

    for _ in range(2):
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())

    print(f"\n{Color.YELLOW}{Color.BOLD}Kartu Dealer : {dealer_hand.display(hide_first_card=True, owner='dealer')}{Color.RESET}")
    print(f"{Color.CYAN}{Color.BOLD}Kartu Kamu   : {player_hand.display(owner='player')}  {Color.WHITE}(Total: {player_hand.get_value()}){Color.RESET}")

    # --- PERIKSA NATURAL BLACKJACK KEDUA PIHAK ---
    player_natural = player_hand.is_natural_blackjack()
    dealer_natural = dealer_hand.is_natural_blackjack()

    # --- FITUR INSURANCE (Kalo Dealer Ace) ---
    insurance_bet = 0
    dealer_upcard = dealer_hand.cards[1]
    
    if dealer_upcard.rank == 'A' and chips >= (bet / 2) and not player_natural:
        max_insurance = bet / 2
        print(f"\n{Color.YELLOW}⚠️ Dealer menunjukkan kartu ACE!{Color.RESET}")
        take_insurance = input(f"Beli Insurance senilai ${int(max_insurance)}? (y/n): ").strip().lower()
        if take_insurance == 'y':
            insurance_bet = max_insurance
            chips -= insurance_bet
            print(f"{Color.CYAN}-> Insurance dipasang sebesar ${int(insurance_bet)}.{Color.RESET}")

    # Penanganan Kasus Natural Blackjack
    if player_natural or dealer_natural:
        print("\n" + Color.GREEN + "=" * 45 + Color.RESET)
        print(f"{Color.YELLOW}Dealer membuka kartu: {dealer_hand.display(owner='dealer')}{Color.RESET}")

        if player_natural and dealer_natural:
            print(f"{Color.YELLOW}{Color.BOLD}KEDUA PIHAK NATURAL BLACKJACK! Hasil Seri (Push). Taruhan dikembalikan.{Color.RESET}")
            chips += bet
        elif player_natural:
            payout = int(bet * 1.5)  # PAYOUT 3:2 (1.5x)
            print(f"{Color.MAGENTA}{Color.BOLD}★ NATURAL BLACKJACK! KAMU MENANG (PAYOUT 3:2)! ★{Color.RESET}")
            print(f"{Color.GREEN}Keuntungan: ${payout} (Total didapat: ${bet + payout}){Color.RESET}")
            chips += bet + payout
        else:
            print(f"{Color.RED}{Color.BOLD}DEALER DAPAT NATURAL BLACKJACK! KAMU KALAH!{Color.RESET}")
            if insurance_bet > 0:
                print(f"{Color.GREEN}✅ Insurance Menang! Dibayar ${int(insurance_bet * 2)}.{Color.RESET}")
                chips += int(insurance_bet * 3)

        print(Color.GREEN + "=" * 45 + Color.RESET)
        return int(chips)

    if insurance_bet > 0:
        print(f"{Color.YELLOW}-> Dealer TIDAK Blackjack. Uang Insurance hangus.{Color.RESET}")

    player_hands = []

    # --- FITUR SPLIT ---
    can_split = (player_hand.cards[0].get_value() == player_hand.cards[1].get_value()) and (chips >= bet)

    if can_split:
        do_split = input(f"\n{Color.MAGENTA}Kartu kamu bernilai sama! Lakukan SPLIT? (y/n): {Color.RESET}").strip().lower()
        if do_split == 'y':
            chips -= bet
            print(f"{Color.MAGENTA}-> Kamu memilih SPLIT! Menambah taruhan ${bet} untuk tangan kedua.{Color.RESET}")

            hand1 = Hand()
            hand1.add_card(player_hand.cards[0])
            hand1.add_card(deck.deal_card())

            hand2 = Hand()
            hand2.add_card(player_hand.cards[1])
            hand2.add_card(deck.deal_card())

            print(f"\n{Color.CYAN}--- Memainkan Tangan 1 ---{Color.RESET}")
            hand1, bet1, chips, bust1 = play_hand(hand1, deck, bet, chips, "Tangan 1")
            player_hands.append((hand1, bet1, bust1, "Tangan 1"))

            print(f"\n{Color.CYAN}--- Memainkan Tangan 2 ---{Color.RESET}")
            hand2, bet2, chips, bust2 = play_hand(hand2, deck, bet, chips, "Tangan 2")
            player_hands.append((hand2, bet2, bust2, "Tangan 2"))

    if not player_hands:
        hand, final_bet, chips, is_bust = play_hand(player_hand, deck, bet, chips)
        player_hands.append((hand, final_bet, is_bust, "Utama"))

    # --- GILIRAN DEALER ---
    all_busted = all(busted for _, _, busted, _ in player_hands)

    if not all_busted:
        print("\n" + Color.YELLOW + "-" * 45 + Color.RESET)
        print(f"{Color.YELLOW}{Color.BOLD}Giliran Dealer...{Color.RESET}")
        print(f"{Color.YELLOW}Kartu Dealer : {dealer_hand.display(owner='dealer')}  {Color.WHITE}(Total: {dealer_hand.get_value()}){Color.RESET}")

        while dealer_hand.get_value() < 17:
            print(f"{Color.YELLOW}Dealer memilih HIT...{Color.RESET}")
            dealer_hand.add_card(deck.deal_card())
            print(f"{Color.YELLOW}Kartu Dealer : {dealer_hand.display(owner='dealer')}  {Color.WHITE}(Total: {dealer_hand.get_value()}){Color.RESET}")

    dealer_total = dealer_hand.get_value()

    # --- PENENTUAN PEMENANG ---
    print("\n" + Color.GREEN + "=" * 45 + Color.RESET)
    print(f"{Color.BOLD}{Color.GREEN}              HASIL RONDE              {Color.RESET}")
    print(Color.GREEN + "=" * 45 + Color.RESET)

    for hand, hand_bet, is_bust, label in player_hands:
        hand_val = hand.get_value()
        prefix = f"[{label}] " if len(player_hands) > 1 else ""

        if is_bust:
            print(f"{prefix}{Color.RED}BUST ({hand_val})! Kamu kehilangan ${hand_bet}.{Color.RESET}")
        elif dealer_total > 21:
            print(f"{prefix}{Color.GREEN}{Color.BOLD}Dealer BUST! KAMU MENANG ${hand_bet}! 🎉{Color.RESET}")
            chips += hand_bet * 2
        elif hand_val > dealer_total:
            print(f"{prefix}{Color.GREEN}{Color.BOLD}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> KAMU MENANG ${hand_bet}! 🎉{Color.RESET}")
            chips += hand_bet * 2
        elif hand_val < dealer_total:
            print(f"{prefix}{Color.RED}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> KALAH! Kehilangan ${hand_bet}.{Color.RESET}")
        else:
            print(f"{prefix}{Color.YELLOW}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> SERI (PUSH)! Taruhan dikembalikan.{Color.RESET}")
            chips += hand_bet

    return int(chips)

def main():
    print(Color.GREEN + "=" * 45 + Color.RESET)
    print(f"{Color.BOLD}{Color.YELLOW}       🃏 WELCOME TO BLACKJACK CLI 🃏       {Color.RESET}")
    print(Color.GREEN + "=" * 45 + Color.RESET)

    chips = 100
    deck = Deck(num_decks=6)

    while chips > 0:
        chips = play_round(chips, deck)

        if chips <= 0:
            print("\n" + Color.RED + "x" * 45 + Color.RESET)
            print(f"{Color.RED}{Color.BOLD}💥 BANKRUPT! Chip kamu habis. Game Over.{Color.RESET}")
            print(Color.RED + "x" * 45 + Color.RESET)
            break

        play_again = input(f"\n{Color.YELLOW}Main ronde berikutnya? ([y]/n): {Color.RESET}").strip().lower()
        if play_again == 'n':
            print(f"\n{Color.GREEN}Terima kasih sudah bermain! Sisa chip kamu: ${int(chips)}{Color.RESET}")
            break

if __name__ == "__main__":
    main()