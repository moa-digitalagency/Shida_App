from datetime import datetime, timedelta
from collections import defaultdict
import threading

class RateLimiter:
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._init_storage()
        return cls._instance
    
    def _init_storage(self):
        self.requests = defaultdict(list)
        self.blocked = {}
        
        self.limits = {
            'login': {'requests': 5, 'window': 300, 'block_duration': 900},
            'register': {'requests': 3, 'window': 3600, 'block_duration': 3600},
            'swipe': {'requests': 100, 'window': 3600, 'block_duration': 600},
            'message': {'requests': 50, 'window': 3600, 'block_duration': 600},
            'report': {'requests': 10, 'window': 3600, 'block_duration': 1800},
            'api': {'requests': 200, 'window': 60, 'block_duration': 300},
            'default': {'requests': 60, 'window': 60, 'block_duration': 300}
        }
    
    def _get_key(self, identifier, action):
        return f"{action}:{identifier}"
    
    def _clean_old_requests(self, key, window):
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window)
        self.requests[key] = [t for t in self.requests[key] if t > cutoff]
    
    def is_blocked(self, identifier, action='default'):
        key = self._get_key(identifier, action)
        
        if key in self.blocked:
            if datetime.utcnow() < self.blocked[key]:
                return True
            else:
                del self.blocked[key]
        
        return False
    
    def check_rate_limit(self, identifier, action='default'):
        if self.is_blocked(identifier, action):
            return False, "Trop de tentatives. Veuillez réessayer plus tard."
        
        limits = self.limits.get(action, self.limits['default'])
        key = self._get_key(identifier, action)
        
        self._clean_old_requests(key, limits['window'])
        
        if len(self.requests[key]) >= limits['requests']:
            self.blocked[key] = datetime.utcnow() + timedelta(seconds=limits['block_duration'])
            return False, f"Limite atteinte. Réessayez dans {limits['block_duration'] // 60} minutes."
        
        self.requests[key].append(datetime.utcnow())
        return True, None
    
    def record_request(self, identifier, action='default'):
        key = self._get_key(identifier, action)
        self.requests[key].append(datetime.utcnow())
    
    def get_remaining(self, identifier, action='default'):
        limits = self.limits.get(action, self.limits['default'])
        key = self._get_key(identifier, action)
        
        self._clean_old_requests(key, limits['window'])
        
        return max(0, limits['requests'] - len(self.requests[key]))
    
    def reset(self, identifier, action=None):
        if action:
            key = self._get_key(identifier, action)
            if key in self.requests:
                del self.requests[key]
            if key in self.blocked:
                del self.blocked[key]
        else:
            keys_to_delete = [k for k in self.requests.keys() if k.endswith(f":{identifier}") or k.startswith(f"{identifier}:")]
            for key in keys_to_delete:
                if key in self.requests:
                    del self.requests[key]
                if key in self.blocked:
                    del self.blocked[key]

rate_limiter = RateLimiter()
