import 'package:ludo_legends/services/api_client.dart';
import 'package:ludo_legends/core/config/api_config.dart';
import 'package:ludo_legends/models/tournament.dart';

class TournamentService {
  final ApiClient _api;

  TournamentService({ApiClient? api}) : _api = api ?? ApiClient();

  Future<List<Tournament>> getTournaments({String? status, int page = 1, int perPage = 20}) async {
    final response = await _api.dio.get(ApiConfig.tournaments, queryParameters: {
      if (status != null) 'status_filter': status,
      'page': page,
      'per_page': perPage,
    });

    final data = response.data;
    return (data['tournaments'] as List).map((t) => Tournament.fromJson(t)).toList();
  }

  Future<Tournament> getTournament(String id) async {
    final response = await _api.dio.get('${ApiConfig.tournaments}/$id');
    return Tournament.fromJson(response.data);
  }

  Future<void> joinTournament(String tournamentId) async {
    await _api.dio.post('${ApiConfig.tournaments}/$tournamentId/join');
  }

  Future<List<dynamic>> getParticipants(String tournamentId) async {
    final response = await _api.dio.get('${ApiConfig.tournaments}/$tournamentId/participants');
    return response.data;
  }
}
