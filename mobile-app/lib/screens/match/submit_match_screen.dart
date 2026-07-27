import 'package:flutter/material.dart';
import 'package:ludo_legends/core/theme/app_theme.dart';
import 'package:ludo_legends/services/match_service.dart';

class SubmitMatchScreen extends StatefulWidget {
  final String tournamentId;
  const SubmitMatchScreen({super.key, required this.tournamentId});

  @override
  State<SubmitMatchScreen> createState() => _SubmitMatchScreenState();
}

class _SubmitMatchScreenState extends State<SubmitMatchScreen> {
  final _notesController = TextEditingController();
  bool _isSubmitting = false;
  String? _screenshotPath;

  Future<void> _submitMatch() async {
    if (_isSubmitting) return;
    setState(() => _isSubmitting = true);
    try {
      await MatchService().submitMatch(
        widget.tournamentId,
        _screenshotPath ?? 'pending_upload',
        resultNotes: _notesController.text.isNotEmpty ? _notesController.text : null,
      );
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Match submitted for verification!'), backgroundColor: AppColors.success),
        );
        Navigator.pop(context);
      }
    } catch (e) {
      if (mounted) {
        final msg = e.toString().contains('Connection')
            ? 'No internet connection. Please try again.'
            : 'Failed to submit match. Please try again.';
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(msg), backgroundColor: AppColors.error),
        );
      }
    } finally {
      if (mounted) setState(() => _isSubmitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Submit Match Result')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            GestureDetector(
              onTap: () {
                ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(
                    content: Text('Screenshot upload coming soon! For now, you can submit with a note.'),
                    backgroundColor: AppColors.primary,
                  ),
                );
              },
              child: Container(
                height: 200,
                decoration: BoxDecoration(
                  color: AppColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: AppColors.border, style: BorderStyle.solid),
                ),
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.camera_alt, size: 48, color: _screenshotPath != null ? AppColors.success : AppColors.textMuted),
                    const SizedBox(height: 8),
                    Text(
                      _screenshotPath != null ? 'Screenshot selected' : 'Tap to upload screenshot',
                      style: TextStyle(color: _screenshotPath != null ? AppColors.success : AppColors.textMuted),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),
            const Text(
              'Note: Screenshot upload is coming soon. Please include match details in the notes below.',
              style: TextStyle(color: AppColors.textMuted, fontSize: 12, fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 16),
            const Text('Result Notes (Optional)', style: TextStyle(color: AppColors.textSecondary)),
            const SizedBox(height: 8),
            TextField(
              controller: _notesController,
              maxLines: 3,
              style: const TextStyle(color: AppColors.textPrimary),
              decoration: const InputDecoration(hintText: 'e.g., Won 3-1, dice roll 6 on final turn'),
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isSubmitting ? null : _submitMatch,
              child: _isSubmitting
                  ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                  : const Text('Submit Result'),
            ),
          ],
        ),
      ),
    );
  }

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }
}
