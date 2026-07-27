import 'package:flutter/material.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

class LeaderboardScreen extends StatefulWidget {
  const LeaderboardScreen({super.key});

  @override
  State<LeaderboardScreen> createState() => _LeaderboardScreenState();
}

class _LeaderboardScreenState extends State<LeaderboardScreen> {
  String _selectedPeriod = 'weekly';

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Leaderboard')),
      body: Column(
        children: [
          // Period Selector
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.all(16),
            child: Row(
              children: ['weekly', 'monthly', 'all_time'].map((period) {
                final isSelected = _selectedPeriod == period;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: ChoiceChip(
                    label: Text(period == 'all_time' ? 'All Time' : period.toUpperCase()),
                    selected: isSelected,
                    onSelected: (_) => setState(() => _selectedPeriod = period),
                    backgroundColor: AppColors.surface,
                    selectedColor: AppColors.primary,
                    labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.textSecondary),
                  ),
                );
              }).toList(),
            ),
          ),

          // Top 3 Podium
          SizedBox(
            height: 180,
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                _podiumItem(2, 'Player 2', 150, AppColors.textSecondary),
                const SizedBox(width: 12),
                _podiumItem(1, 'Player 1', 200, AppColors.gold),
                const SizedBox(width: 12),
                _podiumItem(3, 'Player 3', 120, Color(0xFFCD7F32)),
              ],
            ),
          ),

          // Remaining List
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              itemCount: 10,
              itemBuilder: (context, index) => _leaderboardItem(index + 4),
            ),
          ),
        ],
      ),
    );
  }

  Widget _podiumItem(int rank, String name, double height, Color color) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: [
        CircleAvatar(
          radius: 20,
          backgroundColor: color.withOpacity(0.2),
          child: Text(rank.toString(), style: TextStyle(color: color, fontWeight: FontWeight.bold)),
        ),
        const SizedBox(height: 4),
        Text(name, style: const TextStyle(color: AppColors.textPrimary, fontSize: 12)),
        Container(
          width: 80,
          height: height,
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            borderRadius: const BorderRadius.vertical(top: Radius.circular(8)),
            border: Border.all(color: color.withOpacity(0.3)),
          ),
          child: Center(
            child: Text('₹${(1000 / rank).toInt()}', style: TextStyle(color: color, fontWeight: FontWeight.bold)),
          ),
        ),
      ],
    );
  }

  Widget _leaderboardItem(int rank) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: AppColors.surface,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: AppColors.cardBorder),
      ),
      child: Row(
        children: [
          SizedBox(
            width: 32,
            child: Text(rank.toString(), style: const TextStyle(color: AppColors.textMuted, fontWeight: FontWeight.bold)),
          ),
          CircleAvatar(
            radius: 16,
            backgroundColor: AppColors.primary.withOpacity(0.2),
            child: const Icon(Icons.person, size: 16, color: AppColors.primary),
          ),
          const SizedBox(width: 12),
          Expanded(child: Text('Player $rank', style: TextStyle(color: AppColors.textPrimary))),
          Text('₹${(500 - rank * 40)}', style: const TextStyle(color: AppColors.gold, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }
}
