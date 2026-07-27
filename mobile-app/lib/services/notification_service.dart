import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:dio/dio.dart';
import 'package:ludo_legends/core/config/api_config.dart';

class NotificationService {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;
  final Dio _dio;

  NotificationService({Dio? dio}) : _dio = dio ?? Dio();

  Future<void> initialize() async {
    final settings = await _messaging.requestPermission(
      alert: true,
      badge: true,
      sound: true,
    );

    if (settings.authorizationStatus == AuthorizationStatus.authorized) {
      final token = await _messaging.getToken();
      if (token != null) {
        await _registerFcmToken(token);
      }

      _messaging.onTokenRefresh.listen((token) {
        _registerFcmToken(token);
      });
    }

    FirebaseMessaging.onMessage.listen(_handleForegroundMessage);
    FirebaseMessaging.onBackgroundMessage(_handleBackgroundMessage);
  }

  Future<void> _registerFcmToken(String token) async {
    try {
      await _dio.post(
        '${ApiConfig.users}/fcm-token',
        data: {'fcm_token': token},
      );
    } catch (e) {
      // Token registration failed silently
    }
  }

  void _handleForegroundMessage(RemoteMessage message) {
    // Handle foreground notification
    // Show in-app notification banner
  }

  static Future<void> _handleBackgroundMessage(RemoteMessage message) async {
    // Handle background notification
  }
}
