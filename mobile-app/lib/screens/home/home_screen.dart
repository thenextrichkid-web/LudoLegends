import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/auth_service.dart';
import 'package:ludo_legends/services/wallet_service.dart';
import 'package:ludo_legends/services/tournament_service.dart';
import 'package:ludo_legends/models/user.dart';
import 'package:ludo_legends/models/wallet.dart';
import 'package:ludo_legends/models/tournament.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _authService = AuthService();
  final _walletService = WalletService();
  final _tournamentService = TournamentService();
  bool _expanded = false;

  String _userName = 'Player';
  double _balance = 0;
  int _wins = 0;
  List<Tournament> _tournaments = [];
  List<Tournament> _myTournaments = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final user = await _authService.getCurrentUser();
      final wallet = await _walletService.getBalance();
      final tournaments = await _tournamentService.getTournaments(status: 'upcoming', perPage: 3);
      final myTournaments = await _tournamentService.getMyJoined();
      if (!mounted) return;
      setState(() {
        _userName = user?.name ?? 'Player';
        _balance = wallet.balance;
        _wins = user?.totalWins.toInt() ?? 0;
        _tournaments = tournaments;
        _myTournaments = myTournaments;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      final msg = e.toString().contains('Connection')
          ? 'No internet connection. Pull down to retry.'
          : 'Failed to load data. Pull down to retry.';
      setState(() { _error = msg; _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      body: RefreshIndicator(
        onRefresh: _load,
        color: AppColors.primary,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.wifi_off, size: 48, color: AppColors.textMuted),
                        const SizedBox(height: 16),
                        Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: AppColors.textSecondary)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _load, child: const Text('Retry')),
                      ],
                    ),
                  )
                : ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      _buildWalletCard(),
                      const SizedBox(height: 16),
                      if (_myTournaments.isNotEmpty) ...[
                        _buildMyTournaments(),
                        const SizedBox(height: 16),
                      ],
                      _buildTournamentSection(),
                      const SizedBox(height: 16),
                      _buildWelcomeCard(),
                      const SizedBox(height: 16),
                      _buildStats(),
                      const SizedBox(height: 16),
                      _buildQuickActions(),
                    ],
                  ),
      ),
    );
  }

  Widget _buildWalletCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Wallet Balance', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                  const SizedBox(height: 4),
                  Text('₹${_balance.toStringAsFixed(0)}', style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                ],
              ),
            ),
            ElevatedButton(
              onPressed: () => context.push('/wallet'),
              child: const Text('Top Up'),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMyTournaments() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('My Tournaments', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        const SizedBox(height: 8),
        ..._myTournaments.map((t) => Card(
          margin: const EdgeInsets.only(bottom: 8),
          child: ListTile(
            leading: Icon(
              t.status == 'completed' ? Icons.check_circle : t.status == 'in_progress' ? Icons.play_circle : Icons.emoji_events,
              color: t.status == 'completed' ? AppColors.success : t.status == 'in_progress' ? AppColors.secondary : AppColors.primary,
            ),
            title: Text(t.name, style: const TextStyle(color: AppColors.textPrimary)),
            subtitle: Text(
              'Entry ₹${t.entryFee.toInt()} · ${t.status.toUpperCase()}',
              style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
            ),
            trailing: const Icon(Icons.chevron_right, color: AppColors.textMuted),
            onTap: () => context.push('/tournament/${t.id}'),
          ),
        )),
      ],
    );
  }

  Widget _buildTournamentSection() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Upcoming Tournaments', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        const SizedBox(height: 8),
        if (_tournaments.isEmpty)
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Center(
                child: Column(
                  children: [
                    Icon(Icons.emoji_events_outlined, size: 48, color: AppColors.textMuted.withOpacity(0.5)),
                    const SizedBox(height: 12),
                    const Text('No upcoming tournaments', style: TextStyle(color: AppColors.textSecondary)),
                    const SizedBox(height: 4),
                    TextButton(
                      onPressed: () => context.push('/tournaments'),
                      child: const Text('Browse All Tournaments'),
                    ),
                  ],
                ),
              ),
            ),
          )
        else
          ..._tournaments.map((t) => _buildTournamentCard(t)),
      ],
    );
  }

  Widget _buildTournamentCard(Tournament t) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: const Icon(Icons.emoji_events, color: AppColors.primary),
        title: Text(t.name, style: const TextStyle(color: AppColors.textPrimary)),
        subtitle: Text(
          'Entry ₹${t.entryFee.toInt()} · Prize ₹${t.prizePool.toInt()}',
          style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
        ),
        trailing: const Icon(Icons.chevron_right, color: AppColors.textMuted),
        onTap: () => context.push('/tournament/${t.id}'),
      ),
    );
  }

  Widget _buildWelcomeCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const CircleAvatar(
                  radius: 20,
                  backgroundColor: AppColors.primary,
                  child: Icon(Icons.person, color: Colors.white),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Text(
                    'Welcome, $_userName!',
                    style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStats() {
    return Card(
      child: Column(
        children: [
          ListTile(
            leading: const Icon(Icons.leaderboard, color: AppColors.primary),
            title: const Text('Your Stats', style: TextStyle(color: AppColors.textPrimary)),
            subtitle: Text(
              _expanded ? 'Tap to collapse' : 'Wins: $_wins · Tap to expand',
              style: const TextStyle(color: AppColors.textSecondary, fontSize: 12),
            ),
            trailing: Icon(_expanded ? Icons.expand_less : Icons.expand_more, color: AppColors.textMuted),
            onTap: () => setState(() => _expanded = !_expanded),
          ),
          if (_expanded)
            Padding(
              padding: const EdgeInsets.fromLTRB(16, 0, 16, 16),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceAround,
                children: [
                  _statItem('Wins', '$_wins', Icons.emoji_events),
                  _statItem('Rank', '#--', Icons.leaderboard),
                  _statItem('Matches', '0', Icons.sports_esports),
                ],
              ),
            ),
        ],
      ),
    );
  }

  Widget _statItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: AppColors.primary, size: 20),
        const SizedBox(height: 4),
        Text(value, style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        Text(label, style: const TextStyle(fontSize: 11, color: AppColors.textMuted)),
      ],
    );
  }

  Widget _buildQuickActions() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text('Quick Actions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(child: _quickAction(Icons.school, 'Ludo Academy', () => context.push('/academy'))),
            const SizedBox(width: 8),
            Expanded(child: _quickAction(Icons.play_arrow, 'Quick Play', () => context.push('/pools'))),
            const SizedBox(width: 8),
            Expanded(child: _quickAction(Icons.fitness_center, 'Practice', () => context.push('/practice'))),
          ],
        ),
      ],
    );
  }

  Widget _quickAction(IconData icon, String label, VoidCallback onTap) {
    return Card(
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.symmetric(vertical: 16),
          child: Column(
            children: [
              Icon(icon, color: AppColors.primary, size: 28),
              const SizedBox(height: 8),
              Text(label, style: const TextStyle(fontSize: 12, color: AppColors.textPrimary)),
            ],
          ),
        ),
      ),
    );
  }
}
