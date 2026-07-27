import 'package:flutter/material.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

class AcademyContentScreen extends StatelessWidget {
  final String title;
  final IconData icon;
  final Color color;
  final List<Map<String, String>> items;

  const AcademyContentScreen({
    super.key,
    required this.title,
    required this.icon,
    required this.color,
    required this.items,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text(title)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: color.withOpacity(0.1),
                borderRadius: BorderRadius.circular(16),
                border: Border.all(color: color.withOpacity(0.3)),
              ),
              child: Row(
                children: [
                  Icon(icon, color: color, size: 36),
                  const SizedBox(width: 16),
                  Text(title, style: TextStyle(color: color, fontSize: 22, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            const SizedBox(height: 20),
            ...items.map((item) => Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Container(
                width: double.infinity,
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.cardBorder),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(item['title'] ?? '',
                        style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 15)),
                    const SizedBox(height: 6),
                    Text(item['content'] ?? '',
                        style: const TextStyle(color: AppColors.textSecondary, fontSize: 13, height: 1.5)),
                  ],
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }

  static final rulesData = AcademyContentScreen(
    title: 'Learn the Rules',
    icon: Icons.quiz,
    color: Colors.blue,
    items: [
      {'title': 'The Board', 'content': 'Ludo is played on a 15x15 cross-shaped board with 4 home bases. Each player has 4 tokens of one color (Red, Green, Yellow, Blue).'},
      {'title': 'Objective', 'content': 'Move all 4 of your tokens from your base to the center home area. First player to do this wins.'},
      {'title': 'Rolling the Dice', 'content': 'On your turn, roll a single die. You must roll a 6 to move a token out of your base onto the starting square.'},
      {'title': 'Movement', 'content': 'Move your token clockwise around the board by the number shown on the die. Follow the colored path to your home column.'},
      {'title': 'Capturing', 'content': 'If your token lands on an opponent\'s token, the opponent\'s token is sent back to their base. They must roll a 6 to re-enter.'},
      {'title': 'Safe Squares', 'content': 'Star squares and colored starting squares are safe. Tokens on safe squares cannot be captured.'},
      {'title': 'Extra Turns', 'content': 'Roll a 6 and get an extra turn! Roll three 6s in a row and your last moved token goes back to base.'},
      {'title': 'Home Column', 'content': 'When a token enters its colored home column, it must reach the center with an exact die roll. No overshooting!'},
    ],
  );

  static final tipsData = AcademyContentScreen(
    title: 'Tips & Tricks',
    icon: Icons.lightbulb,
    color: AppColors.gold,
    items: [
      {'title': 'Always Keep a Token Moving', 'content': 'Don\'t hoard all tokens in the base. Get at least 2-3 tokens on the board to maintain pressure and flexibility.'},
      {'title': 'Use Safe Squares', 'content': 'Land on star squares whenever possible. They\'re immune to captures and perfect for regrouping.'},
      {'title': 'The 6th Move', 'content': 'Use your extra turn wisely. Plan 2-3 moves ahead after rolling a 6, not just the immediate move.'},
      {'title': 'Chase or Block?', 'content': 'If you\'re ahead, play defensive on safe squares. If behind, take calculated risks to capture opponents.'},
      {'title': 'Counting Dice', 'content': 'Track what opponents rolled. If someone just rolled a 6, they likely have a token deep in your territory.'},
      {'title': 'Home Stretch Warning', 'content': 'Don\'t send a token into the home column until you can reach the center with a likely roll. Stuck tokens are wasted turns.'},
    ],
  );

  static final strategiesData = AcademyContentScreen(
    title: 'Winning Strategies',
    icon: Icons.psychology,
    color: AppColors.secondary,
    items: [
      {'title': 'The Aggressive Open', 'content': 'Roll a 6? Immediately send your token to a position where it threatens an opponent\'s closest safe square. Force them to react.'},
      {'title': 'The Two-Token Lead', 'content': 'Keep two tokens close together advancing around the board. This creates a capture net that\'s hard to avoid.'},
      {'title': 'Endgame Priority', 'content': 'When one token reaches the home column, switch focus to your next closest token. Never stop all movement for one token.'},
      {'title': 'Bait and Switch', 'content': 'Leave a token slightly exposed on a non-safe square as bait. When an opponent captures it, your other tokens advance freely.'},
      {'title': 'The Six Trap', 'content': 'Save your 6-rolls for when you have a token near an opponent\'s base. The extra turn lets you capture AND retreat in one turn.'},
      {'title': 'Psychology Matters', 'content': 'Stay calm when behind. Most players make mistakes under pressure. Patience wins more games than aggression.'},
    ],
  );

  static final tournamentGuideData = AcademyContentScreen(
    title: 'Tournament Guide',
    icon: Icons.emoji_events,
    color: Colors.orange,
    items: [
      {'title': 'How Tournaments Work', 'content': 'Pay an entry fee to join a tournament bracket. Play against opponents in elimination rounds. Last player standing wins the prize pool.'},
      {'title': 'Entry Fees & Prizes', 'content': 'Entry fees vary (Rs 50-500+). Prize pools are determined by the host. Higher entry = bigger prizes.'},
      {'title': 'Match Submission', 'content': 'After each match, submit your result with a screenshot as proof. Admins verify results before advancing brackets.'},
      {'title': 'Anti-Cheat', 'content': 'Tampered screenshots or fake results lead to permanent ban. The system uses server-authoritative verification.'},
      {'title': 'Withdrawals', 'content': 'Winnings go to your wallet instantly after admin approval. Withdraw to your bank account anytime (minimum Rs 100).'},
      {'title': 'Tournament Tips', 'content': 'Join lower-entry tournaments first to build your bankroll. Higher-stakes tournaments attract experienced players.'},
    ],
  );
}
