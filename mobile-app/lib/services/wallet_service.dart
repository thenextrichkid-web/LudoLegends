import 'package:ludo_legends/services/api_client.dart';
import 'package:ludo_legends/core/config/api_config.dart';
import 'package:ludo_legends/models/wallet.dart';

class WalletService {
  final ApiClient _api;

  WalletService({ApiClient? api}) : _api = api ?? ApiClient();

  Future<Wallet> getBalance() async {
    final response = await _api.dio.get(ApiConfig.wallet);
    return Wallet.fromJson(response.data);
  }

  Future<WalletTransaction> deposit(double amount, String paymentMethod) async {
    final response = await _api.dio.post('${ApiConfig.wallet}/deposit', data: {
      'amount': amount,
      'payment_method': paymentMethod,
    });
    return WalletTransaction.fromJson(response.data);
  }

  Future<WalletTransaction> withdraw(double amount, String paymentMethod, String paymentDetails) async {
    final response = await _api.dio.post('${ApiConfig.wallet}/withdraw', data: {
      'amount': amount,
      'payment_method': paymentMethod,
      'payment_details': paymentDetails,
    });
    return WalletTransaction.fromJson(response.data);
  }

  Future<List<WalletTransaction>> getTransactions({int page = 1, int perPage = 20}) async {
    final response = await _api.dio.get('${ApiConfig.wallet}/transactions', queryParameters: {
      'page': page,
      'per_page': perPage,
    });

    return (response.data as List).map((t) => WalletTransaction.fromJson(t)).toList();
  }
}
