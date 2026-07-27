import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/services/auth_service.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

class SplashScaffold extends StatelessWidget {
  const SplashScaffold({super.key});

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      backgroundColor: AppColors.background,
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(Icons.games, size: 80, color: AppColors.primary),
            SizedBox(height: 16),
            Text('Ludo Legends', style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold, color: AppColors.textPrimary)),
            SizedBox(height: 24),
            CircularProgressIndicator(color: AppColors.primary),
          ],
        ),
      ),
    );
  }
}

class SplashScreen extends StatefulWidget {
  const SplashScreen({super.key});

  @override
  State<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends State<SplashScreen> {
  @override
  void initState() {
    super.initState();
    _init();
  }

  Future<void> _init() async {
    await Future.delayed(const Duration(milliseconds: 500));
    if (!mounted) return;

    try {
      final authService = AuthService();
      final loggedIn = await authService.isLoggedIn();

      if (!mounted) return;

      if (loggedIn) {
        context.go('/home');
      } else {
        context.go('/otp');
      }
    } catch (e) {
      if (mounted) {
        context.go('/otp');
      }
    }
  }

  @override
  Widget build(BuildContext context) => const SplashScaffold();
}
