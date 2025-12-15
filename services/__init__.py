class MatchService:
    @staticmethod
    def check_compatibility(user1_profile, user2_profile):
        score = 0
        if user1_profile.objective == user2_profile.objective:
            score += 50
        if user1_profile.religion == user2_profile.religion:
            score += 25
        if user1_profile.tribe == user2_profile.tribe:
            score += 15
        if abs(user1_profile.age - user2_profile.age) <= 5:
            score += 10
        return score

class TokenService:
    BASE_TOKENS = 5
    VIP_BONUS = 10
    
    @staticmethod
    def calculate_initial_tokens(is_vip=False):
        return TokenService.BASE_TOKENS + (TokenService.VIP_BONUS if is_vip else 0)
    
    @staticmethod
    def can_use_token(user):
        return user.tokens > 0

class NotificationService:
    @staticmethod
    def send_match_notification(user, matched_user):
        pass
    
    @staticmethod
    def send_message_notification(user, sender, message):
        pass
