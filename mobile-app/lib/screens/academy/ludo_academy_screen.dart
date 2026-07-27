import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

class LudoAcademyScreen extends StatelessWidget {
  const LudoAcademyScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Ludo Academy')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.secondary, Color(0xFF00A884)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Icon(Icons.school, color: Colors.white, size: 40),
                  SizedBox(height: 12),
                  Text('Level Up Your Game',
                      style: TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.bold)),
                  SizedBox(height: 4),
                  Text('Learn, practice, and dominate.',
                      style: TextStyle(color: Colors.white70, fontSize: 14)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            _sectionTitle('Play & Learn'),
            const SizedBox(height: 12),
            _academyCard(
              context,
              icon: Icons.sports_esports,
              title: 'Practice Match',
              subtitle: 'Unlimited free matches. No stakes, just skill.',
              color: AppColors.primary,
              onTap: () => context.go('/practice'),
            ),
            const SizedBox(height: 12),
            _academyCard(
              context,
              icon: Icons.quiz,
              title: 'Learn the Rules',
              subtitle: 'Master Ludo rules from scratch.',
              color: Colors.blue,
              onTap: () => context.go('/academy/rules'),
            ),
            const SizedBox(height: 24),

            _sectionTitle('Improve'),
            const SizedBox(height: 12),
            _academyCard(
              context,
              icon: Icons.lightbulb,
              title: 'Tips & Tricks',
              subtitle: 'Pro tips to gain an edge.',
              color: AppColors.gold,
              onTap: () => context.go('/academy/tips'),
            ),
            const SizedBox(height: 12),
            _academyCard(
              context,
              icon: Icons.psychology,
              title: 'Winning Strategies',
              subtitle: 'Deep strategies used by top players.',
              color: AppColors.secondary,
              onTap: () => context.go('/academy/strategies'),
            ),
            const SizedBox(height: 24),

            _sectionTitle('Compete'),
            const SizedBox(height: 12),
            _academyCard(
              context,
              icon: Icons.emoji_events,
              title: 'Tournament Guide',
              subtitle: 'How tournaments work and how to win them.',
              color: Colors.orange,
              onTap: () => context.go('/academy/tournament-guide'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _sectionTitle(String text) {
    return Text(text,
        style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary));
  }

  Widget _academyCard(BuildContext context, {required IconData icon, required String title, required String subtitle, required Color color, required VoidCallback onTap}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.cardBorder),
        ),
        child: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: color.withOpacity(0.15),
                borderRadius: BorderRadius.circular(12),
              ),
              child: Icon(icon, color: color, size: 28),
            ),
            const SizedBox(width: 16),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 16)),
                  const SizedBox(height: 2),
                  Text(subtitle, style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                ],
              ),
            ),
            const Icon(Icons.chevron_right, color: AppColors.textMuted),
          ],
        ),
      ),
    );
  }
}
