import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/wallet_service.dart';
import 'package:ludo_legends/services/tournament_service.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  double _balance = 0;
  int _activeTournaments = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final wallet = await WalletService().getBalance();
      final tournaments = await TournamentService().getTournaments(status: 'upcoming');
      setState(() {
        _balance = wallet.balance;
        _activeTournaments = tournaments.length;
      });
    } catch (e) {
      // Silent fail
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('LUDO LEGENDS'),
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications_outlined),
            onPressed: () {},
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _loadData,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Balance Card
              Container(
                width: double.infinity,
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppColors.primary, Color(0xFF5B1FD4)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Balance', style: TextStyle(color: AppColors.textSecondary, fontSize: 14)),
                    const SizedBox(height: 4),
                    Text('₹${_balance.toStringAsFixed(0)}', style: const TextStyle(color: AppColors.textPrimary, fontSize: 36, fontWeight: FontWeight.bold)),
                    const SizedBox(height: 16),
                    Row(
                      children: [
                        _actionButton(Icons.add, 'Deposit', () => context.go('/wallet')),
                        const SizedBox(width: 12),
                        _actionButton(Icons.arrow_upward, 'Withdraw', () => context.go('/wallet')),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Quick Actions
              const Text('Quick Actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 12),
              Row(
                children: [
                  _quickAction(Icons.emoji_events, 'Tournaments', Colors.purple, () => context.go('/tournaments')),
                  const SizedBox(width: 12),
                  _quickAction(Icons.leaderboard, 'Leaderboard', Colors.amber, () => context.go('/leaderboard')),
                  const SizedBox(width: 12),
                  _quickAction(Icons.card_giftcard, 'Referrals', Colors.green, () => context.go('/referrals')),
                ],
              ),
              const SizedBox(height: 24),

              // Active Tournaments
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Active Tournaments', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                  TextButton(onPressed: () => context.go('/tournaments'), child: const Text('View All')),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 120,
                child: _activeTournaments == 0
                    ? const Center(child: Text('No active tournaments', style: TextStyle(color: AppColors.textMuted)))
                    : ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: _activeTournaments,
                        itemBuilder: (context, index) => _tournamentCard(),
                      ),
              ),
              const SizedBox(height: 24),

              // Stats
              const Text('Your Stats', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 12),
              Row(
                children: [
                  _statCard('Matches', '0', Icons.sports_esports),
                  const SizedBox(width: 12),
                  _statCard('Wins', '0', Icons.emoji_events),
                  const SizedBox(width: 12),
                  _statCard('Win Rate', '0%', Icons.trending_up),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _actionButton(IconData icon, String label, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
        decoration: BoxDecoration(
          color: Colors.white.withOpacity(0.15),
          borderRadius: BorderRadius.circular(8),
        ),
        child: Row(
          children: [
            Icon(icon, color: Colors.white, size: 16),
            const SizedBox(width: 4),
            Text(label, style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w500)),
          ],
        ),
      ),
    );
  }

  Widget _quickAction(IconData icon, String label, Color color, VoidCallback onTap) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(16),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.cardBorder),
          ),
          child: Column(
            children: [
              Icon(icon, color: color, size: 28),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _tournamentCard() {
    return Container(
      width: 200,
      margin: const EdgeInsets.only(right: 12),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: AppColors.cardBorder),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Text('Tournament Name', style: TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold)),
          const SizedBox(height: 4),
          const Text('Entry: ₹100', style: TextStyle(color: AppColors.gold, fontSize: 12)),
          const SizedBox(height: 8),
          LinearProgressIndicator(value: 0.6, backgroundColor: AppColors.border, valueColor: AlwaysStoppedAnimation(AppColors.primary)),
        ],
      ),
    );
  }

  Widget _statCard(String label, String value, IconData icon) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.cardBorder),
        ),
        child: Column(
          children: [
            Icon(icon, color: AppColors.primary, size: 20),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold, fontSize: 18)),
            Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
          ],
        ),
      ),
    );
  }
}
