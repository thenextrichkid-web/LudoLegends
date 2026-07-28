import 'package:flutter/foundation.dart';

class ApiConfig {
  static String get baseUrl {
    const definedUrl = String.fromEnvironment('API_URL', defaultValue: '');
    if (definedUrl.isNotEmpty) return definedUrl;
    if (kIsWeb) return '';
    return 'http://35.193.127.84:8000';
  }

  static const String apiPrefix = '/api';

  static String get auth => '$apiPrefix/auth';
  static String get tournaments => '$apiPrefix/tournaments';
  static String get wallet => '$apiPrefix/wallet';
  static String get matches => '$apiPrefix/matches';
  static String get referrals => '$apiPrefix/referrals';
  static String get users => '$apiPrefix/users';
  static String get withdrawals => '$apiPrefix/withdrawals';
  static String get admin => '$apiPrefix/admin';
}

class StorageKeys {
  static const String accessToken = 'access_token';
  static const String refreshToken = 'refresh_token';
  static const String userId = 'user_id';
  static const String userRole = 'user_role';
  static const String phoneNumber = 'phone_number';
}

class AppConstants {
  static const String appName = 'Ludo Legends';
  static const int maxOtpLength = 6;
  static const int otpExpiryMinutes = 5;
  static const double minDepositAmount = 10;
  static const double minWithdrawalAmount = 100;
}
