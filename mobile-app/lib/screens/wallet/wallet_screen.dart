import 'package:flutter/material.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/wallet_service.dart';
import 'package:ludo_legends/models/wallet.dart';

class WalletScreen extends StatefulWidget {
  const WalletScreen({super.key});

  @override
  State<WalletScreen> createState() => _WalletScreenState();
}

class _WalletScreenState extends State<WalletScreen> {
  final _service = WalletService();
  bool _isLoading = true;
  bool _hasError = false;
  double _balance = 0;
  List<WalletTransaction> _transactions = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() { _isLoading = true; _hasError = false; });
    try {
      final results = await Future.wait([
        _service.getBalance(),
        _service.getTransactions(),
      ]);
      if (!mounted) return;
      setState(() {
        _balance = (results[0] as Wallet).balance;
        _transactions = results[1] as List<WalletTransaction>;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() { _hasError = true; _isLoading = false; });
    }
  }

  void _showDepositDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Deposit', style: TextStyle(color: AppColors.textPrimary)),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          style: const TextStyle(color: AppColors.textPrimary),
          decoration: const InputDecoration(hintText: 'Amount (₹)', prefixText: '₹ '),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final amount = double.tryParse(controller.text);
              if (amount == null || amount <= 0) return;
              Navigator.pop(ctx);
              try {
                await _service.deposit(amount, 'upi');
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Deposit successful!'), backgroundColor: AppColors.success),
                );
                _load();
              } catch (e) {
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(e.toString().contains('Connection') ? 'No internet connection.' : 'Deposit failed.'),
                    backgroundColor: AppColors.error,
                  ),
                );
              }
            },
            child: const Text('Deposit'),
          ),
        ],
      ),
    );
  }

  void _showWithdrawDialog() {
    final controller = TextEditingController();
    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        backgroundColor: AppColors.surface,
        title: const Text('Withdraw', style: TextStyle(color: AppColors.textPrimary)),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.number,
          style: const TextStyle(color: AppColors.textPrimary),
          decoration: const InputDecoration(hintText: 'Amount (₹)', prefixText: '₹ '),
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
          ElevatedButton(
            onPressed: () async {
              final amount = double.tryParse(controller.text);
              if (amount == null || amount <= 0) return;
              Navigator.pop(ctx);
              try {
                await _service.withdraw(amount, 'upi', '');
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('Withdrawal requested!'), backgroundColor: AppColors.success),
                );
                _load();
              } catch (e) {
                if (!mounted) return;
                ScaffoldMessenger.of(context).showSnackBar(
                  SnackBar(
                    content: Text(e.toString().contains('Connection') ? 'No internet connection.' : 'Withdrawal failed.'),
                    backgroundColor: AppColors.error,
                  ),
                );
              }
            },
            child: const Text('Withdraw'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Wallet')),
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
                        const Text('Failed to load wallet', style: TextStyle(color: AppColors.textSecondary)),
                        const SizedBox(height: 16),
                        ElevatedButton(onPressed: _load, child: const Text('Retry')),
                      ],
                    ),
                  )
                : ListView(
                    padding: const EdgeInsets.all(16),
                    children: [
                      Card(
                        child: Padding(
                          padding: const EdgeInsets.all(20),
                          child: Column(
                            children: [
                              const Text('Balance', style: TextStyle(color: AppColors.textSecondary)),
                              const SizedBox(height: 4),
                              Text(
                                '₹${_balance.toStringAsFixed(0)}',
                                style: const TextStyle(fontSize: 36, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                              ),
                              const SizedBox(height: 16),
                              Row(
                                children: [
                                  Expanded(
                                    child: ElevatedButton.icon(
                                      onPressed: _showDepositDialog,
                                      icon: const Icon(Icons.add),
                                      label: const Text('Deposit'),
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: OutlinedButton.icon(
                                      onPressed: _balance > 0 ? _showWithdrawDialog : null,
                                      icon: const Icon(Icons.remove),
                                      label: const Text('Withdraw'),
                                    ),
                                  ),
                                ],
                              ),
                            ],
                          ),
                        ),
                      ),
                      const SizedBox(height: 16),
                      const Text('Transactions', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                      const SizedBox(height: 8),
                      if (_transactions.isEmpty)
                        Card(
                          child: Padding(
                            padding: const EdgeInsets.all(32),
                            child: Center(
                              child: Column(
                                children: [
                                  Icon(Icons.receipt_long, size: 48, color: AppColors.textMuted.withOpacity(0.5)),
                                  const SizedBox(height: 12),
                                  const Text('No transactions yet', style: TextStyle(color: AppColors.textSecondary)),
                                  const SizedBox(height: 4),
                                  const Text('Deposit to start playing!', style: TextStyle(color: AppColors.textMuted, fontSize: 12)),
                                ],
                              ),
                            ),
                          ),
                        )
                      else
                        ..._transactions.map((t) => Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            leading: Icon(
                              t.type == 'credit' ? Icons.arrow_downward : Icons.arrow_upward,
                              color: t.type == 'credit' ? AppColors.success : AppColors.error,
                            ),
                            title: Text(t.description ?? t.type.toUpperCase(), style: const TextStyle(color: AppColors.textPrimary)),
                            subtitle: Text('${t.createdAt.day}/${t.createdAt.month}/${t.createdAt.year}', style: const TextStyle(color: AppColors.textMuted, fontSize: 12)),
                            trailing: Text(
                              '${t.type == 'credit' ? '+' : '-'}₹${t.amount.toStringAsFixed(0)}',
                              style: TextStyle(
                                fontWeight: FontWeight.bold,
                                color: t.type == 'credit' ? AppColors.success : AppColors.error,
                              ),
                            ),
                          ),
                        )),
                    ],
                  ),
      ),
    );
  }
}
