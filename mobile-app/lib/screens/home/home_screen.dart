import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/wallet_service.dart';
import 'package:ludo_legends/services/tournament_service.dart';
import 'package:ludo_legends/services/auth_service.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class HomeScreen extends ConsumerStatefulWidget {
  const HomeScreen({super.key});

  @override
  ConsumerState<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends ConsumerState<HomeScreen> {
  double _balance = 0;
  int _activeTournaments = 0;
  bool _showWelcome = false;
  String _userName = 'Player';
  double _totalEarnings = 0;
  double _totalMatches = 0;
  double _totalWins = 0;
  int _notificationCount = 0;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    try {
      final wallet = await WalletService().getBalance();
      final tournaments = await TournamentService().getTournaments(status: 'upcoming');
      final user = await AuthService().getCurrentUser();
      final storage = const FlutterSecureStorage();
      final hasSeenWelcome = await storage.read(key: 'has_seen_welcome');

      if (mounted) {
        setState(() {
          _balance = wallet.balance;
          _activeTournaments = tournaments.length;
          if (user != null) {
            _userName = user.name ?? 'Player';
            _totalEarnings = user.totalEarnings;
            _totalMatches = user.totalMatches;
            _totalWins = user.totalWins;
          }
          if (hasSeenWelcome == null) {
            _showWelcome = true;
          }
        });
      }
    } catch (e) {
      // Silent fail
    }
  }

  Future<void> _dismissWelcome() async {
    final storage = const FlutterSecureStorage();
    await storage.write(key: 'has_seen_welcome', value: 'true');
    setState(() => _showWelcome = false);
  }

  @override
  Widget build(BuildContext context) {
    final winRate = _totalMatches > 0 ? ((_totalWins / _totalMatches) * 100).toStringAsFixed(0) : '0';

    return Scaffold(
      appBar: AppBar(
        title: const Text('LUDO LEGENDS'),
        actions: [
          Stack(
            children: [
              IconButton(
                icon: const Icon(Icons.notifications_outlined),
                onPressed: () {},
              ),
              if (_notificationCount > 0)
                Positioned(
                  right: 8,
                  top: 8,
                  child: Container(
                    padding: const EdgeInsets.all(4),
                    decoration: const BoxDecoration(
                      color: AppColors.error,
                      shape: BoxShape.circle,
                    ),
                    child: Text(
                      '$_notificationCount',
                      style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold),
                    ),
                  ),
                ),
            ],
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
              // Welcome Card (first login only)
              if (_showWelcome) ...[
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [AppColors.secondary, Color(0xFF00A884)],
                      begin: Alignment.topLeft,
                      end: Alignment.bottomRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text('Welcome, $_userName!',
                                style: const TextStyle(color: Colors.white, fontSize: 18, fontWeight: FontWeight.bold)),
                            const SizedBox(height: 4),
                            const Text('Your Ludo journey starts here.',
                                style: TextStyle(color: Colors.white70, fontSize: 13)),
                          ],
                        ),
                      ),
                      IconButton(
                        icon: const Icon(Icons.close, color: Colors.white70, size: 20),
                        onPressed: _dismissWelcome,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 16),
              ],

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
                    const Text('Wallet Balance',
                        style: TextStyle(color: AppColors.textSecondary, fontSize: 14)),
                    const SizedBox(height: 2),
                    const Text('Built on Trust \u2022 Fair Play \u2022 Real Rewards.',
                        style: TextStyle(color: AppColors.textMuted, fontSize: 11)),
                    const SizedBox(height: 8),
                    Text('\u20B9${_balance.toStringAsFixed(0)}',
                        style: const TextStyle(color: AppColors.textPrimary, fontSize: 36, fontWeight: FontWeight.bold)),
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
              const Text('Quick Actions',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 12),
              Row(
                children: [
                  _quickAction(Icons.emoji_events, 'Tournaments', Colors.purple, () => context.go('/tournaments')),
                  const SizedBox(width: 10),
                  _quickAction(Icons.leaderboard, 'Leaderboard', Colors.amber, () => context.go('/leaderboard')),
                  const SizedBox(width: 10),
                  _quickAction(Icons.card_giftcard, 'Referrals', Colors.green, () => context.go('/referrals')),
                ],
              ),
              const SizedBox(height: 12),
              Row(
                children: [
                  _quickAction(Icons.school, 'Academy', AppColors.secondary, () => context.go('/academy')),
                  const SizedBox(width: 10),
                  _quickAction(Icons.sports_mma, 'Quick Play', Colors.orange, () {}, comingSoon: true),
                  const SizedBox(width: 10),
                  _quickAction(Icons.fitness_center, 'Practice', Colors.cyan, () => context.go('/practice')),
                ],
              ),
              const SizedBox(height: 24),

              // Active Tournaments
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Active Tournaments',
                      style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                  TextButton(onPressed: () => context.go('/tournaments'), child: const Text('View All')),
                ],
              ),
              const SizedBox(height: 8),
              SizedBox(
                height: 120,
                child: _activeTournaments == 0
                    ? Container(
                        width: double.infinity,
                        padding: const EdgeInsets.all(20),
                        decoration: BoxDecoration(
                          color: AppColors.surface,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: AppColors.cardBorder),
                        ),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            const Icon(Icons.emoji_events_outlined, color: AppColors.textMuted, size: 32),
                            const SizedBox(height: 8),
                            const Text('No tournaments are live right now.',
                                style: TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                            const SizedBox(height: 2),
                            const Text('New tournaments are added throughout the day.',
                                style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                            const SizedBox(height: 10),
                            TextButton(
                              onPressed: () => context.go('/tournaments'),
                              style: TextButton.styleFrom(
                                backgroundColor: AppColors.primary.withOpacity(0.15),
                                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                              ),
                              child: const Text('Browse Upcoming Matches',
                                  style: TextStyle(color: AppColors.primary, fontSize: 12)),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: _activeTournaments,
                        itemBuilder: (context, index) => _tournamentCard(),
                      ),
              ),
              const SizedBox(height: 24),

              // Stats
              const Text('Your Stats',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 12),
              Row(
                children: [
                  _statCard('Matches', _totalMatches.toInt().toString(), Icons.sports_esports),
                  const SizedBox(width: 8),
                  _statCard('Wins', _totalWins.toInt().toString(), Icons.emoji_events),
                  const SizedBox(width: 8),
                  _statCard('Win Rate', '$winRate%', Icons.trending_up),
                ],
              ),
              const SizedBox(height: 10),
              Row(
                children: [
                  _statCard('Earnings', '\u20B9${_totalEarnings.toInt()}', Icons.account_balance_wallet),
                  const SizedBox(width: 8),
                  _statCard('Rank', '#--', Icons.workspace_premium),
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

  Widget _quickAction(IconData icon, String label, Color color, VoidCallback onTap, {bool comingSoon = false}) {
    return Expanded(
      child: GestureDetector(
        onTap: onTap,
        child: Container(
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            color: AppColors.surface,
            borderRadius: BorderRadius.circular(12),
            border: Border.all(color: AppColors.cardBorder),
          ),
          child: Column(
            children: [
              Stack(
                alignment: Alignment.center,
                children: [
                  Icon(icon, color: color, size: 34),
                  if (comingSoon)
                    Positioned(
                      bottom: -4,
                      child: Container(
                        padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
                        decoration: BoxDecoration(
                          color: AppColors.gold,
                          borderRadius: BorderRadius.circular(4),
                        ),
                        child: const Text('SOON', style: TextStyle(color: Colors.black, fontSize: 7, fontWeight: FontWeight.bold)),
                      ),
                    ),
                ],
              ),
              const SizedBox(height: 10),
              Text(label, style: TextStyle(color: comingSoon ? AppColors.textMuted : AppColors.textSecondary, fontSize: 12)),
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
          const Text('Entry: \u20B9100', style: TextStyle(color: AppColors.gold, fontSize: 12)),
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
