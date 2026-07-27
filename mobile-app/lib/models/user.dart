import 'package:json_annotation/json_annotation.dart';

part 'user.g.dart';

@JsonSerializable()
class User {
  final String id;
  final String phone;
  final String? email;
  final String? name;
  final String? avatarUrl;
  final String role;
  final String referralCode;
  final double vipLevel;
  final double totalEarnings;
  final double totalMatches;
  final double totalWins;
  final DateTime createdAt;

  const User({
    required this.id,
    required this.phone,
    this.email,
    this.name,
    this.avatarUrl,
    required this.role,
    required this.referralCode,
    required this.vipLevel,
    required this.totalEarnings,
    required this.totalMatches,
    required this.totalWins,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) => _$UserFromJson(json);
  Map<String, dynamic> toJson() => _$UserToJson(this);
}
