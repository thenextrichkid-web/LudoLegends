import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/withdrawal_service.dart';
import 'package:ludo_legends/services/wallet_service.dart';

class WithdrawalScreen extends StatefulWidget {
  const WithdrawalScreen({super.key});

  @override
  State<WithdrawalScreen> createState() => _WithdrawalScreenState();
}

class _WithdrawalScreenState extends State<WithdrawalScreen> {
  final _withdrawalService = WithdrawalService();
  final _walletService = WalletService();
  bool _isLoading = true;
  double _balance = 0;
  List<Map<String, dynamic>> _withdrawals = [];

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() => _isLoading = true);
    try {
      final results = await Future.wait([
        _walletService.getBalance(),
        _withdrawalService.getMyWithdrawals(),
      ]);
      if (!mounted) return;
      setState(() {
        _balance = (results[0] as dynamic).balance;
        _withdrawals = results[1] as List<Map<String, dynamic>>;
        _isLoading = false;
      });
    } catch (e) {
      if (!mounted) return;
      setState(() => _isLoading = false);
    }
  }

  void _showRequestDialog() {
    final amountController = TextEditingController();
    final upiController = TextEditingController();
    String paymentMethod = 'upi';

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          backgroundColor: AppColors.surface,
          title: const Text('Request Withdrawal', style: TextStyle(color: AppColors.textPrimary)),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Available: ₹${_balance.toStringAsFixed(0)}', style: const TextStyle(color: AppColors.textSecondary)),
                const SizedBox(height: 16),
                TextField(
                  controller: amountController,
                  keyboardType: TextInputType.number,
                  style: const TextStyle(color: AppColors.textPrimary),
                  decoration: const InputDecoration(hintText: 'Amount (₹)', prefixText: '₹ '),
                ),
                const SizedBox(height: 12),
                const Text('Payment Method', style: TextStyle(color: AppColors.textSecondary, fontSize: 12)),
                const SizedBox(height: 4),
                SegmentedButton<String>(
                  segments: const [
                    ButtonSegment(value: 'upi', label: Text('UPI')),
                    ButtonSegment(value: 'bank', label: Text('Bank')),
                  ],
                  selected: {paymentMethod},
                  onSelectionChanged: (sel) => setDialogState(() => paymentMethod = sel.first),
                  style: ButtonStyle(
                    visualDensity: VisualDensity.compact,
                    textStyle: WidgetStateProperty.all(const TextStyle(fontSize: 12)),
                  ),
                ),
                const SizedBox(height: 12),
                TextField(
                  controller: upiController,
                  style: const TextStyle(color: AppColors.textPrimary),
                  decoration: InputDecoration(
                    hintText: paymentMethod == 'upi' ? 'your@upi' : 'Account number & IFSC',
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Cancel')),
            ElevatedButton(
              onPressed: () async {
                final amount = double.tryParse(amountController.text);
                if (amount == null || amount <= 0) return;
                if (amount > _balance) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Insufficient balance'), backgroundColor: AppColors.error),
                  );
                  return;
                }
                if (amount < 100) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Minimum withdrawal is ₹100'), backgroundColor: AppColors.error),
                  );
                  return;
                }
                if (upiController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Please enter payment details'), backgroundColor: AppColors.error),
                  );
                  return;
                }
                Navigator.pop(ctx);
                try {
                  await _withdrawalService.createWithdrawal(
                    amount: amount,
                    paymentMethod: paymentMethod,
                    paymentDetails: upiController.text,
                  );
                  if (!mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Withdrawal request submitted!'), backgroundColor: AppColors.success),
                  );
                  _load();
                } catch (e) {
                  if (!mounted) return;
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      content: Text(e.toString().contains('Connection') ? 'No internet connection.' : 'Failed to submit request.'),
                      backgroundColor: AppColors.error,
                    ),
                  );
                }
              },
              child: const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Withdrawals'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _showRequestDialog,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: _load,
        color: AppColors.primary,
        child: _isLoading
            ? const Center(child: CircularProgressIndicator(color: AppColors.primary))
            : Column(
                children: [
                  Card(
                    margin: const EdgeInsets.all(16),
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Row(
                        children: [
                          const Icon(Icons.account_balance_wallet, color: AppColors.primary),
                          const SizedBox(width: 12),
                          const Text('Available Balance', style: TextStyle(color: AppColors.textSecondary)),
                          const Spacer(),
                          Text(
                            '₹${_balance.toStringAsFixed(0)}',
                            style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                          ),
                        ],
                      ),
                    ),
                  ),
                  const Padding(
                    padding: EdgeInsets.symmetric(horizontal: 16),
                    child: Align(
                      alignment: Alignment.centerLeft,
                      child: Text('Withdrawal History', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Expanded(
                    child: _withdrawals.isEmpty
                        ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(Icons.receipt_long, size: 48, color: AppColors.textMuted.withOpacity(0.4)),
                                const SizedBox(height: 12),
                                const Text('No withdrawal requests yet', style: TextStyle(color: AppColors.textSecondary)),
                              ],
                            ),
                          )
                        : ListView.builder(
                            padding: const EdgeInsets.symmetric(horizontal: 16),
                            itemCount: _withdrawals.length,
                            itemBuilder: (context, index) => _withdrawalCard(_withdrawals[index]),
                          ),
                  ),
                ],
              ),
      ),
    );
  }

  Widget _withdrawalCard(Map<String, dynamic> w) {
    final status = w['status'] ?? 'pending';
    Color color;
    String label;
    switch (status) {
      case 'pending':
        color = AppColors.gold;
        label = 'Pending';
        break;
      case 'approved':
        color = AppColors.success;
        label = 'Approved';
        break;
      case 'rejected':
        color = AppColors.error;
        label = 'Rejected';
        break;
      case 'processed':
        color = AppColors.primary;
        label = 'Processed';
        break;
      default:
        color = AppColors.textMuted;
        label = status.toUpperCase();
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(
          status == 'approved' || status == 'processed' ? Icons.check_circle : status == 'rejected' ? Icons.cancel : Icons.hourglass_empty,
          color: color,
        ),
        title: Text('₹${(w['amount'] ?? 0).toStringAsFixed(0)}', style: const TextStyle(fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
        subtitle: Text(
          '${w['payment_method'] ?? 'N/A'} · ${w['payment_details'] ?? ''}',
          style: const TextStyle(color: AppColors.textMuted, fontSize: 12),
        ),
        trailing: Container(
          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
          decoration: BoxDecoration(
            color: color.withOpacity(0.15),
            borderRadius: BorderRadius.circular(4),
          ),
          child: Text(label, style: TextStyle(color: color, fontSize: 10, fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}
