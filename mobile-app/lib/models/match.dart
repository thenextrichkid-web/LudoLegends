import 'package:json_annotation/json_annotation.dart';

part 'match.g.dart';

@JsonSerializable()
class Match {
  final String id;
  final String tournamentId;
  final String userId;
  final String status;
  final String? screenshotUrl;
  final String? resultNotes;
  final String? rejectionReason;
  final DateTime? submittedAt;
  final DateTime? verifiedAt;
  final DateTime createdAt;

  const Match({
    required this.id,
    required this.tournamentId,
    required this.userId,
    required this.status,
    this.screenshotUrl,
    this.resultNotes,
    this.rejectionReason,
    this.submittedAt,
    this.verifiedAt,
    required this.createdAt,
  });

  factory Match.fromJson(Map<String, dynamic> json) => _$MatchFromJson(json);
  Map<String, dynamic> toJson() => _$MatchToJson(this);

  bool get isPending => status == 'submitted';
  bool get isVerified => status == 'verified';
  bool get isRejected => status == 'rejected';
}
