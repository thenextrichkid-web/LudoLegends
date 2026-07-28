import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/match_service.dart';
import 'package:ludo_legends/services/auth_service.dart';
import 'package:ludo_legends/models/match.dart';

class MyMatchesScreen extends StatefulWidget {
  const MyMatchesScreen({super.key});

  @override
  State<MyMatchesScreen> createState() => _MyMatchesScreenState();
}

class _MyMatchesScreenState extends State<MyMatchesScreen> {
  final _matchService = MatchService();
  bool _isLoading = true;
  bool _hasError = false;
  List<Match> _matches = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final matches = await _matchService.getMyMatches();
      if (!mounted) return;
      setState(() { _matches = matches; _isLoading = false; });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('My Matches')),
      body: RefreshIndicator(
        onRefresh: _load,
        color: AppColors.primary,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _hasError
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.wifi_off, size: 48, color: AppColors.textMuted),
                        const SizedBox(height: 16),
                        const Text('Failed to load matches', style: TextStyle(color: AppColors.textSecondary)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _load, child: const Text('Retry')),
                      ],
                    ),
                  )
                : _matches.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.sports_esports, size: 64, color: AppColors.textMuted.withOpacity(0.4)),
                            const SizedBox(height: 16),
                            const Text('No matches yet', style: TextStyle(color: AppColors.textSecondary)),
                            const SizedBox(height: 8),
                            const Text('Join a tournament and submit your results!', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: () => context.push('/tournaments'),
                              child: const Text('Browse Tournaments'),
                            ),
                          ],
                        ),
                      )
                    : ListView.builder(
                        padding: const EdgeInsets.all(16),
                        itemCount: _matches.length,
                        itemBuilder: (context, index) => _matchCard(_matches[index]),
                      ),
      ),
    );
  }

  Widget _matchCard(Match m) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        borderRadius: BorderRadius.circular(12),
        onTap: () => context.push('/match/${m.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      'Tournament Match',
                      style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                    ),
                  ),
                  _statusBadge(m.status),
                ],
              ),
              if (m.resultNotes != null && m.resultNotes!.isNotEmpty) ...[
                const SizedBox(height: 8),
                Text(m.resultNotes!, style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
              ],
              const SizedBox(height: 8),
              if (m.submittedAt != null)
                Text(
                  'Submitted: ${m.submittedAt!.day}/${m.submittedAt!.month}/${m.submittedAt!.year}',
                  style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
                ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _statusBadge(String status) {
    Color color;
    String label;
    switch (status) {
      case 'submitted':
        color = AppColors.gold;
        label = 'PENDING';
        break;
      case 'verified':
        color = AppColors.success;
        label = 'VERIFIED';
        break;
      case 'rejected':
        color = AppColors.error;
        label = 'REJECTED';
        break;
      default:
        color = AppColors.textMuted;
        label = status.toUpperCase();
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
    );
  }
}
