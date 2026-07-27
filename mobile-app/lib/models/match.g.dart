// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'match.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Match _$MatchFromJson(Map<String, dynamic> json) => Match(
      id: json['id'] as String,
      tournamentId: json['tournamentId'] as String,
      userId: json['userId'] as String,
      status: json['status'] as String,
      screenshotUrl: json['screenshotUrl'] as String?,
      resultNotes: json['resultNotes'] as String?,
      rejectionReason: json['rejectionReason'] as String?,
      submittedAt: json['submittedAt'] == null
          ? null
          : DateTime.parse(json['submittedAt'] as String),
      verifiedAt: json['verifiedAt'] == null
          ? null
          : DateTime.parse(json['verifiedAt'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$MatchToJson(Match instance) => <String, dynamic>{
      'id': instance.id,
      'tournamentId': instance.tournamentId,
      'userId': instance.userId,
      'status': instance.status,
      'screenshotUrl': instance.screenshotUrl,
      'resultNotes': instance.resultNotes,
      'rejectionReason': instance.rejectionReason,
      'submittedAt': instance.submittedAt?.toIso8601String(),
      'verifiedAt': instance.verifiedAt?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
    };
