import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:ludo_legends/services/api_client.dart';
import 'package:ludo_legends/core/config/api_config.dart';
import 'package:ludo_legends/models/user.dart';

class AuthService {
  final ApiClient _api;
  final FlutterSecureStorage _storage;

  AuthService({ApiClient? api, FlutterSecureStorage? storage})
      : _api = api ?? ApiClient(),
        _storage = storage ?? const FlutterSecureStorage();

  Future<void> requestOtp(String phone) async {
    await _api.dio.post('${ApiConfig.auth}/otp/request', data: {'phone': phone});
  }

  Future<void> verifyOtp(String phone, String otp, {String? referralCode}) async {
    final response = await _api.dio.post('${ApiConfig.auth}/otp/verify', data: {
      'phone': phone,
      'otp': otp,
      if (referralCode != null) 'referral_code': referralCode,
    });

    final data = response.data;
    await _storage.write(key: StorageKeys.accessToken, value: data['access_token']);
    await _storage.write(key: StorageKeys.refreshToken, value: data['refresh_token']);
    await _storage.write(key: StorageKeys.userId, value: data['user_id']);
    await _storage.write(key: StorageKeys.userRole, value: data['role']);
  }

  Future<User?> getCurrentUser() async {
    try {
      final response = await _api.dio.get('${ApiConfig.auth}/me');
      return User.fromJson(response.data);
    } catch (e) {
      return null;
    }
  }

  Future<void> logout() async {
    await _storage.deleteAll();
  }

  Future<bool> isLoggedIn() async {
    final token = await _storage.read(key: StorageKeys.accessToken);
    return token != null;
  }
}
