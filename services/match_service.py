from models import db, User, Profile, Like, Match, Message, MatchingConfig, Notification
from datetime import datetime
import json

class MatchService:
    @staticmethod
    def get_active_config():
        config = MatchingConfig.query.filter_by(is_active=True).first()
        if not config:
            return {
                'religion_weight': 0.20,
                'location_weight': 0.15,
                'objective_weight': 0.35,
                'profession_weight': 0.10,
                'age_weight': 0.15,
                'interests_weight': 0.05
            }
        return config.to_dict()
    
    @staticmethod
    def calculate_compatibility(profile1, profile2):
        if not profile1 or not profile2:
            return 0.0
        
        config = MatchService.get_active_config()
        score = 0.0
        
        if profile1.objective and profile2.objective:
            if profile1.objective == profile2.objective:
                score += config['objective_weight'] * 100
            elif MatchService._objectives_compatible(profile1.objective, profile2.objective):
                score += config['objective_weight'] * 50
        
        if profile1.religion and profile2.religion:
            if profile1.religion == profile2.religion:
                score += config['religion_weight'] * 100
        
        if profile1.location and profile2.location:
            if profile1.location == profile2.location:
                score += config['location_weight'] * 100
            elif profile1.tribe and profile2.tribe and profile1.tribe == profile2.tribe:
                score += config['location_weight'] * 50
        
        if profile1.profession and profile2.profession:
            if profile1.profession == profile2.profession:
                score += config['profession_weight'] * 100
        
        if profile1.age and profile2.age:
            age_diff = abs(profile1.age - profile2.age)
            if age_diff <= 2:
                score += config['age_weight'] * 100
            elif age_diff <= 5:
                score += config['age_weight'] * 75
            elif age_diff <= 10:
                score += config['age_weight'] * 50
            elif age_diff <= 15:
                score += config['age_weight'] * 25
        
        if profile1.interests and profile2.interests:
            try:
                interests1 = set(json.loads(profile1.interests)) if isinstance(profile1.interests, str) else set(profile1.interests.split(','))
                interests2 = set(json.loads(profile2.interests)) if isinstance(profile2.interests, str) else set(profile2.interests.split(','))
                if interests1 and interests2:
                    common = len(interests1.intersection(interests2))
                    total = len(interests1.union(interests2))
                    if total > 0:
                        score += config['interests_weight'] * (common / total * 100)
            except:
                pass
        
        return min(round(score, 2), 100.0)
    
    @staticmethod
    def _objectives_compatible(obj1, obj2):
        compatible_groups = [
            {'Mariage', 'Mariage & Sérieux'},
            {'Construction', 'Mariage'},
            {'Amitié', 'Construction'}
        ]
        for group in compatible_groups:
            if obj1 in group and obj2 in group:
                return True
        return False
    
    @staticmethod
    def get_discovery_profiles(user, limit=20):
        liked_user_ids = [l.receiver_id for l in user.sent_likes]
        liked_user_ids.append(user.id)
        
        matched_user_ids = []
        matches = Match.query.filter(
            db.or_(Match.user1_id == user.id, Match.user2_id == user.id)
        ).all()
        for match in matches:
            matched_user_ids.append(match.user1_id)
            matched_user_ids.append(match.user2_id)
        
        excluded_ids = set(liked_user_ids + matched_user_ids)
        
        profiles = Profile.query.join(User).filter(
            ~Profile.user_id.in_(excluded_ids),
            Profile.user_id != user.id,
            User.is_active == True,
            User.is_banned == False,
            Profile.is_approved == True
        )
        
        if not user.is_vip:
            profiles = profiles.filter(User.ghost_mode == False)
        
        profiles = profiles.limit(limit * 2).all()
        
        if user.profile:
            scored_profiles = []
            for profile in profiles:
                score = MatchService.calculate_compatibility(user.profile, profile)
                scored_profiles.append((profile, score))
            
            scored_profiles.sort(key=lambda x: x[1], reverse=True)
            return [p for p, s in scored_profiles[:limit]]
        
        return profiles[:limit]
    
    @staticmethod
    def process_like(sender, receiver_id):
        receiver = User.query.get(receiver_id)
        if not receiver or receiver.is_banned:
            return {'success': False, 'error': 'User not found'}
        
        existing_like = Like.query.filter_by(
            sender_id=sender.id,
            receiver_id=receiver_id
        ).first()
        
        if existing_like:
            return {'success': False, 'error': 'Already liked'}
        
        like = Like(sender_id=sender.id, receiver_id=receiver_id)
        db.session.add(like)
        
        if receiver.profile:
            receiver.profile.views_count += 1
            weekly_views = json.loads(receiver.profile.weekly_views or '[0,0,0,0,0,0,0]')
            day_index = datetime.now().weekday()
            weekly_views[day_index] += 1
            receiver.profile.weekly_views = json.dumps(weekly_views)
        
        mutual_like = Like.query.filter_by(
            sender_id=receiver_id,
            receiver_id=sender.id
        ).first()
        
        if mutual_like:
            like.is_match = True
            mutual_like.is_match = True
            
            compatibility = MatchService.calculate_compatibility(sender.profile, receiver.profile)
            match = Match(
                user1_id=sender.id,
                user2_id=receiver_id,
                compatibility_score=compatibility
            )
            db.session.add(match)
            db.session.commit()
            
            from services.notification_service import NotificationService
            NotificationService.send_match_notification(sender, receiver)
            NotificationService.send_match_notification(receiver, sender)
            
            return {
                'success': True,
                'match': True,
                'match_id': match.id,
                'compatibility_score': compatibility,
                'match_data': match.to_dict()
            }
        
        db.session.commit()
        return {'success': True, 'match': False}
    
    @staticmethod
    def get_user_matches(user):
        matches = Match.query.filter(
            db.or_(Match.user1_id == user.id, Match.user2_id == user.id),
            Match.is_active == True
        ).order_by(Match.created_at.desc()).all()
        
        result = []
        for match in matches:
            other_user = match.user2 if match.user1_id == user.id else match.user1
            last_message = Message.query.filter_by(match_id=match.id).order_by(Message.created_at.desc()).first()
            unread_count = Message.query.filter_by(
                match_id=match.id,
                is_read=False
            ).filter(Message.sender_id != user.id).count()
            
            result.append({
                'id': match.id,
                'other_user': other_user.profile.to_dict() if other_user.profile else None,
                'last_message': last_message.to_dict() if last_message else None,
                'unread_count': unread_count,
                'compatibility_score': match.compatibility_score,
                'created_at': match.created_at.isoformat()
            })
        
        return result
    
    @staticmethod
    def get_likes_received(user):
        if not user.is_vip:
            count = Like.query.filter_by(receiver_id=user.id, is_match=False).count()
            return {'count': count, 'profiles': None}
        
        likes = Like.query.filter_by(receiver_id=user.id, is_match=False).order_by(Like.created_at.desc()).all()
        profiles = []
        for like in likes:
            if like.sender.profile:
                profiles.append({
                    'like_id': like.id,
                    'profile': like.sender.profile.to_dict(),
                    'created_at': like.created_at.isoformat()
                })
        
        return {'count': len(profiles), 'profiles': profiles}
