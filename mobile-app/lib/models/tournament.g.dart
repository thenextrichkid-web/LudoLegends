// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'tournament.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

Tournament _$TournamentFromJson(Map<String, dynamic> json) => Tournament(
      id: json['id'] as String,
      name: json['name'] as String,
      description: json['description'] as String?,
      type: json['type'] as String,
      status: json['status'] as String,
      entryFee: (json['entryFee'] as num).toDouble(),
      prizePool: (json['prizePool'] as num).toDouble(),
      maxParticipants: (json['maxParticipants'] as num).toInt(),
      currentParticipants: (json['currentParticipants'] as num).toInt(),
      startsAt: DateTime.parse(json['startsAt'] as String),
      endsAt: json['endsAt'] == null
          ? null
          : DateTime.parse(json['endsAt'] as String),
      registrationDeadline: json['registrationDeadline'] == null
          ? null
          : DateTime.parse(json['registrationDeadline'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      rules: json['rules'] as String?,
    );

Map<String, dynamic> _$TournamentToJson(Tournament instance) =>
    <String, dynamic>{
      'id': instance.id,
      'name': instance.name,
      'description': instance.description,
      'type': instance.type,
      'status': instance.status,
      'entryFee': instance.entryFee,
      'prizePool': instance.prizePool,
      'maxParticipants': instance.maxParticipants,
      'currentParticipants': instance.currentParticipants,
      'startsAt': instance.startsAt.toIso8601String(),
      'endsAt': instance.endsAt?.toIso8601String(),
      'registrationDeadline': instance.registrationDeadline?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'rules': instance.rules,
    };
