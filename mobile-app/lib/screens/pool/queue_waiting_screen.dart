import 'dart:async';
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/queue_service.dart';

class QueueWaitingScreen extends StatefulWidget {
  final Map<String, dynamic> queueData;

  const QueueWaitingScreen({super.key, required this.queueData});

  @override
  State<QueueWaitingScreen> createState() => _QueueWaitingScreenState();
}

class _QueueWaitingScreenState extends State<QueueWaitingScreen> with SingleTickerProviderStateMixin {
  final _queueService = QueueService();
  late AnimationController _pulseController;
  late Animation<double> _pulseAnimation;
  Timer? _pollTimer;
  Timer? _countdownTimer;
  int _timeRemaining = 120;
  int _position = 1;
  bool _isCancelling = false;

  @override
  void initState() {
    super.initState();
    _pulseController = AnimationController(vsync: this, duration: const Duration(seconds: 2))..repeat(reverse: true);
    _pulseAnimation = Tween<double>(begin: 0.8, end: 1.2).animate(CurvedAnimation(parent: _pulseController, curve: Curves.easeInOut));
    _timeRemaining = widget.queueData['time_remaining_seconds'] as int? ?? 120;
    _startPolling();
  }

  void _startPolling() {
    _pollTimer = Timer.periodic(const Duration(seconds: 3), (_) => _checkStatus());
    _countdownTimer = Timer.periodic(const Duration(seconds: 1), (_) {
      if (!mounted) return;
      setState(() {
        _timeRemaining = (_timeRemaining - 1).clamp(0, 999);
      });
      if (_timeRemaining <= 0) {
        _pollTimer?.cancel();
        _countdownTimer?.cancel();
        context.go('/home');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Queue timed out. Balance refunded.'), backgroundColor: AppColors.secondary),
        );
      }
    });
  }

  Future<void> _checkStatus() async {
    try {
      final status = await _queueService.getQueueStatus();
      if (!mounted) return;

      if (status['in_queue'] == false) {
        _pollTimer?.cancel();
        _countdownTimer?.cancel();
        context.go('/home');
        return;
      }

      if (status['status'] == 'matched' && status['match_id'] != null) {
        _pollTimer?.cancel();
        _countdownTimer?.cancel();
        context.go('/match-found', extra: {
          'match_id': status['match_id'],
          'pool_amount': status['pool_amount'],
        });
        return;
      }

      setState(() {
        _position = status['position'] ?? _position;
        _timeRemaining = status['time_remaining_seconds'] ?? _timeRemaining;
      });
    } catch (e) {
      // keep polling
    }
  }

  Future<void> _cancelQueue() async {
    setState(() => _isCancelling = true);
    try {
      await _queueService.cancelQueue();
      if (!mounted) return;
      _pollTimer?.cancel();
      _countdownTimer?.cancel();
      context.go('/home');
    } catch (e) {
      if (!mounted) return;
      setState(() => _isCancelling = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Failed to cancel: $e'), backgroundColor: AppColors.error),
      );
    }
  }

  @override
  void dispose() {
    _pulseController.dispose();
    _pollTimer?.cancel();
    _countdownTimer?.cancel();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final poolAmount = widget.queueData['pool_amount'] ?? 0;
    final minutes = (_timeRemaining ~/ 60).toString().padLeft(2, '0');
    final seconds = (_timeRemaining % 60).toString().padLeft(2, '0');

    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Finding Match'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: _isCancelling ? null : () => _cancelQueue(),
        ),
      ),
      body: Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              AnimatedBuilder(
                animation: _pulseAnimation,
                builder: (context, child) {
                  return Transform.scale(
                    scale: _pulseAnimation.value,
                    child: child,
                  );
                },
                child: Container(
                  width: 120,
                  height: 120,
                  decoration: BoxDecoration(
                    shape: BoxShape.circle,
                    border: Border.all(color: AppColors.primary, width: 3),
                    boxShadow: [
                      BoxShadow(
                        color: AppColors.primary.withOpacity(0.3),
                        blurRadius: 20,
                        spreadRadius: 5,
                      ),
                    ],
                  ),
                  child: const Center(
                    child: Icon(Icons.sports_esports, size: 48, color: AppColors.primary),
                  ),
                ),
              ),
              const SizedBox(height: 32),
              Text(
                '₹${(poolAmount as num).toInt()} Pool',
                style: const TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
              ),
              const SizedBox(height: 8),
              const Text(
                'Looking for an opponent...',
                style: TextStyle(fontSize: 16, color: AppColors.textSecondary),
              ),
              const SizedBox(height: 32),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: AppColors.border),
                ),
                child: Text(
                  '$minutes:$seconds',
                  style: TextStyle(
                    fontSize: 36,
                    fontWeight: FontWeight.bold,
                    color: _timeRemaining < 30 ? AppColors.error : AppColors.secondary,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
              const SizedBox(height: 16),
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.person, size: 16, color: AppColors.textMuted),
                  const SizedBox(width: 6),
                  Text(
                    'Position: #$_position',
                    style: const TextStyle(color: AppColors.textSecondary),
                  ),
                ],
              ),
              const SizedBox(height: 48),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton(
                  onPressed: _isCancelling ? null : _cancelQueue,
                  style: OutlinedButton.styleFrom(
                    side: const BorderSide(color: AppColors.error),
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  ),
                  child: _isCancelling
                      ? const SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2, color: AppColors.error))
                      : const Text('Cancel', style: TextStyle(color: AppColors.error, fontWeight: FontWeight.bold)),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
