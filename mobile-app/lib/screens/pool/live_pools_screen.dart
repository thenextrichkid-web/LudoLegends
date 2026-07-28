import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/queue_service.dart';
import 'package:ludo_legends/services/wallet_service.dart';

class LivePoolsScreen extends StatefulWidget {
  const LivePoolsScreen({super.key});

  @override
  State<LivePoolsScreen> createState() => _LivePoolsScreenState();
}

class _LivePoolsScreenState extends State<LivePoolsScreen> {
  final _queueService = QueueService();
  final _walletService = WalletService();
  List<Map<String, dynamic>> _pools = [];
  double _balance = 0;
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _isLoading = true; _error = null; });
    try {
      final pools = await _queueService.getPools();
      final wallet = await _walletService.getBalance();
      if (!mounted) return;
      setState(() {
        _pools = pools;
        _balance = wallet.balance;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _error = e.toString().contains('Connection')
            ? 'No internet connection.'
            : 'Failed to load pools.';
        _isLoading = false;
      });
    }
  }

  Future<void> _joinPool(double amount) async {
    if (_balance < amount) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('Insufficient balance. You need ₹${amount.toInt()}.'),
          backgroundColor: AppColors.error,
          action: SnackBarAction(
            label: 'Deposit',
            textColor: Colors.white,
            onPressed: () => context.push('/wallet'),
          ),
        ),
      );
      return;
    }

    try {
      final result = await _queueService.joinQueue(amount);
      if (!mounted) return;

      if (result['matched'] == true) {
        context.go('/match-found', extra: result);
      } else {
        context.go('/queue-waiting', extra: result);
      }
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.toString()), backgroundColor: AppColors.error),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: AppColors.background,
      appBar: AppBar(
        title: const Text('Live Pools'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/home'),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        color: AppColors.primary,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : _error != null
                ? Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const Icon(Icons.wifi_off, size: 48, color: AppColors.textMuted),
                        const SizedBox(height: 16),
                        Text(_error!, textAlign: TextAlign.center, style: const TextStyle(color: AppColors.textSecondary)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _load, child: const Text('Retry')),
                      ],
                    ),
                  )
                : ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      _buildBalanceBanner(),
                      const SizedBox(height: 16),
                      const Text(
                        'Choose a Pool',
                        style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Entry fee is frozen until match completes.',
                        style: TextStyle(color: AppColors.textMuted, fontSize: 12),
                      ),
                      const SizedBox(height: 16),
                      ..._pools.map((pool) => _buildPoolCard(pool)),
                    ],
                  ),
      ),
    );
  }

  Widget _buildBalanceBanner() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.account_balance_wallet, color: AppColors.secondary, size: 24),
            const SizedBox(width: 12),
            Text(
              'Balance: ₹${_balance.toInt()}',
              style: const TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
            ),
            const Spacer(),
            TextButton(
              onPressed: () => context.push('/wallet'),
              child: const Text('Top Up', style: TextStyle(color: AppColors.primary)),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildPoolCard(Map<String, dynamic> pool) {
    final amount = (pool['amount'] as num).toDouble();
    final waiting = pool['players_waiting'] as int;
    final estimatedWait = pool['estimated_wait_seconds'] as int;
    final canAfford = _balance >= amount;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: InkWell(
        onTap: canAfford ? () => _joinPool(amount) : null,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              Container(
                width: 60,
                height: 60,
                decoration: BoxDecoration(
                  color: canAfford ? AppColors.primary.withOpacity(0.15) : AppColors.surfaceLight,
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Center(
                  child: Text(
                    '₹${amount.toInt()}',
                    style: TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                      color: canAfford ? AppColors.primary : AppColors.textMuted,
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '₹${amount.toInt()} Pool',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: canAfford ? AppColors.textPrimary : AppColors.textMuted,
                      ),
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        Icon(Icons.people, size: 14, color: AppColors.textMuted),
                        const SizedBox(width: 4),
                        Text(
                          '$waiting waiting',
                          style: const TextStyle(fontSize: 12, color: AppColors.textMuted),
                        ),
                        const SizedBox(width: 12),
                        Icon(Icons.timer, size: 14, color: AppColors.textMuted),
                        const SizedBox(width: 4),
                        Text(
                          '~${estimatedWait}s',
                          style: const TextStyle(fontSize: 12, color: AppColors.textMuted),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
                decoration: BoxDecoration(
                  color: canAfford ? AppColors.primary : AppColors.surfaceLight,
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  canAfford ? 'JOIN' : '₹${amount.toInt()}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: canAfford ? Colors.white : AppColors.textMuted,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
