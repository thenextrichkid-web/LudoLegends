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
  User? _user;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  Future<void> _loadProfile() async {
    try {
      _user = await AuthService().getCurrentUser();
    } catch (e) {
      // Silent fail
    }
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(body: Center(child: CircularProgressIndicator()));
    }

    return Scaffold(
      appBar: AppBar(title: const Text('Profile')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            // Avatar
            CircleAvatar(
              radius: 50,
              backgroundColor: AppColors.primary.withOpacity(0.2),
              child: _user?.avatarUrl != null
                  ? ClipOval(child: Image.network(_user!.avatarUrl!, width: 100, height: 100, fit: BoxFit.cover))
                  : const Icon(Icons.person, size: 50, color: AppColors.primary),
            ),
            const SizedBox(height: 16),
            Text(_user?.name ?? 'Player', style: const TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            const SizedBox(height: 4),
            Text(_user?.phone ?? '', style: const TextStyle(color: AppColors.textSecondary)),
            const SizedBox(height: 24),

            // Stats
            Row(
              children: [
                _statItem('Earnings', '₹${(_user?.totalEarnings ?? 0).toInt()}', AppColors.gold),
                _statItem('Matches', '${(_user?.totalMatches ?? 0).toInt()}', AppColors.primary),
                _statItem('Wins', '${(_user?.totalWins ?? 0).toInt()}', AppColors.success),
                _statItem('VIP', '${(_user?.vipLevel ?? 0).toInt()}', AppColors.secondary),
              ],
            ),
            const SizedBox(height: 24),

            // Referral Code
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.cardBorder),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Referral Code', style: TextStyle(color: AppColors.textSecondary)),
                  Text(_user?.referralCode ?? '', style: const TextStyle(color: AppColors.gold, fontWeight: FontWeight.bold, fontSize: 18)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Menu
            _menuItem(Icons.leaderboard, 'Leaderboard', () => context.push('/leaderboard')),
            _menuItem(Icons.card_giftcard, 'Referrals', () => context.push('/referrals')),
            _menuItem(Icons.history, 'Match History', () {}),
            _menuItem(Icons.help, 'Help & Support', () {}),
            _menuItem(Icons.info, 'About', () {}),
            const SizedBox(height: 16),

            // Logout
            TextButton(
              onPressed: () async {
                await AuthService().logout();
                if (mounted) context.go('/otp');
              },
              child: const Text('Logout', style: TextStyle(color: AppColors.error)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statItem(String label, String value, Color color) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(12),
        margin: const EdgeInsets.symmetric(horizontal: 4),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.cardBorder),
        ),
        child: Column(
          children: [
            Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
          ],
        ),
      ),
    );
  }

  Widget _menuItem(IconData icon, String label, VoidCallback onTap) {
    return ListTile(
      leading: Icon(icon, color: AppColors.textSecondary),
      title: Text(label, style: const TextStyle(color: AppColors.textPrimary)),
      trailing: const Icon(Icons.chevron_right, color: AppColors.textMuted),
      onTap: onTap,
    );
  }
}
