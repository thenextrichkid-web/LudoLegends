import 'package:flutter/material.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';

class PracticeModeScreen extends StatelessWidget {
  const PracticeModeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Practice Mode')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Card(
            child: Padding(
              padding: const EdgeInsets.all(24),
              child: Column(
                children: [
                  Icon(Icons.fitness_center, size: 64, color: AppColors.primary.withOpacity(0.6)),
                  const SizedBox(height: 16),
                  const Text(
                    'Practice Mode',
                    style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold, color: AppColors.textPrimary),
                  ),
                  const SizedBox(height: 8),
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                    decoration: BoxDecoration(
                      color: AppColors.success.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: const Text('FREE', style: TextStyle(color: AppColors.success, fontWeight: FontWeight.bold, fontSize: 12)),
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    'Practice your Ludo skills without risking any money. Perfect for learning strategies and improving your game.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: AppColors.textSecondary),
                  ),
                  const SizedBox(height: 24),
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Practice matches coming soon! We\'re building an AI opponent for you to practice against.'),
                            backgroundColor: AppColors.primary,
                            duration: Duration(seconds: 3),
                          ),
                        );
                      },
                      icon: const Icon(Icons.play_arrow),
                      label: const Text('Start Practice Match'),
                    ),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),
          _featureCard(Icons.psychology, 'Learn Strategies', 'Practice different Ludo strategies without risk'),
          _featureCard(Icons.speed, 'Improve Speed', 'Get faster at making decisions during tournaments'),
          _featureCard(Icons.analytics, 'Track Progress', 'See how you improve over time'),
        ],
      ),
    );
  }

  static Widget _featureCard(IconData icon, String title, String desc) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(icon, color: AppColors.primary),
        title: Text(title, style: const TextStyle(color: AppColors.textPrimary)),
        subtitle: Text(desc, style: const TextStyle(color: AppColors.textSecondary, fontSize: 12)),
      ),
    );
  }
}
