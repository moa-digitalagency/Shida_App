from models import db, User, Profile, Match, Message, Like
from datetime import datetime, timedelta
import json
import os

class GamificationService:
    _config = None
    
    @classmethod
    def get_config(cls):
        if cls._config is None:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'gamification.json')
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    cls._config = json.load(f)
            except:
                cls._config = {
                    'badges': [],
                    'achievements': [],
                    'levels': [],
                    'xp_rewards': {}
                }
        return cls._config
    
    @staticmethod
    def get_user_badges(user):
        badges = []
        config = GamificationService.get_config()
        badge_defs = {b['id']: b for b in config.get('badges', [])}
        
        if user.profile and user.profile.is_verified:
            if 'verified' in badge_defs:
                badges.append(badge_defs['verified'])
        
        if user.is_vip:
            if user.vip_type == 'Gold' and 'vip_gold' in badge_defs:
                badges.append(badge_defs['vip_gold'])
            elif user.vip_type == 'Platinum' and 'vip_platinum' in badge_defs:
                badges.append(badge_defs['vip_platinum'])
        
        if user.profile and user.profile.views_count >= 100:
            if 'popular' in badge_defs:
                badges.append(badge_defs['popular'])
        
        match_count = Match.query.filter(
            db.or_(Match.user1_id == user.id, Match.user2_id == user.id)
        ).count()
        if match_count >= 10:
            if 'match_master' in badge_defs:
                badges.append(badge_defs['match_master'])
        
        if GamificationService.get_profile_completion(user) >= 100:
            if 'profile_complete' in badge_defs:
                badges.append(badge_defs['profile_complete'])
        
        return badges
    
    @staticmethod
    def get_user_xp(user):
        config = GamificationService.get_config()
        xp_rewards = config.get('xp_rewards', {})
        
        xp = 0
        
        if user.profile and user.profile.views_count:
            xp += user.profile.views_count * xp_rewards.get('profile_view', 1)
        
        match_count = Match.query.filter(
            db.or_(Match.user1_id == user.id, Match.user2_id == user.id)
        ).count()
        xp += match_count * xp_rewards.get('match', 25)
        
        message_count = Message.query.filter_by(sender_id=user.id).count()
        xp += message_count * xp_rewards.get('message_sent', 5)
        
        if user.profile and user.profile.is_verified:
            xp += xp_rewards.get('verification', 100)
        
        completion = GamificationService.get_profile_completion(user)
        if completion >= 100:
            xp += xp_rewards.get('profile_complete', 50)
        
        return xp
    
    @staticmethod
    def get_user_level(user):
        config = GamificationService.get_config()
        levels = config.get('levels', [])
        xp = GamificationService.get_user_xp(user)
        
        current_level = levels[0] if levels else {'level': 1, 'name': 'Nouveau', 'min_xp': 0, 'color': '#9E9E9E'}
        
        for level in levels:
            if xp >= level['min_xp']:
                current_level = level
            else:
                break
        
        next_level = None
        for level in levels:
            if level['min_xp'] > xp:
                next_level = level
                break
        
        progress = 0
        if next_level:
            current_min = current_level['min_xp']
            next_min = next_level['min_xp']
            progress = int((xp - current_min) / (next_min - current_min) * 100)
        else:
            progress = 100
        
        return {
            'current': current_level,
            'next': next_level,
            'xp': xp,
            'progress': progress
        }
    
    @staticmethod
    def get_profile_completion(user):
        if not user.profile:
            return 0
        
        profile = user.profile
        fields = {
            'name': profile.name,
            'age': profile.age,
            'bio': profile.bio,
            'photo_url': profile.photo_url,
            'religion': profile.religion,
            'tribe': profile.tribe,
            'profession': profile.profession,
            'objective': profile.objective,
            'location': profile.location,
            'interests': profile.interests
        }
        
        filled = sum(1 for v in fields.values() if v)
        return int(filled / len(fields) * 100)
    
    @staticmethod
    def get_user_achievements(user):
        config = GamificationService.get_config()
        achievements = config.get('achievements', [])
        
        completed = []
        pending = []
        
        for achievement in achievements:
            req = achievement.get('requirement', {})
            req_type = req.get('type')
            
            is_completed = False
            progress = 0
            
            if req_type == 'matches':
                count = Match.query.filter(
                    db.or_(Match.user1_id == user.id, Match.user2_id == user.id)
                ).count()
                target = req.get('count', 1)
                progress = min(count / target * 100, 100)
                is_completed = count >= target
            
            elif req_type == 'messages_sent':
                count = Message.query.filter_by(sender_id=user.id).count()
                target = req.get('count', 1)
                progress = min(count / target * 100, 100)
                is_completed = count >= target
            
            elif req_type == 'profile_completion':
                completion = GamificationService.get_profile_completion(user)
                target = req.get('percentage', 100)
                progress = min(completion / target * 100, 100)
                is_completed = completion >= target
            
            elif req_type == 'verification':
                is_completed = user.profile and user.profile.is_verified
                progress = 100 if is_completed else 0
            
            achievement_data = {
                **achievement,
                'progress': int(progress),
                'is_completed': is_completed
            }
            
            if is_completed:
                completed.append(achievement_data)
            else:
                pending.append(achievement_data)
        
        return {'completed': completed, 'pending': pending}
    
    @staticmethod
    def get_weekly_stats(user):
        if not user.profile:
            return {
                'views': [0] * 7,
                'total_views': 0,
                'change_percent': 0
            }
        
        try:
            weekly_views = json.loads(user.profile.weekly_views or '[0,0,0,0,0,0,0]')
        except:
            weekly_views = [0] * 7
        
        total_views = sum(weekly_views)
        last_week_estimate = sum(weekly_views[:3]) * 2
        
        if last_week_estimate > 0:
            change_percent = int((total_views - last_week_estimate) / last_week_estimate * 100)
        else:
            change_percent = 12
        
        return {
            'views': weekly_views,
            'total_views': user.profile.views_count,
            'change_percent': change_percent
        }
    
    @staticmethod
    def get_dashboard_data(user):
        matches_count = Match.query.filter(
            db.or_(Match.user1_id == user.id, Match.user2_id == user.id)
        ).count()
        
        weekly_stats = GamificationService.get_weekly_stats(user)
        level_data = GamificationService.get_user_level(user)
        badges = GamificationService.get_user_badges(user)
        achievements = GamificationService.get_user_achievements(user)
        
        return {
            'views_total': weekly_stats['total_views'],
            'views_weekly': weekly_stats['views'],
            'views_change_percent': weekly_stats['change_percent'],
            'tokens': user.tokens,
            'negotiations_count': matches_count,
            'is_vip': user.is_vip,
            'vip_type': user.vip_type,
            'level': level_data,
            'badges': badges,
            'achievements_completed': len(achievements['completed']),
            'achievements_total': len(achievements['completed']) + len(achievements['pending']),
            'profile_completion': GamificationService.get_profile_completion(user)
        }
