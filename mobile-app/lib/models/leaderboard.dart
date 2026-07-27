import 'package:json_annotation/json_annotation.dart';

part 'leaderboard.g.dart';

@JsonSerializable()
class LeaderboardEntry {
  final String userId;
  final String? name;
  final String? avatarUrl;
  final int wins;
  final int matchesPlayed;
  final double winRate;
  final double totalEarnings;
  final int rank;

  const LeaderboardEntry({
    required this.userId,
    this.name,
    this.avatarUrl,
    required this.wins,
    required this.matchesPlayed,
    required this.winRate,
    required this.totalEarnings,
    required this.rank,
  });

  factory LeaderboardEntry.fromJson(Map<String, dynamic> json) => _$LeaderboardEntryFromJson(json);
  Map<String, dynamic> toJson() => _$LeaderboardEntryToJson(this);
}
