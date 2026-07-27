// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'leaderboard.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

LeaderboardEntry _$LeaderboardEntryFromJson(Map<String, dynamic> json) =>
    LeaderboardEntry(
      userId: json['userId'] as String,
      name: json['name'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      wins: (json['wins'] as num).toInt(),
      matchesPlayed: (json['matchesPlayed'] as num).toInt(),
      winRate: (json['winRate'] as num).toDouble(),
      totalEarnings: (json['totalEarnings'] as num).toDouble(),
      rank: (json['rank'] as num).toInt(),
    );

Map<String, dynamic> _$LeaderboardEntryToJson(LeaderboardEntry instance) =>
    <String, dynamic>{
      'userId': instance.userId,
      'name': instance.name,
      'avatarUrl': instance.avatarUrl,
      'wins': instance.wins,
      'matchesPlayed': instance.matchesPlayed,
      'winRate': instance.winRate,
      'totalEarnings': instance.totalEarnings,
      'rank': instance.rank,
    };
