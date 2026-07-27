import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/tournament_service.dart';
import 'package:ludo_legends/models/tournament.dart';

class TournamentDetailScreen extends StatefulWidget {
  final String tournamentId;
  const TournamentDetailScreen({super.key, required this.tournamentId});

  @override
  State<TournamentDetailScreen> createState() => _TournamentDetailScreenState();
}

class _TournamentDetailScreenState extends State<TournamentDetailScreen> {
  Tournament? _tournament;
  bool _isLoading = true;
  bool _isJoining = false;

  @override
  void initState() {
    super.initState();
    _loadTournament();
  }

  Future<void> _loadTournament() async {
    try {
      _tournament = await TournamentService().getTournament(widget.tournamentId);
    } catch (e) {
      // Silent fail
    }
    setState(() => _isLoading = false);
  }

  Future<void> _joinTournament() async {
    setState(() => _isJoining = true);
    try {
      await TournamentService().joinTournament(widget.tournamentId);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Joined successfully!'), backgroundColor: AppColors.success),
        );
        _loadTournament();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Failed to join: $e'), backgroundColor: AppColors.error),
        );
      }
    }
    setState(() => _isJoining = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return Scaffold(appBar: AppBar(), body: const Center(child: CircularProgressIndicator()));
    }

    final tournament = _tournament;
    if (tournament == null) {
      return Scaffold(appBar: AppBar(), body: const Center(child: Text('Tournament not found')));
    }

    return Scaffold(
      appBar: AppBar(title: Text(tournament.name)),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Prize Pool
            Container(
              width: double.infinity,
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: const LinearGradient(
                  colors: [AppColors.gold, Color(0xFFB8860B)],
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  const Text('PRIZE POOL', style: TextStyle(color: Colors.black54, fontWeight: FontWeight.bold, fontSize: 12)),
                  const SizedBox(height: 4),
                  Text('₹${tournament.prizePool.toInt()}', style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.bold)),
                ],
              ),
            ),
            const SizedBox(height: 24),

            // Info Row
            Row(
              children: [
                _infoCard('Entry Fee', '₹${tournament.entryFee.toInt()}', AppColors.primary),
                const SizedBox(width: 12),
                _infoCard('Players', '${tournament.currentParticipants}/${tournament.maxParticipants}', AppColors.secondary),
                const SizedBox(width: 12),
                _infoCard('Type', tournament.type.replaceAll('_', ' '), AppColors.gold),
              ],
            ),
            const SizedBox(height: 24),

            // Description
            if (tournament.description != null) ...[
              const Text('About', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 8),
              Text(tournament.description!, style: const TextStyle(color: AppColors.textSecondary)),
              const SizedBox(height: 24),
            ],

            // Rules
            if (tournament.rules != null) ...[
              const Text('Rules', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
              const SizedBox(height: 8),
              Text(tournament.rules!, style: const TextStyle(color: AppColors.textSecondary)),
              const SizedBox(height: 24),
            ],

            // Timeline
            const Text('Timeline', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            const SizedBox(height: 12),
            _timelineItem(Icons.play_arrow, 'Starts', tournament.startsAt, AppColors.success),
            if (tournament.registrationDeadline != null)
              _timelineItem(Icons.how_to_reg, 'Registration Deadline', tournament.registrationDeadline!, AppColors.gold),
            if (tournament.endsAt != null)
              _timelineItem(Icons.stop, 'Ends', tournament.endsAt!, AppColors.error),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(16),
        decoration: const BoxDecoration(
          color: AppColors.surface,
          border: Border(top: BorderSide(color: AppColors.border)),
        ),
        child: ElevatedButton(
          onPressed: tournament.isJoinable && !_isJoining ? _joinTournament : null,
          style: ElevatedButton.styleFrom(
            backgroundColor: tournament.isJoinable ? AppColors.primary : AppColors.textMuted,
            padding: const EdgeInsets.symmetric(vertical: 16),
          ),
          child: _isJoining
              ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
              : Text(
                  tournament.isJoinable ? 'Join Tournament - ₹${tournament.entryFee.toInt()}' : tournament.isFull ? 'Tournament Full' : 'Registration Closed',
                  style: const TextStyle(fontSize: 16),
                ),
        ),
      ),
    );
  }

  Widget _infoCard(String label, String value, Color color) {
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
            Text(value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 16)),
            const SizedBox(height: 4),
            Text(label, style: const TextStyle(color: AppColors.textMuted, fontSize: 11)),
          ],
        ),
      ),
    );
  }

  Widget _timelineItem(IconData icon, String label, DateTime date, Color color) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Icon(icon, color: color, size: 20),
          const SizedBox(width: 12),
          Text(label, style: const TextStyle(color: AppColors.textSecondary)),
          const Spacer(),
          Text(
            '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}',
            style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w500),
          ),
        ],
      ),
    );
  }
}
