import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/tournament_service.dart';
import 'package:ludo_legends/services/wallet_service.dart';
import 'package:ludo_legends/models/tournament.dart';

class TournamentDetailScreen extends StatefulWidget {
  final String tournamentId;
  const TournamentDetailScreen({super.key, required this.tournamentId});

  @override
  State<TournamentDetailScreen> createState() => _TournamentDetailScreenState();
}

class _TournamentDetailScreenState extends State<TournamentDetailScreen> {
  final _tournamentService = TournamentService();
  final _walletService = WalletService();
  bool _isLoading = true;
  bool _isJoining = false;
  bool _hasError = false;
  Tournament? _tournament;
  double _balance = 0;
  bool _joined = false;
  int _participantCount = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final results = await Future.wait([
        _tournamentService.getTournament(widget.tournamentId),
        _walletService.getBalance(),
        _tournamentService.getParticipants(widget.tournamentId),
      ]);
      if (!mounted) return;
      final participants = results[2] as List;
      setState(() {
        _tournament = results[0] as Tournament;
        _balance = (results[1] as dynamic).balance;
        _participantCount = participants.length;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _isLoading = false; });
    }
  }

  Future<void> _showJoinConfirmation() async {
    if (_tournament == null || _isJoining) return;
    final entryFee = _tournament!.entryFee;

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Join Tournament?', style: TextStyle(color: AppColors.textPrimary)),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Text(_tournament!.name, style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            const SizedBox(height: 12),
            _confirmRow('Entry Fee', '₹${entryFee.toInt()}'),
            _confirmRow('Prize Pool', '₹${_tournament!.prizePool.toInt()}'),
            _confirmRow('Your Balance', '₹${_balance.toInt()}'),
            const SizedBox(height: 12),
            if (_balance < entryFee)
              Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: AppColors.error.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Row(
                  children: [
                    Icon(Icons.warning, color: AppColors.error, size: 16),
                    SizedBox(width: 8),
                    Expanded(
                      child: Text('Insufficient balance. Please deposit first.', style: TextStyle(color: AppColors.error, fontSize: 12)),
                    ),
                  ],
                ),
              ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: _balance < entryFee ? null : () => Navigator.pop(ctx, true),
            child: const Text('Confirm Join'),
          ),
        ],
      ),
    );

    if (confirmed == true) _join();
  }

  Widget _confirmRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: AppColors.textSecondary)),
          Text(value, style: const TextStyle(color: AppColors.textPrimary, fontWeight: FontWeight.w600)),
        ],
      ),
    );
  }

  Future<void> _join() async {
    if (_isJoining || _tournament == null) return;
    setState(() => _isJoining = true);
    try {
      await _tournamentService.joinTournament(widget.tournamentId);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Joined tournament! Entry fee deducted.'), backgroundColor: AppColors.success),
      );
      _load();
    } catch (e) {
      if (!mounted) return;
      final msg = e.toString().contains('Connection')
          ? 'No internet connection.'
          : 'Failed to join. Check balance or try again.';
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(msg), backgroundColor: AppColors.error),
      );
    } finally {
      if (mounted) setState(() => _isJoining = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Tournament')),
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
                        const Icon(Icons.error_outline, size: 48, color: AppColors.error),
                        const SizedBox(height: 16),
                        const Text('Failed to load tournament', style: TextStyle(color: AppColors.textSecondary)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _load, child: const Text('Retry')),
                      ],
                    ),
                  )
                : _tournament == null
                    ? const SizedBox.shrink()
                    : ListView(
                        padding: const EdgeInsets.all(16),
                        children: [
                          Card(
                            child: Padding(
                              padding: const EdgeInsets.all(16),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(
                                    _tournament!.name,
                                    style: const TextStyle(fontSize: 22, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                                  ),
                                  if (_tournament!.description != null) ...[
                                    const SizedBox(height: 4),
                                    Text(_tournament!.description!, style: const TextStyle(color: AppColors.textSecondary, fontSize: 13)),
                                  ],
                                  const SizedBox(height: 16),
                                  _infoRow(Icons.payments, 'Entry Fee', '₹${_tournament!.entryFee.toInt()}'),
                                  _infoRow(Icons.emoji_events, 'Prize Pool', '₹${_tournament!.prizePool.toInt()}'),
                                  _infoRow(Icons.people, 'Players', '$_participantCount/${_tournament!.maxParticipants}'),
                                  _infoRow(Icons.calendar_today, 'Starts', _formatDate(_tournament!.startsAt)),
                                  if (_tournament!.registrationDeadline != null)
                                    _infoRow(Icons.timer, 'Register Before', _formatDate(_tournament!.registrationDeadline!)),
                                  const SizedBox(height: 16),
                                  LinearProgressIndicator(
                                    value: _tournament!.maxParticipants > 0
                                        ? _participantCount / _tournament!.maxParticipants
                                        : 0,
                                    backgroundColor: AppColors.border,
                                    valueColor: AlwaysStoppedAnimation(
                                      _participantCount >= _tournament!.maxParticipants ? AppColors.error : AppColors.primary,
                                    ),
                                  ),
                                  const SizedBox(height: 16),
                                  SizedBox(
                                    width: double.infinity,
                                    child: ElevatedButton(
                                      onPressed: _isJoining || _participantCount >= _tournament!.maxParticipants
                                          ? null
                                          : _showJoinConfirmation,
                                      child: _isJoining
                                          ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                                          : Text(
                                              _participantCount >= _tournament!.maxParticipants
                                                  ? 'Tournament Full'
                                                  : 'Join Tournament — ₹${_tournament!.entryFee.toInt()}',
                                              style: const TextStyle(fontSize: 16),
                                            ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                        ],
                      ),
      ),
    );
  }

  Widget _infoRow(IconData icon, String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: [
          Icon(icon, size: 18, color: AppColors.textMuted),
          const SizedBox(width: 10),
          Text(label, style: const TextStyle(color: AppColors.textSecondary)),
          const Spacer(),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        ],
      ),
    );
  }

  String _formatDate(DateTime dt) => '${dt.day}/${dt.month}/${dt.year}';
}
