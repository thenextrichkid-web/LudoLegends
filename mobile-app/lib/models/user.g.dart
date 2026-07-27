// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'user.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

User _$UserFromJson(Map<String, dynamic> json) => User(
      id: json['id'] as String,
      phone: json['phone'] as String,
      email: json['email'] as String?,
      name: json['name'] as String?,
      avatarUrl: json['avatarUrl'] as String?,
      role: json['role'] as String,
      referralCode: json['referralCode'] as String,
      vipLevel: (json['vipLevel'] as num).toDouble(),
      totalEarnings: (json['totalEarnings'] as num).toDouble(),
      totalMatches: (json['totalMatches'] as num).toDouble(),
      totalWins: (json['totalWins'] as num).toDouble(),
      createdAt: DateTime.parse(json['createdAt'] as String),
    );

Map<String, dynamic> _$UserToJson(User instance) => <String, dynamic>{
      'id': instance.id,
      'phone': instance.phone,
      'email': instance.email,
      'name': instance.name,
      'avatarUrl': instance.avatarUrl,
      'role': instance.role,
      'referralCode': instance.referralCode,
      'vipLevel': instance.vipLevel,
      'totalEarnings': instance.totalEarnings,
      'totalMatches': instance.totalMatches,
      'totalWins': instance.totalWins,
      'createdAt': instance.createdAt.toIso8601String(),
    };
