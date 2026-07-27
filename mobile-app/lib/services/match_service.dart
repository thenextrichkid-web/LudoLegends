import 'package:ludo_legends/services/api_client.dart';
import 'package:ludo_legends/core/config/api_config.dart';
import 'package:ludo_legends/models/match.dart';

class MatchService {
  final ApiClient _api;

  MatchService({ApiClient? api}) : _api = api ?? ApiClient();

  Future<Match> submitMatch(String tournamentId, String screenshotUrl, {String? resultNotes}) async {
    final response = await _api.dio.post('${ApiConfig.matches}/submit', data: {
      'tournament_id': tournamentId,
      'screenshot_url': screenshotUrl,
      if (resultNotes != null) 'result_notes': resultNotes,
    });
    return Match.fromJson(response.data);
  }

  Future<List<Match>> getMyMatches({int page = 1, int perPage = 20}) async {
    final response = await _api.dio.get('${ApiConfig.matches}/my', queryParameters: {
      'page': page,
      'per_page': perPage,
    });
    return (response.data as List).map((m) => Match.fromJson(m)).toList();
  }

  Future<List<Match>> getPendingMatches({int page = 1, int perPage = 20}) async {
    final response = await _api.dio.get('${ApiConfig.matches}/pending', queryParameters: {
      'page': page,
      'per_page': perPage,
    });
    return (response.data as List).map((m) => Match.fromJson(m)).toList();
  }

  Future<Match> verifyMatch(String matchId, String action, {String? winnerId, String? score, double? prizeAwarded, String? rejectionReason}) async {
    final response = await _api.dio.post('${ApiConfig.matches}/$matchId/verify', data: {
      'action': action,
      if (winnerId != null) 'winner_id': winnerId,
      if (score != null) 'score': score,
      if (prizeAwarded != null) 'prize_awarded': prizeAwarded,
      if (rejectionReason != null) 'rejection_reason': rejectionReason,
    });
    return Match.fromJson(response.data);
  }
}
