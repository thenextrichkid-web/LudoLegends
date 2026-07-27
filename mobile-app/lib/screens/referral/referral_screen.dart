import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

class ReferralScreen extends StatelessWidget {
  const ReferralScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Referrals')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24),
        child: Column(
          children: [
            // Header
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(24),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.secondary, Color(0xFF00A88A)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  const Icon(Icons.card_giftcard, size: 48, color: Colors.white),
                  const SizedBox(height: 12),
                  const Text('Refer & Earn', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
                  const SizedBox(height: 4),
                  const Text('Invite friends and earn ₹50 for each referral', textAlign: TextAlign.center, style: TextStyle(color: Colors.white70)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Referral Code
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: AppColors.surface,
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppColors.secondary),
              ),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Text('Your Code', style: TextStyle(color: AppColors.textSecondary)),
                  Row(
                    children: [
                      const Text('LL_ABC123', style: TextStyle(color: AppColors.secondary, fontWeight: FontWeight.bold, fontSize: 18)),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.copy, color: AppColors.textMuted, size: 20),
                        onPressed: () {
                          Clipboard.setData(const ClipboardData(text: 'LL_ABC123'));
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('Copied!'), duration: Duration(seconds: 1)),
                          );
                        },
                      ),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Stats
            Row(
              children: [
                _statCard('Total Referrals', '0', Icons.people),
                const SizedBox(width: 12),
                _statCard('Active', '0', Icons.check_circle),
                const SizedBox(width: 12),
                _statCard('Earned', '₹0', Icons.monetization_on),
              ],
            ),
            const SizedBox(height: 24),

            // How it works
            const Text('How it works', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            const SizedBox(height: 12),
            _stepItem(1, 'Share your referral code with friends'),
            _stepItem(2, 'Friend signs up using your code'),
            _stepItem(3, 'You both earn ₹50 bonus!'),
            const SizedBox(height: 24),

            // Share Button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.share),
                label: const Text('Share Referral Code'),
                style: ElevatedButton.styleFrom(backgroundColor: AppColors.secondary),
              ),
            ),
          ],
        ),
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
            Icon(icon, color: AppColors.secondary, size: 20),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.bold)),
            Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 10)),
          ],
        ),
      ),
    );
  }

  Widget _stepItem(int step, String text) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Row(
        children: [
          Container(
            width: 28,
            height: 28,
            decoration: BoxDecoration(
              color: AppColors.secondary.withOpacity(0.15),
              borderRadius: BorderRadius.circular(14),
            ),
            child: Center(child: Text(step.toString(), style: const TextStyle(color: AppColors.secondary, fontWeight: FontWeight.bold, fontSize: 12))),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text(text, style: const TextStyle(color: AppColors.textSecondary))),
        ],
      ),
    );
  }
}
