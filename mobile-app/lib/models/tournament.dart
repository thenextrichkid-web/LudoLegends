import 'package:json_annotation/json_annotation.dart';

part 'tournament.g.dart';

@JsonSerializable()
class Tournament {
  final String id;
  final String name;
  final String? description;
  final String type;
  final String status;
  final double entryFee;
  final double prizePool;
  final int maxParticipants;
  final int currentParticipants;
  final DateTime startsAt;
  final DateTime? endsAt;
  final DateTime? registrationDeadline;
  final DateTime createdAt;
  final String? rules;

  const Tournament({
    required this.id,
    required this.name,
    this.description,
    required this.type,
    required this.status,
    required this.entryFee,
    required this.prizePool,
    required this.maxParticipants,
    required this.currentParticipants,
    required this.startsAt,
    this.endsAt,
    this.registrationDeadline,
    required this.createdAt,
    this.rules,
  });

  factory Tournament.fromJson(Map<String, dynamic> json) => _$TournamentFromJson(json);
  Map<String, dynamic> toJson() => _$TournamentToJson(this);

  bool get isJoinable => status == 'upcoming' && currentParticipants < maxParticipants;
  bool get isFull => currentParticipants >= maxParticipants;
  double get fillPercentage => currentParticipants / maxParticipants;
}
