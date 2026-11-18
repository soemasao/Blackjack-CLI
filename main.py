import random
import time

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

def format_money(amount):
    if amount == int(amount):
        return f"${int(amount)}"
    return f"${amount:.2f}"

class Card:
    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank

    # Mengembalikan 5 baris string ASCII art untuk 1 kartu
    def get_art_lines(self, owner="player", hidden=False):
        border = Color.YELLOW if owner == "dealer" else Color.CYAN
        
        if hidden:
            return [
                f"{border}┌───────┐{Color.RESET}",
                f"{border}│ ░░░░░ │{Color.RESET}",
                f"{border}│ ░░░░░ │{Color.RESET}",
                f"{border}│ ░░░░░ │{Color.RESET}",
                f"{border}└───────┘{Color.RESET}"
            ]

        suit_color = Color.RED if self.suit in ['♥', '♦'] else Color.WHITE
        top_rank = f"{self.rank:<2}"
        bot_rank = f"{self.rank:>2}"

        return [
            f"{border}┌───────┐{Color.RESET}",
            f"{border}│ {suit_color}{top_rank}    {border}│{Color.RESET}",
            f"{border}│   {suit_color}{self.suit}   {border}│{Color.RESET}",
            f"{border}│    {suit_color}{bot_rank} {border}│{Color.RESET}",
            f"{border}└───────┘{Color.RESET}"
        ]

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

    # Menggabungkan semua kartu di tangan secara horizontal (berdampingan)
    def display(self, hide_first_card=False, owner="player"):
        if not self.cards:
            return ""
        
        card_arts = []
        for idx, card in enumerate(self.cards):
            is_hidden = (idx == 0 and hide_first_card)
            card_arts.append(card.get_art_lines(owner=owner, hidden=is_hidden))
        
        lines = []
        for row in range(5):
            lines.append(" ".join(art[row] for art in card_arts))
            
        return "\n".join(lines)

def play_hand(hand, deck, bet, chips, hand_label="", is_split_ace=False):
    player_busted = False
    current_bet = float(bet)
    label_str = f" ({hand_label})" if hand_label else ""

    if is_split_ace:
        print(f"\n{Color.CYAN}{Color.BOLD}Kartu Kamu{label_str} {Color.WHITE}(Total: {hand.get_value()}):{Color.RESET}")
        print(hand.display(owner='player'))
        print(f"{Color.YELLOW}⚠️ Split Ace: Hanya diperbolehkan 1 kartu tambahan per tangan.{Color.RESET}")
        if hand.get_value() > 21:
            print(f"{Color.RED}{Color.BOLD}💥 BUST pada {hand_label if hand_label else 'tangan kamu'}!{Color.RESET}")
            player_busted = True
        return hand, current_bet, chips, player_busted

    while True:
        print(f"\n{Color.CYAN}{Color.BOLD}Kartu Kamu{label_str} {Color.WHITE}(Total: {hand.get_value()}):{Color.RESET}")
        print(hand.display(owner='player'))

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
            chips = round(chips - current_bet, 2)
            current_bet = round(current_bet * 2, 2)
            print(f"{Color.MAGENTA}-> Kamu memilih DOUBLE DOWN! Taruhan naik menjadi {format_money(current_bet)}.{Color.RESET}")
            hand.add_card(deck.deal_card())
            print(f"\n{Color.CYAN}{Color.BOLD}Kartu Kamu{label_str} {Color.WHITE}(Total: {hand.get_value()}):{Color.RESET}")
            print(hand.display(owner='player'))
            
            if hand.get_value() > 21:
                print(f"{Color.RED}{Color.BOLD}💥 BUST pada {hand_label if hand_label else 'tangan kamu'}!{Color.RESET}")
                player_busted = True
            break
        else:
            print(f"{Color.RED}Pilihan tidak valid.{Color.RESET}")

    return hand, current_bet, chips, player_busted

def play_round(chips, deck, stats):
    if deck.remaining_cards() < 52:
        deck.build_and_shuffle()

    stats["rounds"] += 1

    print("\n" + Color.GREEN + "=" * 45 + Color.RESET)
    print(f"{Color.YELLOW}{Color.BOLD} 💰 Total Chip: {format_money(chips)}{Color.RESET} | {Color.WHITE}🎴 Sisa Kartu: {deck.remaining_cards()} | Ronde #{stats['rounds']}{Color.RESET}")
    print(Color.GREEN + "=" * 45 + Color.RESET)

    while True:
        try:
            bet_input = float(input(f"{Color.YELLOW}Masukkan jumlah taruhan (1 - {format_money(chips)[1:]}): ${Color.RESET}"))
            bet = round(bet_input, 2)
            if 0.5 <= bet <= chips:
                break
            print(f"{Color.RED}Taruhan tidak valid! Harus antara $0.50 dan {format_money(chips)}.{Color.RESET}")
        except ValueError:
            print(f"{Color.RED}Masukkan angka yang valid!{Color.RESET}")

    chips = round(chips - bet, 2)

    player_hand = Hand()
    dealer_hand = Hand()

    for _ in range(2):
        player_hand.add_card(deck.deal_card())
        dealer_hand.add_card(deck.deal_card())

    print(f"\n{Color.YELLOW}{Color.BOLD}Kartu Dealer :{Color.RESET}")
    print(dealer_hand.display(hide_first_card=True, owner='dealer'))

    player_natural = player_hand.is_natural_blackjack()
    dealer_natural = dealer_hand.is_natural_blackjack()
    dealer_upcard = dealer_hand.cards[1]
    max_insurance = round(bet / 2, 2)
    can_split = (player_hand.cards[0].rank == player_hand.cards[1].rank) and (chips >= bet)

    # Tampilkan kartu pemain lebih awal HANYA jika ada keputusan awal (Blackjack / Insurance / Split)
    need_early_display = (
        player_natural
        or dealer_natural
        or (dealer_upcard.rank == 'A' and chips >= max_insurance)
        or can_split
    )

    if need_early_display:
        print(f"\n{Color.CYAN}{Color.BOLD}Kartu Kamu {Color.WHITE}(Total: {player_hand.get_value()}):{Color.RESET}")
        print(player_hand.display(owner='player'))

    # --- FITUR INSURANCE ---
    insurance_bet = 0.0
    if dealer_upcard.rank == 'A' and chips >= max_insurance and not player_natural:
        print(f"\n{Color.YELLOW}⚠️ Dealer menunjukkan kartu ACE!{Color.RESET}")
        take_insurance = input(f"Beli Insurance senilai {format_money(max_insurance)}? (y/n): ").strip().lower()
        if take_insurance == 'y':
            insurance_bet = max_insurance
            chips = round(chips - insurance_bet, 2)
            print(f"{Color.CYAN}-> Insurance dipasang sebesar {format_money(insurance_bet)}.{Color.RESET}")

    # --- FITUR DEALER PEEK ---
    if dealer_upcard.get_value() in [10, 11]:
        print(f"\n{Color.YELLOW}👀 Dealer mengintip kartu tertutup (Hole Card)...{Color.RESET}")
        time.sleep(1.2)
        if not dealer_natural:
            print(f"{Color.GREEN}✓ Dealer tidak memiliki Blackjack. Permainan berlanjut!{Color.RESET}")
            if insurance_bet > 0:
                print(f"{Color.YELLOW}-> Uang Insurance sebesar {format_money(insurance_bet)} hangus.{Color.RESET}")

    # Penanganan Kasus Natural Blackjack
    if player_natural or dealer_natural:
        print("\n" + Color.GREEN + "=" * 45 + Color.RESET)
        print(f"{Color.YELLOW}{Color.BOLD}Dealer membuka kartu:{Color.RESET}")
        print(dealer_hand.display(owner='dealer'))

        if player_natural and dealer_natural:
            print(f"{Color.YELLOW}{Color.BOLD}KEDUA PIHAK NATURAL BLACKJACK! Hasil Seri (Push). Taruhan dikembalikan.{Color.RESET}")
            chips = round(chips + bet, 2)
            stats["pushes"] += 1
            stats["blackjacks"] += 1
        elif player_natural:
            payout = round(bet * 1.5, 2)
            total_return = round(bet + payout, 2)
            print(f"{Color.MAGENTA}{Color.BOLD}★ NATURAL BLACKJACK! KAMU MENANG (PAYOUT 3:2)! ★{Color.RESET}")
            print(f"{Color.GREEN}Keuntungan: {format_money(payout)} (Total didapat: {format_money(total_return)}){Color.RESET}")
            chips = round(chips + total_return, 2)
            stats["wins"] += 1
            stats["blackjacks"] += 1
        else:
            print(f"{Color.RED}{Color.BOLD}💥 DEALER DAPAT NATURAL BLACKJACK! KAMU KALAH!{Color.RESET}")
            stats["losses"] += 1
            if insurance_bet > 0:
                ins_profit = round(insurance_bet * 2, 2)
                print(f"{Color.GREEN}✅ Insurance Menang! Dibayar {format_money(ins_profit)}.{Color.RESET}")
                chips = round(chips + (insurance_bet * 3), 2)

        print(Color.GREEN + "=" * 45 + Color.RESET)
        return chips

    player_hands = []

    # --- FITUR SPLIT ---
    if can_split:
        do_split = input(f"\n{Color.MAGENTA}Kartu kamu kembar! Lakukan SPLIT? (y/n): {Color.RESET}").strip().lower()
        if do_split == 'y':
            chips = round(chips - bet, 2)
            print(f"{Color.MAGENTA}-> Kamu memilih SPLIT! Menambah taruhan {format_money(bet)} untuk tangan kedua.{Color.RESET}")

            is_ace_split = (player_hand.cards[0].rank == 'A')

            hand1 = Hand()
            hand1.add_card(player_hand.cards[0])
            hand1.add_card(deck.deal_card())

            hand2 = Hand()
            hand2.add_card(player_hand.cards[1])
            hand2.add_card(deck.deal_card())

            print(f"\n{Color.CYAN}--- Memainkan Tangan 1 ---{Color.RESET}")
            hand1, bet1, chips, bust1 = play_hand(hand1, deck, bet, chips, "Tangan 1", is_split_ace=is_ace_split)
            player_hands.append((hand1, bet1, bust1, "Tangan 1"))

            print(f"\n{Color.CYAN}--- Memainkan Tangan 2 ---{Color.RESET}")
            hand2, bet2, chips, bust2 = play_hand(hand2, deck, bet, chips, "Tangan 2", is_split_ace=is_ace_split)
            player_hands.append((hand2, bet2, bust2, "Tangan 2"))

    if not player_hands:
        hand, final_bet, chips, is_bust = play_hand(player_hand, deck, bet, chips)
        player_hands.append((hand, final_bet, is_bust, "Utama"))

    # --- GILIRAN DEALER ---
    all_busted = all(busted for _, _, busted, _ in player_hands)

    if not all_busted:
        print("\n" + Color.YELLOW + "-" * 45 + Color.RESET)
        print(f"{Color.YELLOW}{Color.BOLD}Giliran Dealer...{Color.RESET}")
        time.sleep(0.8)
        print(f"{Color.YELLOW}Kartu Dealer {Color.WHITE}(Total: {dealer_hand.get_value()}):{Color.RESET}")
        print(dealer_hand.display(owner='dealer'))

        while dealer_hand.get_value() < 17:
            time.sleep(0.8)
            print(f"\n{Color.YELLOW}Dealer memilih HIT...{Color.RESET}")
            dealer_hand.add_card(deck.deal_card())
            print(f"{Color.YELLOW}Kartu Dealer {Color.WHITE}(Total: {dealer_hand.get_value()}):{Color.RESET}")
            print(dealer_hand.display(owner='dealer'))

    dealer_total = dealer_hand.get_value()

    # --- PENENTUAN PEMENANG & UPDATE STATISTIK ---
    print("\n" + Color.GREEN + "=" * 45 + Color.RESET)
    print(f"{Color.BOLD}{Color.GREEN}              HASIL RONDE              {Color.RESET}")
    print(Color.GREEN + "=" * 45 + Color.RESET)

    for hand, hand_bet, is_bust, label in player_hands:
        hand_val = hand.get_value()
        prefix = f"[{label}] " if len(player_hands) > 1 else ""

        if is_bust:
            print(f"{prefix}{Color.RED}BUST ({hand_val})! Kamu kehilangan {format_money(hand_bet)}.{Color.RESET}")
            stats["losses"] += 1
        elif dealer_total > 21:
            print(f"{prefix}{Color.GREEN}{Color.BOLD}Dealer BUST! KAMU MENANG {format_money(hand_bet)}! 🎉{Color.RESET}")
            chips = round(chips + (hand_bet * 2), 2)
            stats["wins"] += 1
        elif hand_val > dealer_total:
            print(f"{prefix}{Color.GREEN}{Color.BOLD}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> KAMU MENANG {format_money(hand_bet)}! 🎉{Color.RESET}")
            chips = round(chips + (hand_bet * 2), 2)
            stats["wins"] += 1
        elif hand_val < dealer_total:
            print(f"{prefix}{Color.RED}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> KALAH! Kehilangan {format_money(hand_bet)}.{Color.RESET}")
            stats["losses"] += 1
        else:
            print(f"{prefix}{Color.YELLOW}Kamu ({hand_val}) vs Dealer ({dealer_total}) -> SERI (PUSH)! Taruhan dikembalikan.{Color.RESET}")
            chips = round(chips + hand_bet, 2)
            stats["pushes"] += 1

    return chips

def display_stats(stats, final_chips, initial_chips=100.0):
    total_hands = stats["wins"] + stats["losses"] + stats["pushes"]
    win_rate = (stats["wins"] / total_hands * 100) if total_hands > 0 else 0.0
    net_profit = round(final_chips - initial_chips, 2)

    print("\n" + Color.CYAN + "=" * 45 + Color.RESET)
    print(f"{Color.BOLD}{Color.CYAN}          📊 STATISTIK SESI BERMAIN 📊         {Color.RESET}")
    print(Color.CYAN + "=" * 45 + Color.RESET)
    print(f"{Color.WHITE}Total Ronde Dimainkan : {Color.BOLD}{stats['rounds']}{Color.RESET}")
    print(f"{Color.GREEN}Menang (Wins)         : {Color.BOLD}{stats['wins']}{Color.RESET}")
    print(f"{Color.RED}Kalah (Losses)        : {Color.BOLD}{stats['losses']}{Color.RESET}")
    print(f"{Color.YELLOW}Seri (Pushes)         : {Color.BOLD}{stats['pushes']}{Color.RESET}")
    print(f"{Color.MAGENTA}Natural Blackjack     : {Color.BOLD}{stats['blackjacks']}{Color.RESET}")
    print(f"{Color.CYAN}Win Rate              : {Color.BOLD}{win_rate:.1f}%{Color.RESET}")
    print("-" * 45)
    print(f"{Color.YELLOW}Chip Tertinggi (Peak) : {Color.BOLD}{format_money(stats['peak_chips'])}{Color.RESET}")
    print(f"{Color.YELLOW}Sisa Chip Akhir       : {Color.BOLD}{format_money(final_chips)}{Color.RESET}")
    
    if net_profit > 0:
        print(f"{Color.GREEN}Keuntungan Bersih     : {Color.BOLD}+{format_money(net_profit)}{Color.RESET}")
    elif net_profit < 0:
        print(f"{Color.RED}Kerugian Bersih       : {Color.BOLD}-{format_money(abs(net_profit))}{Color.RESET}")
    else:
        print(f"{Color.WHITE}Keuntungan Bersih     : {Color.BOLD}$0 (Impas){Color.RESET}")
    print(Color.CYAN + "=" * 45 + Color.RESET)

def main():
    print(Color.GREEN + "=" * 45 + Color.RESET)
    print(f"{Color.BOLD}{Color.YELLOW}       🃏 WELCOME TO BLACKJACK CLI 🃏       {Color.RESET}")
    print(Color.GREEN + "=" * 45 + Color.RESET)

    initial_chips = 100.0
    chips = initial_chips
    deck = Deck(num_decks=6)

    stats = {
        "rounds": 0,
        "wins": 0,
        "losses": 0,
        "pushes": 0,
        "blackjacks": 0,
        "peak_chips": initial_chips
    }

    while chips > 0:
        chips = play_round(chips, deck, stats)

        if chips > stats["peak_chips"]:
            stats["peak_chips"] = chips

        if chips <= 0:
            print("\n" + Color.RED + "x" * 45 + Color.RESET)
            print(f"{Color.RED}{Color.BOLD}💥 BANKRUPT! Chip kamu habis. Game Over.{Color.RESET}")
            print(Color.RED + "x" * 45 + Color.RESET)
            break

        play_again = input(f"\n{Color.YELLOW}Main ronde berikutnya? ([y]/n): {Color.RESET}").strip().lower()
        if play_again == 'n':
            print(f"\n{Color.GREEN}Terima kasih sudah bermain!{Color.RESET}")
            break

    display_stats(stats, chips, initial_chips)

if __name__ == "__main__":
    main()