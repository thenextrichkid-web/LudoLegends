import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:ludo_legends/screens/splash_screen.dart';
import 'package:ludo_legends/screens/auth/otp_screen.dart';
import 'package:ludo_legends/screens/auth/verify_otp_screen.dart';
import 'package:ludo_legends/screens/main_shell.dart';
import 'package:ludo_legends/screens/home/home_screen.dart';
import 'package:ludo_legends/screens/tournament/tournament_list_screen.dart';
import 'package:ludo_legends/screens/tournament/tournament_detail_screen.dart';
import 'package:ludo_legends/screens/wallet/wallet_screen.dart';
import 'package:ludo_legends/screens/profile/profile_screen.dart';
import 'package:ludo_legends/screens/match/submit_match_screen.dart';
import 'package:ludo_legends/screens/leaderboard/leaderboard_screen.dart';
import 'package:ludo_legends/screens/referral/referral_screen.dart';
import 'package:ludo_legends/screens/academy/ludo_academy_screen.dart';
import 'package:ludo_legends/screens/academy/academy_content_screen.dart';
import 'package:ludo_legends/screens/practice/practice_mode_screen.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

final appRouterProvider = Provider<GoRouter>((ref) {
  return GoRouter(
    initialLocation: '/',
    routes: [
      GoRoute(path: '/', builder: (context, state) => const SplashScreen()),
      GoRoute(path: '/otp', builder: (context, state) => const OtpScreen()),
      GoRoute(path: '/verify-otp', builder: (context, state) => VerifyOtpScreen(phone: state.extra as String? ?? '')),
      ShellRoute(
        builder: (context, state, child) => MainShell(child: child),
        routes: [
          GoRoute(path: '/home', builder: (context, state) => const HomeScreen()),
          GoRoute(path: '/tournaments', builder: (context, state) => const TournamentListScreen()),
          GoRoute(path: '/wallet', builder: (context, state) => const WalletScreen()),
          GoRoute(path: '/profile', builder: (context, state) => const ProfileScreen()),
        ],
      ),
      GoRoute(path: '/tournament/:id', builder: (context, state) => TournamentDetailScreen(tournamentId: state.pathParameters['id']!)),
      GoRoute(path: '/submit-match/:tournamentId', builder: (context, state) => SubmitMatchScreen(tournamentId: state.pathParameters['tournamentId']!)),
      GoRoute(path: '/leaderboard', builder: (context, state) => const LeaderboardScreen()),
      GoRoute(path: '/referrals', builder: (context, state) => const ReferralScreen()),
      GoRoute(path: '/academy', builder: (context, state) => const LudoAcademyScreen()),
      GoRoute(path: '/practice', builder: (context, state) => const PracticeModeScreen()),
      GoRoute(
        path: '/academy/rules',
        builder: (context, state) => AcademyContentScreen.rulesData,
      ),
      GoRoute(
        path: '/academy/tips',
        builder: (context, state) => AcademyContentScreen.tipsData,
      ),
      GoRoute(
        path: '/academy/strategies',
        builder: (context, state) => AcademyContentScreen.strategiesData,
      ),
      GoRoute(
        path: '/academy/tournament-guide',
        builder: (context, state) => AcademyContentScreen.tournamentGuideData,
      ),
    ],
  );
});
