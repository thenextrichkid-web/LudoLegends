import 'package:ludo_legends/services/api_client.dart';
import 'package:ludo_legends/core/config/api_config.dart';

class QueueService {
  final ApiClient _api;

  QueueService({ApiClient? api}) : _api = api ?? ApiClient();

  Future<List<Map<String, dynamic>>> getPools() async {
    final response = await _api.dio.get('${ApiConfig.queue}/pools');
    return List<Map<String, dynamic>>.from(response.data['pools']);
  }

  Future<Map<String, dynamic>> joinQueue(double poolAmount) async {
    final response = await _api.dio.post('${ApiConfig.queue}/join', data: {
      'pool_amount': poolAmount,
    });
    return response.data;
  }

  Future<Map<String, dynamic>> cancelQueue() async {
    final response = await _api.dio.post('${ApiConfig.queue}/cancel');
    return response.data;
  }

  Future<Map<String, dynamic>> getQueueStatus() async {
    final response = await _api.dio.get('${ApiConfig.queue}/status');
    return response.data;
  }
}
