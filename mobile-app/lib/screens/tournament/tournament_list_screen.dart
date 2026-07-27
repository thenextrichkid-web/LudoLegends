import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/tournament_service.dart';
import 'package:ludo_legends/models/tournament.dart';

class TournamentListScreen extends StatefulWidget {
  const TournamentListScreen({super.key});

  @override
  State<TournamentListScreen> createState() => _TournamentListScreenState();
}

class _TournamentListScreenState extends State<TournamentListScreen> {
  List<Tournament> _tournaments = [];
  bool _isLoading = true;
  String _selectedFilter = 'all';

  @override
  void initState() {
    super.initState();
    _loadTournaments();
  }

  Future<void> _loadTournaments() async {
    setState(() => _isLoading = true);
    try {
      final status = _selectedFilter == 'all' ? null : _selectedFilter;
      _tournaments = await TournamentService().getTournaments(status: status);
    } catch (e) {
      // Silent fail
    }
    setState(() => _isLoading = false);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tournaments')),
      body: Column(
        children: [
          // Filter Chips
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: ['all', 'upcoming', 'in_progress', 'completed'].map((filter) {
                final isSelected = _selectedFilter == filter;
                return Padding(
                  padding: const EdgeInsets.only(right: 8),
                  child: FilterChip(
                    label: Text(filter == 'all' ? 'All' : filter.replaceAll('_', ' ').toUpperCase()),
                    selected: isSelected,
                    onSelected: (_) {
                      setState(() => _selectedFilter = filter);
                      _loadTournaments();
                    },
                    backgroundColor: AppColors.surface,
                    selectedColor: AppColors.primary,
                    labelStyle: TextStyle(color: isSelected ? Colors.white : AppColors.textSecondary),
                  ),
                );
              }).toList(),
            ),
          ),

          // Tournament List
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _tournaments.isEmpty
                    ? const Center(child: Text('No tournaments found', style: TextStyle(color: AppColors.textMuted)))
                    : RefreshIndicator(
                        onRefresh: _loadTournaments,
                        child: ListView.builder(
                          padding: const EdgeInsets.all(16),
                          itemCount: _tournaments.length,
                          itemBuilder: (context, index) => _tournamentCard(_tournaments[index]),
                        ),
                      ),
          ),
        ],
      ),
    );
  }

  Widget _tournamentCard(Tournament tournament) {
    return GestureDetector(
      onTap: () => context.push('/tournament/${tournament.id}'),
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(16),
        decoration: BoxDecoration(
          color: AppColors.surface,
          borderRadius: BorderRadius.circular(12),
          border: Border.all(color: AppColors.cardBorder),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(tournament.name, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                ),
                _statusBadge(tournament.status),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                _infoChip(Icons.monetization_on, '₹${tournament.entryFee.toInt()}', AppColors.gold),
                const SizedBox(width: 8),
                _infoChip(Icons.emoji_events, '₹${tournament.prizePool.toInt()}', AppColors.secondary),
                const SizedBox(width: 8),
                _infoChip(Icons.people, '${tournament.currentParticipants}/${tournament.maxParticipants}', AppColors.textSecondary),
              ],
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: tournament.fillPercentage,
              backgroundColor: AppColors.border,
              valueColor: AlwaysStoppedAnimation(tournament.isFull ? AppColors.error : AppColors.primary),
            ),
            const SizedBox(height: 8),
            Text(
              'Starts: ${tournament.startsAt.day}/${tournament.startsAt.month}/${tournament.startsAt.year}',
              style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _statusBadge(String status) {
    Color color;
    switch (status) {
      case 'upcoming':
        color = AppColors.primary;
        break;
      case 'in_progress':
        color = AppColors.secondary;
        break;
      case 'completed':
        color = AppColors.gold;
        break;
      default:
        color = AppColors.textMuted;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(status.toUpperCase(), style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }

  Widget _infoChip(IconData icon, String text, Color color) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Icon(icon, color: color, size: 14),
        const SizedBox(width: 4),
        Text(text, style: TextStyle(color: color, fontSize: 12)),
      ],
    );
  }
}
