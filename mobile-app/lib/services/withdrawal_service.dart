import 'package:ludo_legends/services/api_client.dart';
import 'package:ludo_legends/core/config/api_config.dart';

class WithdrawalService {
  final ApiClient _api;

  WithdrawalService({ApiClient? api}) : _api = api ?? ApiClient();

  Future<Map<String, dynamic>> createWithdrawal({
    required double amount,
    required String paymentMethod,
    required String paymentDetails,
  }) async {
    final response = await _api.dio.post(ApiConfig.withdrawals, data: {
      'amount': amount,
      'payment_method': paymentMethod,
      'payment_details': paymentDetails,
    });
    return response.data;
  }

  Future<List<Map<String, dynamic>>> getMyWithdrawals({int page = 1, int perPage = 20}) async {
    final response = await _api.dio.get(ApiConfig.withdrawals, queryParameters: {
      'page': page,
      'per_page': perPage,
    });
    return (response.data as List).cast<Map<String, dynamic>>();
  }
}
