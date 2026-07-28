import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/auth_service.dart';
import 'package:ludo_legends/models/user.dart';

class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _authService = AuthService();
  bool _isLoading = true;
  User? _user;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final user = await _authService.getCurrentUser();
      if (!mounted) return;
      setState(() { _user = user; _isLoading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final name = _user?.name ?? 'Player';
    final phone = _user?.phone ?? '';
    final wins = _user?.totalWins.toInt() ?? 0;

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(24),
                    child: Column(
                      children: [
                        const CircleAvatar(
                          radius: 36,
                          backgroundColor: AppColors.primary,
                          child: Icon(Icons.person, size: 40, color: Colors.white),
                        ),
                        const SizedBox(height: 12),
                        Text(name, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                        const SizedBox(height: 4),
                        Text(phone, style: const TextStyle(color: AppColors.textSecondary)),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            _pill('$wins Wins', Icons.emoji_events),
                            const SizedBox(width: 12),
                            _pill('Referral', Icons.card_giftcard),
                          ],
                        ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                _menuItem(Icons.sports_esports, 'My Matches', () => context.push('/matches')),
                _menuItem(Icons.account_balance, 'Withdrawals', () => context.push('/withdrawals')),
                _menuItem(Icons.history, 'Match History', () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Full match history coming soon!'), backgroundColor: AppColors.primary),
                  );
                }),
                _menuItem(Icons.help_outline, 'Help & Support', () {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Help & support coming soon!'), backgroundColor: AppColors.primary),
                  );
                }),
                _menuItem(Icons.info_outline, 'About', () {
                  showAboutDialog(
                    context: context,
                    applicationName: 'Ludo Legends',
                    applicationVersion: '1.0.0',
                    applicationIcon: const Icon(Icons.games, color: AppColors.primary, size: 32),
                    children: const [
                      Text('Ludo Legends is a competitive Ludo platform where you can join tournaments and win real prizes!'),
                    ],
                  );
                }),
                const SizedBox(height: 24),
                OutlinedButton.icon(
                  onPressed: () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        backgroundColor: AppColors.surface,
                        title: const Text('Logout', style: TextStyle(color: AppColors.textPrimary)),
                        content: const Text('Are you sure you want to logout?', style: TextStyle(color: AppColors.textSecondary)),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                          TextButton(
                            onPressed: () => Navigator.pop(ctx, true),
                            child: const Text('Logout', style: TextStyle(color: AppColors.error)),
                          ),
                        ],
                      ),
                    );
                    if (confirmed == true && mounted) {
                      await _authService.logout();
                      if (mounted) context.go('/otp');
                    }
                  },
                  icon: const Icon(Icons.logout, color: AppColors.error),
                  label: const Text('Logout', style: TextStyle(color: AppColors.error)),
                  style: OutlinedButton.styleFrom(side: const BorderSide(color: AppColors.error)),
                ),
              ],
            ),
    );
  }

  Widget _pill(String text, IconData icon) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: AppColors.primary.withOpacity(0.1),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppColors.primary),
          const SizedBox(width: 4),
          Text(text, style: const TextStyle(color: AppColors.primary, fontSize: 12)),
        ],
      ),
    );
  }

  Widget _menuItem(IconData icon, String label, VoidCallback onTap) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: AppColors.textMuted),
        title: Text(label, style: const TextStyle(color: AppColors.textPrimary)),
        trailing: const Icon(Icons.chevron_right, color: AppColors.textMuted),
        onTap: onTap,
      ),
    );
  }
}
