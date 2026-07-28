import 'package:flutter/material.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/match_service.dart';
import 'package:ludo_legends/models/match.dart';

class MatchDetailScreen extends StatefulWidget {
  final String matchId;
  const MatchDetailScreen({super.key, required this.matchId});

  @override
  State<MatchDetailScreen> createState() => _MatchDetailScreenState();
}

class _MatchDetailScreenState extends State<MatchDetailScreen> {
  bool _isLoading = true;
  Match? _match;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final matches = await MatchService().getMyMatches();
      _match = matches.where((m) => m.id == widget.matchId).firstOrNull;
      if (!mounted) return;
      setState(() => _isLoading = false);
    } catch (e) {
      if (!mounted) return;
      setState(() { _error = e.toString(); _isLoading = false; });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Match Details')),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
          : _error != null || _match == null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 48, color: AppColors.error),
                      const SizedBox(height: 16),
                      const Text('Match not found', style: TextStyle(color: AppColors.textSecondary)),
                    ],
                  ),
                )
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    Card(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                const Text('Status', style: TextStyle(color: AppColors.textSecondary)),
                                _statusBadge(_match!.status),
                              ],
                            ),
                            const Divider(height: 24),
                            _infoRow('Tournament', _match!.tournamentId.substring(0, 8)),
                            if (_match!.submittedAt != null)
                              _infoRow('Submitted', _formatDate(_match!.submittedAt!)),
                            if (_match!.verifiedAt != null)
                              _infoRow('Verified', _formatDate(_match!.verifiedAt!)),
                            if (_match!.resultNotes != null && _match!.resultNotes!.isNotEmpty) ...[
                              const Divider(height: 24),
                              const Text('Notes', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                              const SizedBox(height: 4),
                              Text(_match!.resultNotes!, style: const TextStyle(color: AppColors.textPrimary)),
                            ],
                            if (_match!.rejectionReason != null && _match!.rejectionReason!.isNotEmpty) ...[
                              const Divider(height: 24),
                              Container(
                                padding: const EdgeInsets.all(12),
                                decoration: BoxDecoration(
                                  color: AppColors.error.withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(8),
                                ),
                                child: Row(
                                  children: [
                                    const Icon(Icons.info_outline, color: AppColors.error, size: 16),
                                    const SizedBox(width: 8),
                                    Expanded(
                                      child: Text(
                                        _match!.rejectionReason!,
                                        style: const TextStyle(color: AppColors.error, fontSize: 13),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),
                  ],
                ),
    );
  }

  Widget _infoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w500)),
        ],
      ),
    );
  }

  Widget _statusBadge(String status) {
    Color color;
    String label;
    switch (status) {
      case 'submitted':
        color = AppColors.gold;
        label = 'Pending Review';
        break;
      case 'verified':
        color = AppColors.success;
        label = 'Verified';
        break;
      case 'rejected':
        color = AppColors.error;
        label = 'Rejected';
        break;
      default:
        color = AppColors.textMuted;
        label = status.toUpperCase();
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
      decoration: BoxDecoration(
        color: color.withOpacity(0.15),
        borderRadius: BorderRadius.circular(6),
      ),
      child: Text(label, style: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.bold)),
    );
  }

  String _formatDate(DateTime dt) => '${dt.day}/${dt.month}/${dt.year} ${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
}
